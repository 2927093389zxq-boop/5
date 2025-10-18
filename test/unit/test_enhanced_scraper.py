"""
Unit tests for enhanced scraper module
增强型爬虫模块单元测试
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import json
import csv

from core.enhanced_scraper import EnhancedScraper


class TestEnhancedScraper(unittest.TestCase):
    """增强型爬虫测试类 / Enhanced Scraper Test Class"""
    
    def setUp(self):
        """测试前设置 / Setup before tests"""
        self.cache_dir = tempfile.mkdtemp()
        self.data_dir = tempfile.mkdtemp()
        self.scraper = EnhancedScraper(
            cache_dir=self.cache_dir,
            data_dir=self.data_dir,
            delay_range=(0.1, 0.2),  # Shorter delays for testing
            max_retries=2,
            cache_ttl_hours=1
        )
    
    def tearDown(self):
        """测试后清理 / Cleanup after tests"""
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        shutil.rmtree(self.data_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化 / Test initialization"""
        self.assertTrue(Path(self.cache_dir).exists())
        self.assertTrue(Path(self.data_dir).exists())
        self.assertEqual(self.scraper.max_retries, 2)
        self.assertEqual(len(self.scraper.USER_AGENTS), 14)
    
    def test_user_agent_rotation(self):
        """测试User-Agent轮换 / Test User-Agent rotation"""
        agents = set()
        for _ in range(20):
            agent = self.scraper._get_random_user_agent()
            agents.add(agent)
        
        # Should get multiple different user agents
        self.assertGreater(len(agents), 1)
        
        # All agents should be from the pool
        for agent in agents:
            self.assertIn(agent, self.scraper.USER_AGENTS)
    
    def test_cache_key_generation(self):
        """测试缓存键生成 / Test cache key generation"""
        url1 = "https://example.com/page1"
        url2 = "https://example.com/page2"
        
        key1 = self.scraper._get_cache_key(url1)
        key2 = self.scraper._get_cache_key(url2)
        
        # Keys should be different for different URLs
        self.assertNotEqual(key1, key2)
        
        # Same URL should generate same key
        key1_again = self.scraper._get_cache_key(url1)
        self.assertEqual(key1, key1_again)
        
        # Keys should be MD5 hashes (32 characters)
        self.assertEqual(len(key1), 32)
    
    def test_cache_save_and_load(self):
        """测试缓存保存和加载 / Test cache save and load"""
        url = "https://example.com/test"
        test_data = {
            'html': '<html>Test</html>',
            'url': url,
            'timestamp': '2025-10-18T00:00:00'
        }
        
        # Save to cache
        self.scraper._save_to_cache(url, test_data)
        
        # Load from cache
        cached_data = self.scraper._get_from_cache(url)
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['html'], test_data['html'])
        self.assertEqual(cached_data['url'], test_data['url'])
    
    def test_csv_export(self):
        """测试CSV导出 / Test CSV export"""
        products = [
            {'title': 'Product 1', 'price': '$99.99', 'rating': '4.5'},
            {'title': 'Product 2', 'price': '$149.99', 'rating': '4.7'}
        ]
        
        filepath = self.scraper.save_to_csv(products, 'test_products.csv')
        
        self.assertTrue(os.path.exists(filepath))
        
        # Read and verify CSV
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['title'], 'Product 1')
        self.assertEqual(rows[1]['price'], '$149.99')
    
    def test_json_export(self):
        """测试JSON导出 / Test JSON export"""
        products = [
            {'title': 'Product 1', 'price': '$99.99'},
            {'title': 'Product 2', 'price': '$149.99'}
        ]
        
        filepath = self.scraper.save_to_json(products, 'test_products.json')
        
        self.assertTrue(os.path.exists(filepath))
        
        # Read and verify JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('products', data)
        self.assertEqual(data['total_count'], 2)
        self.assertEqual(len(data['products']), 2)
        self.assertEqual(data['products'][0]['title'], 'Product 1')
    
    def test_empty_data_handling(self):
        """测试空数据处理 / Test empty data handling"""
        # Test with empty list
        csv_path = self.scraper.save_to_csv([], 'empty.csv')
        json_path = self.scraper.save_to_json([], 'empty.json')
        
        self.assertEqual(csv_path, "")
        self.assertEqual(json_path, "")
    
    def test_clear_cache(self):
        """测试清理缓存 / Test cache clearing"""
        # Save some test cache
        for i in range(5):
            url = f"https://example.com/page{i}"
            self.scraper._save_to_cache(url, {'html': f'<html>Page {i}</html>'})
        
        # Verify cache files exist
        cache_files = list(Path(self.cache_dir).glob("*.json"))
        self.assertEqual(len(cache_files), 5)
        
        # Clear cache
        cleared = self.scraper.clear_cache(older_than_hours=0)
        
        # Verify cache is cleared
        self.assertEqual(cleared, 5)
        cache_files = list(Path(self.cache_dir).glob("*.json"))
        self.assertEqual(len(cache_files), 0)


if __name__ == '__main__':
    unittest.main()
