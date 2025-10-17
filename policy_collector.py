import json, os, requests, datetime
from typing import List, Dict

CONFIG_PATH = "config/policy_sources.json"
DEFAULT_SOURCES = [
    {"country": "US", "agency": "U.S. Customs and Border Protection", "endpoint": "https://www.cbp.gov"},
    {"country": "UK", "agency": "Department for International Trade", "endpoint": "https://www.gov.uk"}
]

def load_policy_sources() -> List[Dict]:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return DEFAULT_SOURCES

def fetch_latest_policies(timeout=10, snippet_len=800) -> List[Dict]:
    """
    获取全球政策更新并做来源权威验证
    统一返回结构：
    {
      "source": {...},
      "ok": bool,
      "http_status": int|None,
      "credibility": float,
      "fetched_at": ISO8601,
      "snippet": str,
      "error": str|None
    }
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (PolicyMonitor/1.0; +https://example.com)",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    })

    out = []
    for src in load_policy_sources():
        rec = {
            "source": src,
            "ok": False,
            "http_status": None,
            "credibility": 0.0,
            "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
            "snippet": "",
            "error": None
        }
        try:
            r = session.get(src["endpoint"], timeout=timeout)
            rec["http_status"] = r.status_code
            r.raise_for_status()
            text = r.text
            if not isinstance(text, str):
                text = repr(text)
            rec["snippet"] = text[:snippet_len]
            # 简单可信度模型
            url_lower = src["endpoint"].lower()
            if "gov" in url_lower or url_lower.endswith(".gov"):
                rec["credibility"] = 0.97
            elif "org" in url_lower:
                rec["credibility"] = 0.9
            else:
                rec["credibility"] = 0.8
            rec["ok"] = True
        except Exception as e:
            rec["error"] = str(e)
            rec["credibility"] = 0.4
        out.append(rec)
    return out