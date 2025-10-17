"""
路线图实现测试
Roadmap Implementation Tests
"""
import sys
import os

# 添加项目根目录到路径 / Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_data_fetcher():
    """测试数据获取器 / Test data fetcher"""
    print("测试数据获取器 / Testing data fetcher...")
    
    from core.data_fetcher import get_platform_data, PLATFORM_LIST
    
    assert "Amazon" in PLATFORM_LIST
    assert "Shopee" in PLATFORM_LIST
    assert "eBay" in PLATFORM_LIST
    
    print(f"✅ 支持的平台 / Supported platforms: {PLATFORM_LIST}")
    print("✅ 数据获取器测试通过 / Data fetcher test passed")


def test_ml_ranker():
    """测试ML策略排序器 / Test ML strategy ranker"""
    print("\n测试ML策略排序器 / Testing ML strategy ranker...")
    
    from core.auto_crawler_iter.ml_strategy_ranker import MLStrategyRanker
    
    ranker = MLStrategyRanker()
    
    # 测试策略排序 / Test strategy ranking
    strategies = [
        ['reduce_delay'],
        ['increase_delay'],
        ['change_user_agent']
    ]
    
    metrics = {
        'items_total': 50,
        'pages_zero': 2,
        'errors_total': 1,
        'captcha_hits': 0,
        'avg_list_time': 1.5
    }
    
    ranked = ranker.rank_strategies(strategies, metrics)
    
    print(f"✅ 策略排序结果 / Strategy ranking result: {len(ranked)} strategies ranked")
    print("✅ ML排序器测试通过 / ML ranker test passed")


def test_i18n():
    """测试国际化 / Test i18n"""
    print("\n测试国际化 / Testing i18n...")
    
    from core.i18n import get_i18n, t, set_language
    
    i18n = get_i18n()
    
    # 测试中文 / Test Chinese
    set_language("zh_CN")
    assert t("app_title") == "京盛传媒 企业版智能体"
    print(f"✅ 中文翻译 / Chinese: {t('app_title')}")
    
    # 测试英文 / Test English
    set_language("en_US")
    assert t("app_title") == "Jingsheng Media Enterprise AI Agent"
    print(f"✅ 英文翻译 / English: {t('app_title')}")
    
    print("✅ i18n测试通过 / i18n test passed")


def test_plugin_system():
    """测试插件系统 / Test plugin system"""
    print("\n测试插件系统 / Testing plugin system...")
    
    from core.plugin_system import get_plugin_manager, StrategyPlugin, EvaluatorPlugin
    
    pm = get_plugin_manager()
    
    strategies = pm.list_strategies()
    evaluators = pm.list_evaluators()
    
    print(f"✅ 策略插件数量 / Strategy plugins: {len(strategies)}")
    print(f"✅ 评估器插件数量 / Evaluator plugins: {len(evaluators)}")
    
    if strategies:
        print(f"   策略插件 / Strategies: {strategies}")
    if evaluators:
        print(f"   评估器插件 / Evaluators: {evaluators}")
    
    print("✅ 插件系统测试通过 / Plugin system test passed")


def test_rl_tuner():
    """测试强化学习调优器 / Test RL tuner"""
    print("\n测试强化学习调优器 / Testing RL tuner...")
    
    from core.rl_auto_tuner import RLAutoTuner
    
    param_space = {
        'delay': [0.5, 1.0, 2.0],
        'timeout': [10, 20, 30]
    }
    
    tuner = RLAutoTuner(param_space)
    
    # 测试动作选择 / Test action selection
    state = {
        'items_total': 50,
        'errors_total': 2,
        'avg_list_time': 1.5
    }
    
    action_idx, params = tuner.select_action(state)
    
    print(f"✅ 选择的动作 / Selected action: {action_idx}")
    print(f"✅ 参数组合 / Parameters: {params}")
    
    # 测试奖励计算 / Test reward calculation
    base_metrics = {'items_total': 50, 'errors_total': 2}
    new_metrics = {'items_total': 60, 'errors_total': 1}
    reward = tuner.calculate_reward(base_metrics, new_metrics)
    
    print(f"✅ 计算的奖励 / Calculated reward: {reward}")
    print("✅ RL调优器测试通过 / RL tuner test passed")


def test_integration():
    """集成测试 / Integration test"""
    print("\n集成测试 / Integration test...")
    
    from core.auto_crawler_iter.strategy_registry import StrategyRegistry
    
    cfg = {
        "strategies_enabled": ["reduce_delay", "change_user_agent"],
        "ml_ranking_enabled": False  # 禁用ML以避免依赖历史数据
    }
    
    registry = StrategyRegistry(cfg)
    
    issues = ["captcha_blocks"]
    strategies = registry.pick_strategies(issues)
    
    print(f"✅ 选择的策略 / Selected strategies: {strategies}")
    print("✅ 集成测试通过 / Integration test passed")


def main():
    """运行所有测试 / Run all tests"""
    print("=" * 60)
    print("路线图实现测试套件 / Roadmap Implementation Test Suite")
    print("=" * 60)
    
    try:
        test_data_fetcher()
        test_ml_ranker()
        test_i18n()
        test_plugin_system()
        test_rl_tuner()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！/ All tests passed!")
        print("=" * 60)
        
        print("\n路线图实现完成情况 / Roadmap Implementation Status:")
        print("- ✅ 短期：平台适配器 (Amazon, Shopee, eBay)")
        print("- ✅ 中期：ML策略排序")
        print("- ✅ 中期：i18n国际化")
        print("- ✅ 长期：插件化系统")
        print("- ✅ 长期：强化学习调参")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败 / Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
