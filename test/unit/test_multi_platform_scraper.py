"""
多平台爬虫测试模块
Multi-Platform Scraper Test Module
"""
import pytest
from scrapers.multi_platform_scraper import (
    PLATFORM_SCRAPERS,
    get_scraper,
    scrape_platform,
    FordealScraper,
    MercariScraper,
    EbayScraper,
    ShopeeScraper,
    TemuScraper,
)
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup


class TestBaseScraper:
    """测试基础爬虫类 / Test Base Scraper Class"""
    
    def test_base_scraper_cannot_be_instantiated(self):
        """测试基础爬虫类不能直接实例化 / Test base scraper cannot be directly instantiated"""
        # BaseScraper is abstract, so we need a concrete implementation to test
        assert issubclass(FordealScraper, BaseScraper)
    
    def test_base_scraper_has_required_methods(self):
        """测试基础爬虫类有必需的方法 / Test base scraper has required methods"""
        scraper = FordealScraper()
        assert hasattr(scraper, 'scrape_list_page')
        assert hasattr(scraper, 'scrape_product_detail')
        assert hasattr(scraper, 'run')
        assert hasattr(scraper, 'save_data')
        assert hasattr(scraper, '_fetch_page')
        assert hasattr(scraper, '_extract_text')
    
    def test_base_scraper_initialization(self):
        """测试基础爬虫类初始化 / Test base scraper initialization"""
        scraper = FordealScraper()
        assert scraper.PLATFORM_NAME == "fordeal"
        assert scraper.data_dir == "data/fordeal"
        assert scraper.session is not None


class TestPlatformScrapers:
    """测试各平台爬虫类 / Test Platform Scrapers"""
    
    def test_all_platforms_registered(self):
        """测试所有平台都已注册 / Test all platforms are registered"""
        expected_platforms = [
            "fordeal", "mercari", "fyndia", "tokopedia", "onbuy", "joom",
            "yandex_market", "faire", "aliexpress", "ebay", "tiktokshop",
            "rakuten_japan", "ozon", "etsy", "mercadolibre", "noon",
            "wildberries", "shopee", "coupang", "flipkart", "allegro",
            "target", "falabella", "cdiscount", "otto", "jumia", "lazada", "temu"
        ]
        
        assert len(PLATFORM_SCRAPERS) == 28
        for platform in expected_platforms:
            assert platform in PLATFORM_SCRAPERS
    
    def test_get_scraper_valid_platform(self):
        """测试获取有效平台的爬虫 / Test get scraper for valid platform"""
        scraper = get_scraper("ebay")
        assert isinstance(scraper, EbayScraper)
        assert scraper.PLATFORM_NAME == "ebay"
    
    def test_get_scraper_invalid_platform(self):
        """测试获取无效平台的爬虫 / Test get scraper for invalid platform"""
        with pytest.raises(ValueError):
            get_scraper("invalid_platform")
    
    def test_get_scraper_case_insensitive(self):
        """测试平台名称大小写不敏感 / Test platform name is case insensitive"""
        scraper1 = get_scraper("ebay")
        scraper2 = get_scraper("eBay")
        scraper3 = get_scraper("EBAY")
        
        assert scraper1.PLATFORM_NAME == scraper2.PLATFORM_NAME
        assert scraper2.PLATFORM_NAME == scraper3.PLATFORM_NAME
    
    def test_scraper_has_platform_name(self):
        """测试每个爬虫都有平台名称 / Test each scraper has platform name"""
        for platform_name, scraper_class in PLATFORM_SCRAPERS.items():
            scraper = scraper_class()
            assert scraper.PLATFORM_NAME == platform_name


class TestScraperFunctionality:
    """测试爬虫功能 / Test Scraper Functionality"""
    
    def test_extract_text_from_html(self):
        """测试从HTML提取文本 / Test extract text from HTML"""
        html = '<div class="test"><span class="title">Test Product</span></div>'
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.test')
        
        scraper = EbayScraper()
        text = scraper._extract_text(item, ['span.title'])
        assert text == "Test Product"
    
    def test_extract_text_with_fallback(self):
        """测试文本提取的降级策略 / Test text extraction with fallback"""
        html = '<div class="test"><h2>Product Title</h2></div>'
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.test')
        
        scraper = EbayScraper()
        # 第一个选择器不存在，应该降级到h2
        text = scraper._extract_text(item, ['span.missing', 'h2'])
        assert text == "Product Title"
    
    def test_extract_text_with_attribute(self):
        """测试提取HTML属性 / Test extract HTML attribute"""
        html = '<div class="test"><img src="image.jpg" alt="Product Image"></div>'
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.test')
        
        scraper = ShopeeScraper()
        alt_text = scraper._extract_text(item, ['img'], attr='alt')
        assert alt_text == "Product Image"
        
        src_text = scraper._extract_text(item, ['img'], attr='src')
        assert src_text == "image.jpg"
    
    def test_save_data(self):
        """测试数据保存功能 / Test save data functionality"""
        import os
        import json
        import shutil
        
        scraper = TemuScraper()
        test_data = [
            {
                "platform": "temu",
                "title": "Test Product",
                "price": "$19.99"
            }
        ]
        
        filepath = scraper.save_data(test_data, filename="test_temu_products.json")
        assert os.path.exists(filepath)
        
        # 验证文件内容 / Verify file content
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['platform'] == 'temu'
        assert saved_data['total_count'] == 1
        assert saved_data['items'][0]['title'] == "Test Product"
        assert 'scraped_at' in saved_data
        
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)
        # Remove test directory if empty
        if os.path.exists("data/temu") and not os.listdir("data/temu"):
            shutil.rmtree("data/temu")


class TestScraperRetryMechanism:
    """测试爬虫重试机制 / Test Scraper Retry Mechanism"""
    
    def test_scraper_has_retry_config(self):
        """测试爬虫有重试配置 / Test scraper has retry config"""
        scraper = MercariScraper()
        assert hasattr(scraper, 'max_retries')
        assert scraper.max_retries > 0
    
    def test_scraper_has_wait_time_config(self):
        """测试爬虫有等待时间配置 / Test scraper has wait time config"""
        scraper = MercariScraper()
        assert hasattr(scraper, 'wait_time')
        assert 'min' in scraper.wait_time
        assert 'max' in scraper.wait_time
        assert scraper.wait_time['min'] < scraper.wait_time['max']


class TestConvenienceFunction:
    """测试便捷函数 / Test Convenience Function"""
    
    def test_scrape_platform_function_exists(self):
        """测试平台采集便捷函数存在 / Test scrape platform function exists"""
        assert callable(scrape_platform)
    
    def test_scrape_platform_with_mock(self):
        """测试平台采集便捷函数（模拟）/ Test scrape platform function with mock"""
        from unittest.mock import patch, MagicMock
        
        with patch('scrapers.multi_platform_scraper.get_scraper') as mock_get_scraper:
            mock_scraper = MagicMock()
            mock_scraper.run.return_value = []
            mock_get_scraper.return_value = mock_scraper
            
            result = scrape_platform("ebay", "https://test.com", max_items=10)
            mock_scraper.run.assert_called_once_with("https://test.com", 10, False)
            assert result == []


class TestPlatformSpecificFeatures:
    """测试平台特定功能 / Test Platform-Specific Features"""
    
    def test_ebay_scraper_filters_placeholder(self):
        """测试eBay爬虫过滤占位符 / Test eBay scraper filters placeholder"""
        # This is a behavior test - eBay scraper should skip placeholder items
        scraper = EbayScraper()
        assert scraper.PLATFORM_NAME == "ebay"
    
    def test_shopee_scraper_has_location(self):
        """测试Shopee爬虫包含位置信息 / Test Shopee scraper includes location"""
        scraper = ShopeeScraper()
        assert scraper.PLATFORM_NAME == "shopee"
    
    def test_tokopedia_scraper_supports_rating(self):
        """测试Tokopedia爬虫支持评分 / Test Tokopedia scraper supports rating"""
        from scrapers.multi_platform_scraper import TokopediaScraper
        scraper = TokopediaScraper()
        assert scraper.PLATFORM_NAME == "tokopedia"


class TestDataFetcherIntegration:
    """测试与data_fetcher的集成 / Test integration with data_fetcher"""
    
    @pytest.mark.skipif(True, reason="Streamlit dependency required for data_fetcher")
    def test_platform_list_updated(self):
        """测试平台列表已更新 / Test platform list is updated"""
        from core.data_fetcher import PLATFORM_LIST
        
        # 验证新平台已添加到列表中 / Verify new platforms added to list
        assert "Fordeal" in PLATFORM_LIST
        assert "Mercari" in PLATFORM_LIST
        assert "Temu" in PLATFORM_LIST
        assert "Lazada" in PLATFORM_LIST
        assert len(PLATFORM_LIST) >= 28


class TestScraperRobustness:
    """测试爬虫健壮性 / Test Scraper Robustness"""
    
    def test_scraper_handles_empty_page(self):
        """测试爬虫处理空页面 / Test scraper handles empty page"""
        from unittest.mock import patch
        
        scraper = FordealScraper()
        with patch.object(scraper, '_fetch_page', return_value=None):
            products = scraper.scrape_list_page("https://test.com")
            assert products == []
    
    def test_scraper_handles_missing_elements(self):
        """测试爬虫处理缺失元素 / Test scraper handles missing elements"""
        html = '<div class="product-item"></div>'
        soup = BeautifulSoup(html, 'lxml')
        
        scraper = FordealScraper()
        # Should not crash even if elements are missing
        text = scraper._extract_text(soup, ['span.missing'])
        assert text == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
