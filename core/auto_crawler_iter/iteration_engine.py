import os
import time
import yaml
import json
from typing import Dict, Any
from scrapers.logger import log_info, log_error
from .metrics_collector import MetricsCollector
from .issue_detector import IssueDetector
from .strategy_registry import StrategyRegistry
from .variant_builder import build_variant, variant_hash
from .sandbox_executor import SandboxExecutor
from .evaluator import VariantEvaluator
from .patch_store import PatchStore

HISTORY_PATH = "logs/iter_history.jsonl"

class CrawlerIterationEngine:
    def __init__(self, cfg_path="config/crawler_iter_config.yaml"):
        self.cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
        self.last_run_ts = 0
        self.metrics_collector = MetricsCollector()
        self.issue_detector = IssueDetector()
        self.strategy_registry = StrategyRegistry(self.cfg)
        self.sandbox = SandboxExecutor(self.cfg["sandbox_dir"])
        self.patch_store = PatchStore(self.cfg["patch_output_dir"])
        self.production_file = self.cfg["production_file"]

    def can_run(self) -> bool:
        if not self.cfg.get("enabled", True):
            return False
        now = time.time()
        if now - self.last_run_ts < self.cfg.get("min_interval_minutes", 30) * 60:
            return False
        return True

    def _append_history(self, entry: Dict[str, Any]):
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def run_once(self) -> Dict[str, Any]:
        if not self.can_run():
            return {"status": "skipped", "reason": "interval_or_disabled"}

        self.last_run_ts = time.time()
        start = time.time()
        log_info("[ITER] 开始自迭代运行")

        try:
            metrics = self.metrics_collector.collect()
            issues = self.issue_detector.detect(metrics)
            log_info(f"[ITER] Issues: {issues}")

            strategies = self.strategy_registry.pick_strategies(issues)
            patch_conf = self.strategy_registry.materialize(strategies)

            original_source = open(self.production_file, "r", encoding="utf-8").read()
            variant_source = build_variant(patch_conf, original_source, strategies)

            if variant_source.strip() == original_source.strip():
                log_info("[ITER] 变体与原始无差异，跳过")
                result = {
                    "status": "no_change",
                    "issues": issues,
                    "strategies": strategies,
                    "metrics": metrics
                }
                self._append_history(result)
                return result

            tag = variant_hash(variant_source)
            variant_path = self.sandbox.write_variant(variant_source, tag)
            prod_mod = self.sandbox._dynamic_import(self.production_file)
            var_mod = self.sandbox._dynamic_import(variant_path)

            base_stats = self.sandbox.run_test(prod_mod, self.cfg["test_urls"])
            new_stats = self.sandbox.run_test(var_mod, self.cfg["test_urls"])

            evaluator = VariantEvaluator(
                weights=self.cfg["weights"],
                threshold=self.cfg["score_threshold"],
                require_error_drop=self.cfg["require_error_drop"]
            )
            eval_result = evaluator.score(base_stats, new_stats)
            log_info(f"[ITER] Eval result: {eval_result}")

            if eval_result["passed"]:
                meta = {
                    "strategies": strategies,
                    "score": eval_result["raw_score"],
                    "component_scores": eval_result["component_scores"],
                    "delta": eval_result["delta"]
                }
                patch_path = self.patch_store.build_patch(
                    original_source, variant_source, tag, meta
                )
                result = {
                    "status": "candidate",
                    "tag": tag,
                    "patch_path": patch_path,
                    "strategies": strategies,
                    "metrics_before": base_stats,
                    "metrics_after": new_stats,
                    "evaluation": eval_result
                }
            else:
                result = {
                    "status": "rejected",
                    "reason": "score_not_improved",
                    "strategies": strategies,
                    "metrics_before": base_stats,
                    "metrics_after": new_stats,
                    "evaluation": eval_result
                }
            self._append_history(result)
            return result

        except Exception as e:
            log_error(f"[ITER] 异常: {repr(e)}")
            result = {"status": "error", "error": repr(e)}
            self._append_history(result)
            return result
        finally:
            elapsed = round(time.time() - start, 2)
            log_info(f"[ITER] 结束 elapsed={elapsed}s")

    def apply_patch(self, tag: str) -> Dict[str, Any]:
        patch_file = os.path.join(self.cfg["patch_output_dir"], f"{tag}.patch")
        variant_file = os.path.join(self.cfg["sandbox_dir"], f"amazon_scraper_{tag}.py")
        if not (os.path.exists(patch_file) and os.path.exists(variant_file)):
            return {"status": "error", "reason": "patch_or_variant_missing"}
        variant_code = open(variant_file, "r", encoding="utf-8").read()
        backup = self.patch_store.apply_patch_direct(patch_file, self.production_file, variant_code)
        apply_entry = {"status": "applied", "tag": tag, "backup": backup}
        self._append_history(apply_entry)
        log_info(f"[ITER] 补丁已应用 tag={tag} backup={backup}")
        return apply_entry