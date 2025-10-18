"""
Unit tests for advanced analysis module
高级分析模块单元测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd

from core.advanced_analysis import AdvancedAnalyzer


class TestAdvancedAnalyzer(unittest.TestCase):
    """高级分析器测试类 / Advanced Analyzer Test Class"""
    
    def setUp(self):
        """测试前设置 / Setup before tests"""
        self.output_dir = tempfile.mkdtemp()
        self.analyzer = AdvancedAnalyzer(output_dir=self.output_dir)
        
        # Sample product data
        self.sample_products = [
            {
                'brand': 'Apple',
                'title': 'MacBook Pro Laptop Computer',
                'price': '$1299.00',
                'rating': '4.7 out of 5 stars',
                'review_count': '2,456 ratings'
            },
            {
                'brand': 'Apple',
                'title': 'MacBook Air Laptop',
                'price': '$999.00',
                'rating': '4.8 out of 5 stars',
                'review_count': '3,210 ratings'
            },
            {
                'brand': 'Dell',
                'title': 'Dell XPS 13 Laptop Computer',
                'price': '$1099.00',
                'rating': '4.5 out of 5 stars',
                'review_count': '1,234 ratings'
            },
            {
                'brand': 'HP',
                'title': 'HP Pavilion Laptop Computer',
                'price': '$799.00',
                'rating': '4.3 out of 5 stars',
                'review_count': '890 ratings'
            },
            {
                'brand': 'Lenovo',
                'title': 'ThinkPad X1 Laptop Computer',
                'price': '$1199.00',
                'rating': '4.6 out of 5 stars',
                'review_count': '1,567 ratings'
            }
        ]
    
    def tearDown(self):
        """测试后清理 / Cleanup after tests"""
        shutil.rmtree(self.output_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化 / Test initialization"""
        self.assertTrue(Path(self.output_dir).exists())
    
    def test_competitor_matrix(self):
        """测试竞品矩阵分析 / Test competitor matrix analysis"""
        matrix = self.analyzer.analyze_competitor_matrix(self.sample_products, group_by='brand')
        
        self.assertIsInstance(matrix, pd.DataFrame)
        self.assertGreater(len(matrix), 0)
        
        # Check for expected columns
        self.assertIn('brand', matrix.columns)
        self.assertIn('market_share_percent', matrix.columns)
        
        # Verify market shares add up to ~100%
        total_share = matrix['market_share_percent'].sum()
        self.assertAlmostEqual(total_share, 100.0, places=1)
    
    def test_price_distribution(self):
        """测试价格分布分析 / Test price distribution analysis"""
        stats = self.analyzer.analyze_price_distribution(self.sample_products, save_plot=False)
        
        self.assertIn('mean', stats)
        self.assertIn('median', stats)
        self.assertIn('std', stats)
        self.assertIn('min', stats)
        self.assertIn('max', stats)
        self.assertIn('price_ranges', stats)
        
        # Verify statistics are reasonable
        self.assertGreater(stats['mean'], 0)
        self.assertGreater(stats['max'], stats['min'])
        self.assertGreaterEqual(stats['median'], stats['min'])
        self.assertLessEqual(stats['median'], stats['max'])
    
    def test_keyword_analysis(self):
        """测试关键词分析 / Test keyword analysis"""
        keywords = self.analyzer.analyze_keywords(
            self.sample_products,
            text_field='title',
            top_n=10,
            save_wordcloud=False
        )
        
        self.assertIsInstance(keywords, dict)
        self.assertGreater(len(keywords), 0)
        
        # Common words should appear in results
        common_words = ['laptop', 'computer']
        found_common = any(word in ' '.join(keywords.keys()).lower() for word in common_words)
        self.assertTrue(found_common)
    
    def test_brand_concentration(self):
        """测试品牌集中度分析 / Test brand concentration analysis"""
        analysis = self.analyzer.analyze_brand_concentration(self.sample_products)
        
        self.assertIn('total_brands', analysis)
        self.assertIn('total_products', analysis)
        self.assertIn('top_brands', analysis)
        self.assertIn('hhi_index', analysis)
        self.assertIn('cr4_percent', analysis)
        self.assertIn('concentration_type', analysis)
        
        # Verify data integrity
        self.assertEqual(analysis['total_products'], len(self.sample_products))
        self.assertGreater(analysis['total_brands'], 0)
        self.assertGreater(analysis['hhi_index'], 0)
        
        # Verify brand shares
        top_brands = analysis['top_brands']
        self.assertGreater(len(top_brands), 0)
        
        # Market shares should add up to 100%
        total_share = sum(brand['market_share_percent'] for brand in top_brands)
        self.assertAlmostEqual(total_share, 100.0, places=1)
    
    def test_market_trends(self):
        """测试市场趋势分析 / Test market trends analysis"""
        trends = self.analyzer.analyze_market_trends(self.sample_products)
        
        self.assertIn('price_trends', trends)
        self.assertIn('rating_trends', trends)
        self.assertIn('review_trends', trends)
        self.assertIn('hot_selling_points', trends)
        
        # Verify price trends
        price_trends = trends['price_trends']
        self.assertIn('average', price_trends)
        self.assertIn('median', price_trends)
        self.assertGreater(price_trends['average'], 0)
        
        # Verify rating trends
        rating_trends = trends['rating_trends']
        self.assertIn('average', rating_trends)
        self.assertGreater(rating_trends['average'], 0)
        self.assertLessEqual(rating_trends['average'], 5.0)
    
    def test_extract_price(self):
        """测试价格提取 / Test price extraction"""
        test_cases = [
            ('$1299.00', 1299.0),
            ('$99.99', 99.99),
            ('1,234.56', 1234.56),
            ('¥999', 999.0),
            ('invalid', 0.0),
            ('', 0.0),
            (None, 0.0)
        ]
        
        for price_str, expected in test_cases:
            result = self.analyzer._extract_price(price_str)
            self.assertAlmostEqual(result, expected, places=2, 
                                 msg=f"Failed for input: {price_str}")
    
    def test_extract_rating(self):
        """测试评分提取 / Test rating extraction"""
        test_cases = [
            ('4.7 out of 5 stars', 4.7),
            ('4.5', 4.5),
            ('3.8 stars', 3.8),
            ('invalid', 0.0),
            ('', 0.0),
            (None, 0.0)
        ]
        
        for rating_str, expected in test_cases:
            result = self.analyzer._extract_rating(rating_str)
            self.assertAlmostEqual(result, expected, places=1,
                                 msg=f"Failed for input: {rating_str}")
    
    def test_extract_number(self):
        """测试数字提取 / Test number extraction"""
        test_cases = [
            ('2,456 ratings', 2456),
            ('1234', 1234),
            ('3,210 reviews', 3210),
            ('invalid', 0),
            ('', 0),
            (None, 0)
        ]
        
        for num_str, expected in test_cases:
            result = self.analyzer._extract_number(num_str)
            self.assertEqual(result, expected,
                           msg=f"Failed for input: {num_str}")
    
    def test_empty_data_handling(self):
        """测试空数据处理 / Test empty data handling"""
        # Test with empty list
        matrix = self.analyzer.analyze_competitor_matrix([])
        self.assertTrue(matrix.empty)
        
        stats = self.analyzer.analyze_price_distribution([])
        self.assertEqual(stats, {})
        
        keywords = self.analyzer.analyze_keywords([])
        self.assertEqual(keywords, {})
        
        brand_analysis = self.analyzer.analyze_brand_concentration([])
        self.assertEqual(brand_analysis, {})
        
        trends = self.analyzer.analyze_market_trends([])
        self.assertEqual(trends, {})
    
    def test_comprehensive_report(self):
        """测试综合报告生成 / Test comprehensive report generation"""
        report_path = self.analyzer.generate_comprehensive_report(
            self.sample_products,
            report_name='test_report.json'
        )
        
        self.assertTrue(Path(report_path).exists())
        
        # Read and verify report
        import json
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        self.assertIn('generated_at', report)
        self.assertIn('total_products', report)
        self.assertIn('competitor_matrix', report)
        self.assertIn('price_distribution', report)
        self.assertIn('top_keywords', report)
        self.assertIn('brand_concentration', report)
        self.assertIn('market_trends', report)
        
        self.assertEqual(report['total_products'], len(self.sample_products))


if __name__ == '__main__':
    unittest.main()
