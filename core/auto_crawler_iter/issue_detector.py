import os
import yaml
from typing import Dict, List

DEFAULT_THRESHOLDS = {
    "low_yield_files_scanned_min": 5,
    "low_yield_avg_items_max": 3,
    "too_many_zeros_pages_zero_min": 2,
    "captcha_hits_min": 0,
    "errors_total_min": 5
}

class IssueDetector:
    """
    从标准化指标判定问题列表
    """

    def __init__(self, threshold_path: str = "config/auto_iter_thresholds.yaml"):
        if os.path.exists(threshold_path):
            self.thresholds = yaml.safe_load(open(threshold_path, "r", encoding="utf-8")) or {}
        else:
            self.thresholds = {}
        for k, v in DEFAULT_THRESHOLDS.items():
            self.thresholds.setdefault(k, v)

    def detect(self, m: Dict) -> List[str]:
        issues = []
        if m.get("files_scanned", 0) >= self.thresholds["low_yield_files_scanned_min"] and \
           m.get("avg_items_per_file", 0) < self.thresholds["low_yield_avg_items_max"]:
            issues.append("low_yield")
        if m.get("pages_zero", 0) > self.thresholds["too_many_zeros_pages_zero_min"]:
            issues.append("too_many_zeros")
        if m.get("captcha_hits", 0) > self.thresholds["captcha_hits_min"]:
            issues.append("captcha_blocks")
        if m.get("errors_total", 0) > self.thresholds["errors_total_min"]:
            issues.append("frequent_errors")
        return issues