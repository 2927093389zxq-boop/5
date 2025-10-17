import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List

class MetricsCollector:
    """
    统一指标字段：
    - items_total
    - pages_zero
    - errors_total
    - captcha_hits
    - avg_list_time
    """

    def __init__(self, data_dir: str = "data/amazon", log_file: str = "scraper.log"):
        self.data_dir = data_dir
        self.log_file = log_file

    def collect(self) -> Dict[str, Any]:
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "items_total": 0,
            "pages_zero": 0,
            "errors_total": 0,
            "captcha_hits": 0,
            "avg_list_time": None,
            "files_scanned": 0,
            "avg_items_per_file": 0.0,
            "recent_errors": [],
        }
        counts: List[int] = []

        if os.path.isdir(self.data_dir):
            files = [
                f for f in os.listdir(self.data_dir)
                if f.endswith(".json")
            ]
            files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(self.data_dir, x)), reverse=True)[:30]
            for f in files:
                path = os.path.join(self.data_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    # 支持结构：list 或 {"items": [...]}
                    if isinstance(data, list):
                        cnt = len(data)
                    elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
                        cnt = len(data["items"])
                    else:
                        continue
                    counts.append(cnt)
                    if cnt == 0:
                        metrics["pages_zero"] += 1
                except Exception:
                    continue
            metrics["files_scanned"] = len(counts)
            metrics["items_total"] = sum(counts)
            if counts:
                metrics["avg_items_per_file"] = metrics["items_total"] / len(counts)

        if os.path.exists(self.log_file):
            list_times: List[float] = []
            err_capture: List[str] = []
            with open(self.log_file, "r", encoding="utf-8") as rf:
                for line in rf:
                    low = line.lower()
                    if "captcha" in low:
                        metrics["captcha_hits"] += 1
                    if re.search(r"\[(EXCEPTION|ERROR)\]", line.upper()):
                        metrics["errors_total"] += 1
                        if len(err_capture) < 10:
                            err_capture.append(line.strip())
                    mt = re.search(r"\[LIST_TIME\]\s+secs=([0-9]+(?:\.[0-9]+)?)", line)
                    if mt:
                        try:
                            list_times.append(float(mt.group(1)))
                        except Exception:
                            pass
            if list_times:
                metrics["avg_list_time"] = round(sum(list_times)/len(list_times), 3)
            metrics["recent_errors"] = err_capture
        return metrics