from core.auto_crawler_iter.strategy_registry import StrategyRegistry

CFG = {
    "strategies_enabled": [
        "extend_selectors", "fallback_data_asins",
        "switch_user_agent", "add_second_pass",
        "adjust_wait_time", "increase_scroll_cycles"
    ],
    "selector_bundles": {
        "base": {
            "list_selectors": ["L1"],
            "title_selectors": ["T1"],
            "price_selectors": ["P1"]
        },
        "extended": {
            "list_selectors": ["L2"],
            "title_selectors": ["T2"],
            "price_selectors": ["P2"]
        }
    },
    "scroll_cycles_base": 3,
    "scroll_cycles_extended": 6,
    "wait_time_base": {"min": 1.0, "max": 1.6},
    "wait_time_extended": {"min": 1.2, "max": 2.4}
}

def test_pick_strategies():
    sr = StrategyRegistry(CFG)
    chosen = sr.pick_strategies(["low_yield", "captcha_blocks"])
    assert "extend_selectors" in chosen
    assert "switch_user_agent" in chosen

def test_materialize_extend():
    sr = StrategyRegistry(CFG)
    patch = sr.materialize(["extend_selectors", "increase_scroll_cycles"])
    assert "L2" in patch["list_selectors"]
    assert patch["scroll_cycles"] == 6

def test_materialize_wait():
    sr = StrategyRegistry(CFG)
    patch = sr.materialize(["adjust_wait_time"])
    assert patch["wait_min"] == 1.2
    assert patch["wait_max"] == 2.4