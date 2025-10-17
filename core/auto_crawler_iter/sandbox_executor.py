import os
import importlib.util
import time
from typing import Dict, List
from scrapers.logger import log_info, log_error

class SandboxExecutor:
    def __init__(self, sandbox_dir="sandbox"):
        self.sandbox_dir = sandbox_dir
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def write_variant(self, variant_code: str, tag: str) -> str:
        path = os.path.join(self.sandbox_dir, f"amazon_scraper_{tag}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(variant_code)
        return path

    def _dynamic_import(self, path: str):
        spec = importlib.util.spec_from_file_location("amazon_variant", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_test(self, scraper_module, test_urls: List[str], max_items=20) -> Dict:
        stats = {
            "items_total": 0,
            "pages_zero": 0,
            "errors_total": 0,
            "captcha_hits": 0,
            "avg_list_time": None  # 用于统一字段，测试阶段按 avg_time
        }
        times: List[float] = []
        for u in test_urls:
            start = time.time()
            try:
                data = scraper_module.scrape_amazon(
                    url=u,
                    max_items=max_items,
                    resume=False,
                    use_proxy=False,
                    deep_detail=False,
                    storage_mode="local",
                    headless=True,
                    second_pass=True
                )
                if not data:
                    stats["pages_zero"] += 1
                else:
                    stats["items_total"] += len(data)
                    # 简单 captcha 标记：如果 detail 中出现特定字段（可拓展）
                    # 占位：真实方案应通过日志或返回结构判断
            except Exception as e:
                stats["errors_total"] += 1
                log_error(f"[SANDBOX] 测试错误: {e}")
            elapsed = time.time() - start
            times.append(elapsed)
        if times:
            stats["avg_list_time"] = round(sum(times)/len(times), 3)
        return stats

    def cleanup(self):
        pass  # 可实现变体过期清理