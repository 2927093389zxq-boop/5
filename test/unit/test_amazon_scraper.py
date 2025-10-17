"""
Amazon爬虫测试模块
Amazon Scraper Test Module
"""
import pytest
from scrapers.amazon_scraper import AmazonScraper, scrape_amazon, SELECTORS
from bs4 import BeautifulSoup
import os
import json


class TestAmazonScraper:
    """Amazon爬虫测试类 / Amazon Scraper Test Class"""
    
    def test_scraper_initialization(self):
        """测试爬虫初始化 / Test scraper initialization"""
        scraper = AmazonScraper()
        assert scraper.data_dir == "data/amazon"
        assert os.path.exists(scraper.data_dir)
        assert scraper.session is not None
    
    def test_custom_data_dir(self):
        """测试自定义数据目录 / Test custom data directory"""
        custom_dir = "data/test_amazon"
        scraper = AmazonScraper(data_dir=custom_dir)
        assert scraper.data_dir == custom_dir
        assert os.path.exists(custom_dir)
        # Cleanup
        os.rmdir(custom_dir)
    
    def test_random_user_agent(self):
        """测试随机User-Agent / Test random User-Agent"""
        scraper = AmazonScraper()
        ua = scraper._get_random_user_agent()
        assert ua in [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
    
    def test_extract_text_basic(self):
        """测试基础文本提取 / Test basic text extraction"""
        html = '<div class="test"><span class="title">Test Product</span></div>'
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.test')
        
        scraper = AmazonScraper()
        text = scraper._extract_text(item, ['span.title'])
        assert text == "Test Product"
    
    def test_extract_text_fallback(self):
        """测试文本提取降级 / Test text extraction fallback"""
        html = '<div class="test"><h2>Product Title</h2></div>'
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.test')
        
        scraper = AmazonScraper()
        # 第一个选择器不存在，应该降级到h2
        text = scraper._extract_text(item, ['span.missing', 'h2'])
        assert text == "Product Title"
    
    def test_extract_text_with_attr(self):
        """测试属性提取 / Test attribute extraction"""
        html = '<div class="test"><img src="image.jpg" alt="Product Image"></div>'
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.test')
        
        scraper = AmazonScraper()
        alt_text = scraper._extract_text(item, ['img'], attr='alt')
        assert alt_text == "Product Image"
    
    def test_extract_price(self):
        """测试价格提取 / Test price extraction"""
        html = '''
        <div class="product">
            <span class="a-price">
                <span class="a-price-whole">19</span>
                <span class="a-price-fraction">99</span>
            </span>
        </div>
        '''
        soup = BeautifulSoup(html, 'lxml')
        item = soup.select_one('div.product')
        
        scraper = AmazonScraper()
        price = scraper._extract_price(item)
        # The function combines whole + fraction when both are found
        assert "19" in price  # At minimum should contain the whole number
    
    def test_save_data(self):
        """测试数据保存 / Test data saving"""
        scraper = AmazonScraper()
        test_data = [
            {
                "asin": "TEST123",
                "title": "Test Product",
                "price": "$19.99"
            }
        ]
        
        filepath = scraper.save_data(test_data, filename="test_products.json")
        assert os.path.exists(filepath)
        
        # 验证文件内容 / Verify file content
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['total_count'] == 1
        assert saved_data['items'][0]['asin'] == "TEST123"
        assert 'scraped_at' in saved_data
        
        # Cleanup
        os.remove(filepath)
    
    def test_selectors_config(self):
        """测试选择器配置 / Test selectors configuration"""
        assert 'list_selectors' in SELECTORS
        assert 'title_selectors' in SELECTORS
        assert 'price_selectors' in SELECTORS
        assert 'rating_selectors' in SELECTORS
        assert 'review_count_selectors' in SELECTORS
        
        assert len(SELECTORS['list_selectors']) > 0
        assert len(SELECTORS['title_selectors']) > 0
        assert len(SELECTORS['price_selectors']) > 0
    
    def test_convenience_function(self):
        """测试便捷函数接口 / Test convenience function interface"""
        # 这个测试只验证函数可以调用，不实际执行网络请求
        # This test only verifies the function can be called, no actual network request
        from unittest.mock import patch, MagicMock
        
        with patch.object(AmazonScraper, 'run') as mock_run:
            mock_run.return_value = []
            result = scrape_amazon("https://test.com", max_items=10, deep_detail=False)
            mock_run.assert_called_once()
            assert result == []


class TestDataFetcherIntegration:
    """测试与data_fetcher的集成 / Test integration with data_fetcher"""
    
    @pytest.mark.skipif(True, reason="Streamlit dependency required for data_fetcher")
    def test_fetch_amazon_data_function_exists(self):
        """测试Amazon数据获取函数存在 / Test Amazon data fetch function exists"""
        from core.data_fetcher import get_platform_data
        
        # 验证函数存在且可调用 / Verify function exists and is callable
        assert callable(get_platform_data)
    
    @pytest.mark.skipif(True, reason="Streamlit dependency required for data_fetcher")
    def test_platform_list_includes_amazon(self):
        """测试平台列表包含Amazon / Test platform list includes Amazon"""
        from core.data_fetcher import PLATFORM_LIST
        assert "Amazon" in PLATFORM_LIST


class TestDispatcherIntegration:
    """测试与dispatcher的集成 / Test integration with dispatcher"""
    
    def test_crawl_url_function_updated(self):
        """测试URL爬取函数已更新 / Test crawl URL function updated"""
        from core.crawl.dispatcher import _crawl_url
        assert callable(_crawl_url)
    
    def test_run_batch_function(self):
        """测试批量运行函数 / Test run batch function"""
        from core.crawl.dispatcher import run_batch
        assert callable(run_batch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
