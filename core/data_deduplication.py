"""
数据去重工具模块
Data Deduplication Utility Module
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataDeduplicator:
    """数据去重器 - 支持多种去重策略"""
    
    def __init__(self, storage_path: str = "data/authoritative_sources"):
        self.storage_path = storage_path
        self.seen_hashes_file = os.path.join(storage_path, ".seen_hashes.json")
        self.seen_hashes = self._load_seen_hashes()
    
    def _load_seen_hashes(self) -> Dict[str, Any]:
        """加载已见过的数据哈希"""
        if os.path.exists(self.seen_hashes_file):
            try:
                with open(self.seen_hashes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading seen hashes: {e}")
                return {}
        return {}
    
    def _save_seen_hashes(self):
        """保存已见过的数据哈希"""
        try:
            os.makedirs(os.path.dirname(self.seen_hashes_file), exist_ok=True)
            with open(self.seen_hashes_file, 'w', encoding='utf-8') as f:
                json.dump(self.seen_hashes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving seen hashes: {e}")
    
    def get_url_hash(self, url: str) -> str:
        """基于URL生成哈希"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def get_content_hash(self, content: str) -> str:
        """基于内容生成哈希"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_title_time_hash(self, title: str, timestamp: str) -> str:
        """基于标题和时间生成哈希"""
        combined = f"{title}_{timestamp}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def is_duplicate_by_url(self, url: str) -> bool:
        """检查URL是否重复"""
        url_hash = self.get_url_hash(url)
        return url_hash in self.seen_hashes.get('url', {})
    
    def is_duplicate_by_content(self, content: str, threshold: float = 0.95) -> bool:
        """检查内容是否重复"""
        content_hash = self.get_content_hash(content)
        
        # Exact match
        if content_hash in self.seen_hashes.get('content', {}):
            return True
        
        # Could add similarity checking here for near-duplicates
        # For now, just checking exact hash matches
        return False
    
    def is_duplicate_by_title_time(self, title: str, timestamp: str) -> bool:
        """检查标题+时间组合是否重复"""
        title_time_hash = self.get_title_time_hash(title, timestamp)
        return title_time_hash in self.seen_hashes.get('title_time', {})
    
    def mark_as_seen(self, method: str, identifier: str, metadata: Dict[str, Any] = None):
        """标记数据为已见过"""
        if method not in self.seen_hashes:
            self.seen_hashes[method] = {}
        
        hash_value = None
        if method == 'url':
            hash_value = self.get_url_hash(identifier)
        elif method == 'content':
            hash_value = self.get_content_hash(identifier)
        elif method == 'title_time':
            # identifier should be "title|timestamp"
            parts = identifier.split('|')
            if len(parts) == 2:
                hash_value = self.get_title_time_hash(parts[0], parts[1])
        
        if hash_value:
            self.seen_hashes[method][hash_value] = {
                "first_seen": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            self._save_seen_hashes()
    
    def deduplicate_data_list(
        self, 
        data_list: List[Dict[str, Any]], 
        method: str = 'url',
        url_key: str = 'url',
        content_key: str = 'content',
        title_key: str = 'title',
        time_key: str = 'timestamp'
    ) -> List[Dict[str, Any]]:
        """
        对数据列表进行去重
        
        Args:
            data_list: 待去重的数据列表
            method: 去重方法 ('url', 'content', 'title_time')
            url_key: URL字段名
            content_key: 内容字段名
            title_key: 标题字段名
            time_key: 时间字段名
            
        Returns:
            去重后的数据列表
        """
        unique_data = []
        
        for item in data_list:
            is_duplicate = False
            
            if method == 'url' and url_key in item:
                is_duplicate = self.is_duplicate_by_url(item[url_key])
                identifier = item[url_key]
            
            elif method == 'content' and content_key in item:
                is_duplicate = self.is_duplicate_by_content(item[content_key])
                identifier = item[content_key]
            
            elif method == 'title_time' and title_key in item and time_key in item:
                is_duplicate = self.is_duplicate_by_title_time(
                    item[title_key], 
                    item[time_key]
                )
                identifier = f"{item[title_key]}|{item[time_key]}"
            
            else:
                # No valid method or missing keys, keep the item
                unique_data.append(item)
                continue
            
            if not is_duplicate:
                unique_data.append(item)
                # Mark as seen
                self.mark_as_seen(method, identifier, {
                    title_key: item.get(title_key, ''),
                    'source': item.get('source', '')
                })
            else:
                logger.info(f"Duplicate detected and skipped: {identifier[:50]}...")
        
        logger.info(f"Deduplication: {len(data_list)} items -> {len(unique_data)} unique items")
        return unique_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取去重统计信息"""
        stats = {
            'total_seen': 0,
            'by_method': {}
        }
        
        for method, hashes in self.seen_hashes.items():
            count = len(hashes)
            stats['by_method'][method] = count
            stats['total_seen'] += count
        
        return stats
    
    def clear_old_hashes(self, days: int = 30):
        """清理超过指定天数的旧哈希记录"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cleared_count = 0
        
        for method in list(self.seen_hashes.keys()):
            hashes = self.seen_hashes[method]
            for hash_value in list(hashes.keys()):
                try:
                    first_seen = datetime.fromisoformat(hashes[hash_value]['first_seen'])
                    if first_seen < cutoff_date:
                        del hashes[hash_value]
                        cleared_count += 1
                except Exception:
                    continue
        
        if cleared_count > 0:
            self._save_seen_hashes()
            logger.info(f"Cleared {cleared_count} old hash records")
        
        return cleared_count


def deduplicate_scraped_data(
    data: List[Dict[str, Any]], 
    method: str = 'url',
    storage_path: str = "data/authoritative_sources"
) -> List[Dict[str, Any]]:
    """
    便捷函数：对爬取的数据进行去重
    
    Args:
        data: 待去重的数据列表
        method: 去重方法
        storage_path: 存储路径
        
    Returns:
        去重后的数据列表
    """
    deduplicator = DataDeduplicator(storage_path)
    return deduplicator.deduplicate_data_list(data, method=method)
