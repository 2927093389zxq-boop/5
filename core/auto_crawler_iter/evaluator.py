from typing import Dict

class VariantEvaluator:
    """
    使用标准化指标对比：
    - items_total（提高为正）
    - pages_zero（减少为正 -> 负权重）
    - errors_total（减少为正 -> 负权重）
    - avg_list_time（减少为正 -> 负权重）
    - captcha_hits（减少为正 -> 负权重）
    返回 component_scores + delta + raw_score + passed
    """

    def __init__(self, weights: Dict, threshold: float, require_error_drop: bool):
        self.weights = weights
        self.threshold = threshold
        self.require_error_drop = require_error_drop

    def score(self, base: Dict, new: Dict) -> Dict:
        deltas = {
            "items_total": new.get("items_total", 0) - base.get("items_total", 0),
            "pages_zero": new.get("pages_zero", 0) - base.get("pages_zero", 0),
            "errors_total": new.get("errors_total", 0) - base.get("errors_total", 0),
            "avg_list_time": (new.get("avg_list_time") or 0) - (base.get("avg_list_time") or 0),
            "captcha_hits": new.get("captcha_hits", 0) - base.get("captcha_hits", 0)
        }
        component_scores = {
            k: round(self.weights.get(k, 0) * v, 4)
            for k, v in deltas.items()
        }
        raw_score = round(sum(component_scores.values()), 4)
        passed = raw_score >= self.threshold
        # 如果要求错误下降，且 errors_total 增加（delta > 0）则判失败
        if self.require_error_drop and deltas["errors_total"] > 0:
            passed = False
        return {
            "delta": deltas,
            "component_scores": component_scores,
            "raw_score": raw_score,
            "passed": passed
        }