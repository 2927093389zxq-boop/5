import re
import json
import hashlib
import os
from typing import Dict, List

TEMPLATE_HEADER = """# AUTO-GENERATED VARIANT
# strategies: {strategies}
# Do not edit manually; apply via patch system.
"""

CONFIG_START = "# === AUTO_TUNING_CONFIG_START ==="
CONFIG_END = "# === AUTO_TUNING_CONFIG_END ==="
REPLACEMENT_HINT = "# (auto-tuning patch applied)"

RE_BLOCK = re.compile(rf"{CONFIG_START}\s*(?:\r?\n)?(.*?){CONFIG_END}", re.DOTALL)

REQUIRED_KEYS = [
    "list_selectors", "title_selectors", "price_selectors",
    "ua_mode", "scroll_cycles", "wait_min", "wait_max",
    "enable_second_pass", "enable_fallback_asin"
]

def _ser(v):
    if isinstance(v, (list, dict, tuple)):
        if isinstance(v, tuple):
            v = list(v)
        return json.dumps(v, ensure_ascii=False)
    return repr(v)

def validate_conf(patch_conf: Dict):
    missing = [k for k in REQUIRED_KEYS if k not in patch_conf]
    if missing:
        raise ValueError(f"patch_conf 缺少字段: {missing}")
    for key in ["list_selectors", "title_selectors", "price_selectors"]:
        if not isinstance(patch_conf[key], (list, tuple)):
            raise TypeError(f"{key} 必须是列表或元组")

def build_config_block(patch_conf: Dict) -> str:
    validate_conf(patch_conf)
    lines = [
        CONFIG_START,
        f"LIST_SELECTORS = {_ser(patch_conf['list_selectors'])}",
        f"TITLE_SELECTORS = {_ser(patch_conf['title_selectors'])}",
        f"PRICE_SELECTORS = {_ser(patch_conf['price_selectors'])}",
        "",
        f"UA_MODE = {_ser(patch_conf['ua_mode'])}",
        f"SCROLL_CYCLES = {_ser(patch_conf['scroll_cycles'])}",
        f"WAIT_MIN = {_ser(patch_conf['wait_min'])}",
        f"WAIT_MAX = {_ser(patch_conf['wait_max'])}",
        f"ENABLE_SECOND_PASS = {_ser(patch_conf['enable_second_pass'])}",
        f"ENABLE_FALLBACK_ASIN = {_ser(patch_conf['enable_fallback_asin'])}",
        CONFIG_END,
        REPLACEMENT_HINT
    ]
    return "\n".join(lines) + "\n"

def build_variant(patch_conf: Dict, base_source: str, strategies: List[str]) -> str:
    block = build_config_block(patch_conf)
    if CONFIG_START in base_source:
        def _replace(_m):
            return block
        return RE_BLOCK.sub(_replace, base_source, count=1)
    else:
        return TEMPLATE_HEADER.format(strategies=",".join(strategies)) + block + base_source

def variant_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

def write_variant_file(path: str, content: str):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    os.replace(tmp, path)