from core.auto_crawler_iter.variant_builder import build_variant, variant_hash

def test_variant_insertion():
    base = "print('Hello')"
    patch_conf = {
        "list_selectors": ["a", "b"],
        "title_selectors": ["t1"],
        "price_selectors": ["p1"],
        "ua_mode": "desktop",
        "scroll_cycles": 3,
        "wait_min": 1.0,
        "wait_max": 1.6,
        "enable_second_pass": True,
        "enable_fallback_asin": False
    }
    out = build_variant(patch_conf, base, ["extend_selectors"])
    assert "# === AUTO_TUNING_CONFIG_START ===" in out
    assert "LIST_SELECTORS" in out

def test_hash_stable():
    h1 = variant_hash("abc")
    h2 = variant_hash("abc")
    assert h1 == h2
    assert len(h1) == 16