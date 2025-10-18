"""
高级分析模块 - 竞品分析和市场洞察
Advanced Analysis Module - Competitive analysis and market insights

功能特性 / Features:
- 竞品矩阵分析 / Competitor matrix analysis
- 价格分布图 / Price distribution charts
- 评论关键词云 / Review keyword cloud
- 品牌集中度分析 / Brand concentration analysis
- 市场趋势分析 / Market trend analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 设置中文字体支持
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    logger.warning("Chinese font not available, using default font")


class AdvancedAnalyzer:
    """高级分析器 / Advanced Analyzer"""
    
    def __init__(self, output_dir: str = "data/analysis"):
        """
        初始化分析器
        
        Args:
            output_dir: 输出目录 / Output directory
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Advanced analyzer initialized")
    
    def analyze_competitor_matrix(self, 
                                  products: List[Dict[str, Any]],
                                  group_by: str = 'brand') -> pd.DataFrame:
        """
        竞品矩阵分析（不同卖家的价格/评分对比）
        Competitor matrix analysis (price/rating comparison across sellers)
        
        Args:
            products: 商品数据列表 / Product data list
            group_by: 分组依据（brand/seller） / Group by field
            
        Returns:
            竞品矩阵数据框 / Competitor matrix dataframe
        """
        logger.info("Analyzing competitor matrix...")
        
        if not products:
            logger.warning("No products to analyze")
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(products)
        
        # 提取价格和评分数据
        df['price_numeric'] = df.get('price', df.get('current_price', '')).apply(self._extract_price)
        df['rating_numeric'] = df.get('rating', df.get('average_rating', '')).apply(self._extract_rating)
        df['review_count_numeric'] = df.get('review_count', '').apply(self._extract_number)
        
        # 确保分组字段存在
        if group_by not in df.columns:
            df[group_by] = 'Unknown'
        
        # 按品牌/卖家分组统计
        matrix = df.groupby(group_by).agg({
            'price_numeric': ['mean', 'min', 'max', 'std', 'count'],
            'rating_numeric': ['mean', 'min', 'max'],
            'review_count_numeric': ['mean', 'sum']
        }).round(2)
        
        # 扁平化列名
        matrix.columns = ['_'.join(col).strip() for col in matrix.columns.values]
        matrix = matrix.reset_index()
        
        # 计算市场份额
        total_products = len(df)
        matrix['market_share_percent'] = (matrix['price_numeric_count'] / total_products * 100).round(2)
        
        # 按市场份额排序
        matrix = matrix.sort_values('market_share_percent', ascending=False)
        
        logger.info(f"Competitor matrix created with {len(matrix)} competitors")
        return matrix
    
    def analyze_price_distribution(self, 
                                   products: List[Dict[str, Any]],
                                   save_plot: bool = True) -> Dict[str, Any]:
        """
        价格分布分析（箱线图或区间分布）
        Price distribution analysis (box plot or interval distribution)
        
        Args:
            products: 商品数据列表 / Product data list
            save_plot: 是否保存图表 / Whether to save plot
            
        Returns:
            价格分布统计 / Price distribution statistics
        """
        logger.info("Analyzing price distribution...")
        
        if not products:
            logger.warning("No products to analyze")
            return {}
        
        # 提取价格数据
        prices = []
        for product in products:
            price_str = product.get('price', product.get('current_price', ''))
            price = self._extract_price(price_str)
            if price > 0:
                prices.append(price)
        
        if not prices:
            logger.warning("No valid prices found")
            return {}
        
        prices_array = np.array(prices)
        
        # 计算统计数据
        stats = {
            'mean': float(np.mean(prices_array)),
            'median': float(np.median(prices_array)),
            'std': float(np.std(prices_array)),
            'min': float(np.min(prices_array)),
            'max': float(np.max(prices_array)),
            'q25': float(np.percentile(prices_array, 25)),
            'q75': float(np.percentile(prices_array, 75)),
            'count': len(prices)
        }
        
        # 价格区间分布
        bins = [0, 50, 100, 200, 500, 1000, float('inf')]
        labels = ['<$50', '$50-100', '$100-200', '$200-500', '$500-1000', '>$1000']
        price_ranges = pd.cut(prices_array, bins=bins, labels=labels)
        range_counts = price_ranges.value_counts().to_dict()
        stats['price_ranges'] = {str(k): int(v) for k, v in range_counts.items()}
        
        # 生成图表
        if save_plot:
            self._plot_price_distribution(prices_array, stats)
        
        logger.info(f"Price distribution analyzed: mean=${stats['mean']:.2f}, median=${stats['median']:.2f}")
        return stats
    
    def _plot_price_distribution(self, prices: np.ndarray, stats: Dict[str, Any]):
        """绘制价格分布图 / Plot price distribution"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # 箱线图
        axes[0].boxplot(prices, orientation='vertical')
        axes[0].set_ylabel('Price ($)')
        axes[0].set_title('Price Distribution - Box Plot')
        axes[0].grid(True, alpha=0.3)
        
        # 添加统计信息
        textstr = f"Mean: ${stats['mean']:.2f}\nMedian: ${stats['median']:.2f}\nStd: ${stats['std']:.2f}"
        axes[0].text(0.05, 0.95, textstr, transform=axes[0].transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 直方图
        axes[1].hist(prices, bins=30, edgecolor='black', alpha=0.7)
        axes[1].axvline(stats['mean'], color='red', linestyle='--', linewidth=2, label=f"Mean: ${stats['mean']:.2f}")
        axes[1].axvline(stats['median'], color='green', linestyle='--', linewidth=2, label=f"Median: ${stats['median']:.2f}")
        axes[1].set_xlabel('Price ($)')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Price Distribution - Histogram')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"price_distribution_{timestamp}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Price distribution plot saved: {filepath}")
    
    def analyze_keywords(self, 
                        products: List[Dict[str, Any]],
                        text_field: str = 'title',
                        top_n: int = 50,
                        save_wordcloud: bool = True) -> Dict[str, int]:
        """
        评论关键词分析（使用jieba分词）
        Keyword analysis (using jieba for Chinese text)
        
        Args:
            products: 商品数据列表 / Product data list
            text_field: 文本字段名 / Text field name
            top_n: 返回前N个关键词 / Return top N keywords
            save_wordcloud: 是否保存词云 / Whether to save word cloud
            
        Returns:
            关键词频率字典 / Keyword frequency dictionary
        """
        logger.info("Analyzing keywords...")
        
        if not products:
            logger.warning("No products to analyze")
            return {}
        
        # 导入jieba（如果可用）
        try:
            import jieba
            use_jieba = True
        except ImportError:
            logger.warning("jieba not installed, using basic word splitting")
            use_jieba = False
        
        # 收集所有文本
        all_text = []
        for product in products:
            text = product.get(text_field, '')
            if text:
                all_text.append(str(text))
        
        combined_text = ' '.join(all_text)
        
        # 分词和统计
        word_freq = {}
        
        if use_jieba:
            # 使用jieba分词（中文）
            words = jieba.cut(combined_text)
            for word in words:
                word = word.strip().lower()
                if len(word) > 1 and not word.isdigit():  # 过滤单字符和纯数字
                    word_freq[word] = word_freq.get(word, 0) + 1
        else:
            # 基础英文分词
            words = combined_text.lower().split()
            for word in words:
                # 移除标点符号
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 2:  # 过滤短词
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # 停用词过滤
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                    '的', '了', '和', '是', '在', '有', '个', '为', '与', '等', '及'}
        word_freq = {k: v for k, v in word_freq.items() if k not in stopwords}
        
        # 排序并获取前N个
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_keywords = dict(sorted_words)
        
        # 生成词云
        if save_wordcloud and top_keywords:
            self._generate_wordcloud(top_keywords)
        
        logger.info(f"Keyword analysis completed: {len(top_keywords)} keywords extracted")
        return top_keywords
    
    def _generate_wordcloud(self, word_freq: Dict[str, int]):
        """生成词云图 / Generate word cloud"""
        try:
            from wordcloud import WordCloud
            
            # 创建词云
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                font_path=None,  # 如果需要中文支持，需要指定中文字体路径
                max_words=100,
                relative_scaling=0.5,
                colormap='viridis'
            ).generate_from_frequencies(word_freq)
            
            # 绘制词云
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Keyword Cloud', fontsize=16, pad=20)
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.output_dir / f"keyword_cloud_{timestamp}.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Word cloud saved: {filepath}")
            
        except ImportError:
            logger.warning("wordcloud library not installed, skipping word cloud generation")
        except Exception as e:
            logger.error(f"Error generating word cloud: {e}")
    
    def analyze_brand_concentration(self, 
                                   products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        品牌集中度分析（品牌数量、市场占比）
        Brand concentration analysis (brand count, market share)
        
        Args:
            products: 商品数据列表 / Product data list
            
        Returns:
            品牌集中度分析结果 / Brand concentration analysis results
        """
        logger.info("Analyzing brand concentration...")
        
        if not products:
            logger.warning("No products to analyze")
            return {}
        
        # 统计品牌
        brand_counts = {}
        for product in products:
            brand = product.get('brand', 'Unknown')
            if not brand or brand == '':
                brand = 'Unknown'
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        total_products = len(products)
        
        # 计算市场份额
        brand_shares = []
        for brand, count in brand_counts.items():
            share = (count / total_products) * 100
            brand_shares.append({
                'brand': brand,
                'count': count,
                'market_share_percent': round(share, 2)
            })
        
        # 按市场份额排序
        brand_shares.sort(key=lambda x: x['market_share_percent'], reverse=True)
        
        # 计算集中度指标
        # HHI (Herfindahl-Hirschman Index) - 赫芬达尔指数
        hhi = sum((share['market_share_percent']) ** 2 for share in brand_shares)
        
        # CR4 (Concentration Ratio) - 前4名集中度
        top4_share = sum(share['market_share_percent'] for share in brand_shares[:4])
        
        # CR8 - 前8名集中度
        top8_share = sum(share['market_share_percent'] for share in brand_shares[:8])
        
        # 判断市场集中度类型
        if hhi > 2500:
            concentration_type = "High Concentration (Oligopoly)"
        elif hhi > 1500:
            concentration_type = "Moderate Concentration"
        else:
            concentration_type = "Low Concentration (Competitive)"
        
        result = {
            'total_brands': len(brand_counts),
            'total_products': total_products,
            'top_brands': brand_shares[:10],  # 前10品牌
            'hhi_index': round(hhi, 2),
            'cr4_percent': round(top4_share, 2),
            'cr8_percent': round(top8_share, 2),
            'concentration_type': concentration_type
        }
        
        # 生成品牌份额饼图
        self._plot_brand_share(brand_shares[:10])
        
        logger.info(f"Brand concentration analyzed: {result['total_brands']} brands, HHI={result['hhi_index']}")
        return result
    
    def _plot_brand_share(self, brand_shares: List[Dict[str, Any]]):
        """绘制品牌市场份额饼图 / Plot brand market share pie chart"""
        if not brand_shares:
            return
        
        brands = [item['brand'][:20] for item in brand_shares]  # 限制品牌名长度
        shares = [item['market_share_percent'] for item in brand_shares]
        
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(brands)))
        
        plt.pie(shares, labels=brands, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title('Top Brands Market Share', fontsize=14, pad=20)
        plt.axis('equal')
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"brand_share_{timestamp}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Brand share plot saved: {filepath}")
    
    def analyze_market_trends(self, 
                             products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        市场趋势分析（价格、销量、评分、评论数）
        Market trend analysis (price, sales, rating, review count)
        
        Args:
            products: 商品数据列表 / Product data list
            
        Returns:
            市场趋势分析结果 / Market trend analysis results
        """
        logger.info("Analyzing market trends...")
        
        if not products:
            logger.warning("No products to analyze")
            return {}
        
        # 提取数据
        prices = []
        ratings = []
        review_counts = []
        
        for product in products:
            price = self._extract_price(product.get('price', product.get('current_price', '')))
            if price > 0:
                prices.append(price)
            
            rating = self._extract_rating(product.get('rating', product.get('average_rating', '')))
            if rating > 0:
                ratings.append(rating)
            
            review_count = self._extract_number(product.get('review_count', ''))
            if review_count > 0:
                review_counts.append(review_count)
        
        # 计算趋势指标
        trends = {
            'price_trends': {
                'average': round(np.mean(prices), 2) if prices else 0,
                'median': round(np.median(prices), 2) if prices else 0,
                'range': [round(np.min(prices), 2), round(np.max(prices), 2)] if prices else [0, 0]
            },
            'rating_trends': {
                'average': round(np.mean(ratings), 2) if ratings else 0,
                'distribution': self._rating_distribution(ratings) if ratings else {}
            },
            'review_trends': {
                'average': round(np.mean(review_counts), 2) if review_counts else 0,
                'total': sum(review_counts) if review_counts else 0,
                'high_engagement_products': len([r for r in review_counts if r > 100]) if review_counts else 0
            },
            'hot_selling_points': self._identify_hot_points(products)
        }
        
        logger.info("Market trends analysis completed")
        return trends
    
    def _rating_distribution(self, ratings: List[float]) -> Dict[str, int]:
        """评分分布统计 / Rating distribution statistics"""
        distribution = {
            '5_stars': 0,
            '4_stars': 0,
            '3_stars': 0,
            '2_stars': 0,
            '1_star': 0
        }
        
        for rating in ratings:
            if rating >= 4.5:
                distribution['5_stars'] += 1
            elif rating >= 3.5:
                distribution['4_stars'] += 1
            elif rating >= 2.5:
                distribution['3_stars'] += 1
            elif rating >= 1.5:
                distribution['2_stars'] += 1
            else:
                distribution['1_star'] += 1
        
        return distribution
    
    def _identify_hot_points(self, products: List[Dict[str, Any]]) -> List[str]:
        """识别热销点 / Identify hot selling points"""
        hot_points = []
        
        # 高评分产品比例
        high_rating_count = sum(1 for p in products 
                               if self._extract_rating(p.get('rating', p.get('average_rating', ''))) >= 4.5)
        if high_rating_count / len(products) > 0.5:
            hot_points.append("High quality products dominate (>50% rated 4.5+)")
        
        # 评论活跃度
        review_counts = [self._extract_number(p.get('review_count', '')) for p in products]
        avg_reviews = np.mean([r for r in review_counts if r > 0]) if any(review_counts) else 0
        if avg_reviews > 500:
            hot_points.append(f"High customer engagement (avg {int(avg_reviews)} reviews)")
        
        # 价格竞争
        prices = [self._extract_price(p.get('price', p.get('current_price', ''))) for p in products]
        price_std = np.std([p for p in prices if p > 0]) if any(prices) else 0
        price_mean = np.mean([p for p in prices if p > 0]) if any(prices) else 0
        if price_std / price_mean < 0.3 if price_mean > 0 else False:
            hot_points.append("Price competition is intense (low price variance)")
        
        return hot_points if hot_points else ["Market data insufficient for trend analysis"]
    
    def generate_comprehensive_report(self, 
                                     products: List[Dict[str, Any]],
                                     report_name: str = None) -> str:
        """
        生成综合分析报告
        Generate comprehensive analysis report
        
        Args:
            products: 商品数据列表 / Product data list
            report_name: 报告名称 / Report name
            
        Returns:
            报告文件路径 / Report file path
        """
        logger.info("Generating comprehensive report...")
        
        if not products:
            logger.warning("No products to analyze")
            return ""
        
        # 执行所有分析
        competitor_matrix = self.analyze_competitor_matrix(products)
        price_dist = self.analyze_price_distribution(products, save_plot=True)
        keywords = self.analyze_keywords(products, save_wordcloud=True)
        brand_concentration = self.analyze_brand_concentration(products)
        market_trends = self.analyze_market_trends(products)
        
        # 创建报告
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_products': len(products),
            'competitor_matrix': competitor_matrix.to_dict('records') if not competitor_matrix.empty else [],
            'price_distribution': price_dist,
            'top_keywords': keywords,
            'brand_concentration': brand_concentration,
            'market_trends': market_trends
        }
        
        # 保存报告
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"market_analysis_report_{timestamp}.json"
        
        filepath = self.output_dir / report_name
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Comprehensive report saved: {filepath}")
        return str(filepath)
    
    # 辅助方法 / Helper methods
    
    def _extract_price(self, price_str: Any) -> float:
        """提取价格数值 / Extract price value"""
        if not price_str:
            return 0.0
        try:
            # 移除货币符号和逗号
            price_str = str(price_str).replace('$', '').replace('¥', '').replace(',', '').strip()
            # 提取第一个数字
            import re
            match = re.search(r'\d+\.?\d*', price_str)
            if match:
                return float(match.group())
        except:
            pass
        return 0.0
    
    def _extract_rating(self, rating_str: Any) -> float:
        """提取评分数值 / Extract rating value"""
        if not rating_str:
            return 0.0
        try:
            rating_str = str(rating_str)
            # 提取第一个数字（通常是评分）
            import re
            match = re.search(r'\d+\.?\d*', rating_str)
            if match:
                rating = float(match.group())
                # 确保评分在0-5之间
                if 0 <= rating <= 5:
                    return rating
        except:
            pass
        return 0.0
    
    def _extract_number(self, num_str: Any) -> int:
        """提取数字 / Extract number"""
        if not num_str:
            return 0
        try:
            # 移除逗号和其他非数字字符
            import re
            num_str = str(num_str).replace(',', '')
            match = re.search(r'\d+', num_str)
            if match:
                return int(match.group())
        except:
            pass
        return 0
