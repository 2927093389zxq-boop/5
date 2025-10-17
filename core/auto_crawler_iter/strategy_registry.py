import random
from typing import Dict, List

ISSUE_STRATEGY_MAP = {
    "low_yield": "extend_selectors",
    "too_many_zeros": "fallback_data_asins",
    "captcha_blocks": "switch_user_agent",
    "frequent_errors": "add_second_pass"
}

class StrategyRegistry:
    def __init__(self, cfg: Dict):
        self.cfg = cfg

    def pick_strategies(self, issues: List[str]) -> List[str]:
        enabled = set(self.cfg.get("strategies_enabled", []))
        chosen: List[str] = []
        for issue in issues:
            strat = ISSUE_STRATEGY_MAP.get(issue)
            if strat and strat in enabled and strat not in chosen:
                chosen.append(strat)
        if not chosen and enabled:
            chosen.append(random.choice(list(enabled)))
        return chosen

    def materialize(self, strategy_list: List[str]) -> Dict:
        patch_conf: Dict = {}
        base = self.cfg.get("selector_bundles", {}).get("base", {})
        extended = self.cfg.get("selector_bundles", {}).get("extended", {})

        patch_conf["list_selectors"] = list(base.get("list_selectors", []))
        patch_conf["title_selectors"] = list(base.get("title_selectors", []))
        patch_conf["price_selectors"] = list(base.get("price_selectors", []))

        if "extend_selectors" in strategy_list:
            patch_conf["list_selectors"] += extended.get("list_selectors", [])
            patch_conf["title_selectors"] += extended.get("title_selectors", [])
            patch_conf["price_selectors"] += extended.get("price_selectors", [])

        # UA mode
        ua_mode = "hybrid" if "switch_user_agent" in strategy_list else "desktop"
        patch_conf["ua_mode"] = ua_mode

        # scroll cycles
        cycles = self.cfg.get("scroll_cycles_base", 3)
        if "increase_scroll_cycles" in strategy_list or "extend_selectors" in strategy_list:
            cycles = max(cycles, self.cfg.get("scroll_cycles_extended", cycles))
        patch_conf["scroll_cycles"] = cycles

        # wait times
        if "adjust_wait_time" in strategy_list or "extend_selectors" in strategy_list:
            wt = self.cfg.get("wait_time_extended", {})
        else:
            wt = self.cfg.get("wait_time_base", {})
        patch_conf["wait_min"] = wt.get("min", 1.0)
        patch_conf["wait_max"] = wt.get("max", 1.6)

        patch_conf["enable_second_pass"] = ("add_second_pass" in strategy_list)
        patch_conf["enable_fallback_asin"] = ("fallback_data_asins" in strategy_list)

        return patch_conf