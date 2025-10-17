"""
Data Validation and Deduplication Module
数据验证和去重模块

Supports data quality checks and duplicate detection
支持数据质量检查和重复检测
"""

import hashlib
import json
import re
from typing import List, Dict, Any, Optional, Set, Callable
from datetime import datetime, timezone
from scrapers.logger import log_info, log_error, log_warning


class ValidationRule:
    """Validation rule class / 验证规则类"""
    
    def __init__(self, field: str, rule_type: str, params: Dict[str, Any] = None, required: bool = True):
        """
        Initialize validation rule
        初始化验证规则
        
        Args:
            field: Field name to validate / 要验证的字段名
            rule_type: Rule type (required, type, regex, range, etc.) / 规则类型
            params: Rule parameters / 规则参数
            required: Whether field is required / 字段是否必需
        """
        self.field = field
        self.rule_type = rule_type
        self.params = params or {}
        self.required = required
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate data
        验证数据
        
        Args:
            data: Data to validate / 要验证的数据
            
        Returns:
            (is_valid, error_message) / (是否有效, 错误信息)
        """
        value = data.get(self.field)
        
        # Check if field exists
        if value is None:
            if self.required:
                return False, f"字段 '{self.field}' 缺失"
            return True, None
        
        # Type check
        if self.rule_type == "type":
            expected_type = self.params.get("type")
            if expected_type == "string" and not isinstance(value, str):
                return False, f"字段 '{self.field}' 应为字符串类型"
            elif expected_type == "number" and not isinstance(value, (int, float)):
                return False, f"字段 '{self.field}' 应为数字类型"
            elif expected_type == "boolean" and not isinstance(value, bool):
                return False, f"字段 '{self.field}' 应为布尔类型"
            elif expected_type == "list" and not isinstance(value, list):
                return False, f"字段 '{self.field}' 应为列表类型"
            elif expected_type == "dict" and not isinstance(value, dict):
                return False, f"字段 '{self.field}' 应为字典类型"
        
        # Regex pattern check
        elif self.rule_type == "regex":
            pattern = self.params.get("pattern")
            if pattern and isinstance(value, str):
                if not re.match(pattern, value):
                    return False, f"字段 '{self.field}' 不符合正则表达式: {pattern}"
        
        # Length check
        elif self.rule_type == "length":
            min_len = self.params.get("min")
            max_len = self.params.get("max")
            
            if isinstance(value, (str, list)):
                length = len(value)
                if min_len is not None and length < min_len:
                    return False, f"字段 '{self.field}' 长度不能小于 {min_len}"
                if max_len is not None and length > max_len:
                    return False, f"字段 '{self.field}' 长度不能大于 {max_len}"
        
        # Range check (for numbers)
        elif self.rule_type == "range":
            min_val = self.params.get("min")
            max_val = self.params.get("max")
            
            if isinstance(value, (int, float)):
                if min_val is not None and value < min_val:
                    return False, f"字段 '{self.field}' 不能小于 {min_val}"
                if max_val is not None and value > max_val:
                    return False, f"字段 '{self.field}' 不能大于 {max_val}"
        
        # Custom validator
        elif self.rule_type == "custom":
            validator = self.params.get("validator")
            if validator and callable(validator):
                try:
                    if not validator(value):
                        return False, f"字段 '{self.field}' 未通过自定义验证"
                except Exception as e:
                    return False, f"字段 '{self.field}' 验证出错: {e}"
        
        return True, None


class DataValidator:
    """Data validator class / 数据验证器类"""
    
    def __init__(self):
        """Initialize validator / 初始化验证器"""
        self.rules: List[ValidationRule] = []
        self.custom_validators: Dict[str, Callable] = {}
    
    def add_rule(self, rule: ValidationRule):
        """
        Add validation rule
        添加验证规则
        
        Args:
            rule: Validation rule / 验证规则
        """
        self.rules.append(rule)
    
    def add_custom_validator(self, name: str, validator: Callable):
        """
        Add custom validator function
        添加自定义验证函数
        
        Args:
            name: Validator name / 验证器名称
            validator: Validator function / 验证函数
        """
        self.custom_validators[name] = validator
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data against all rules
        根据所有规则验证数据
        
        Args:
            data: Data to validate / 要验证的数据
            
        Returns:
            (is_valid, error_messages) / (是否有效, 错误信息列表)
        """
        errors = []
        
        for rule in self.rules:
            is_valid, error_msg = rule.validate(data)
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate batch of data
        批量验证数据
        
        Args:
            data_list: List of data to validate / 要验证的数据列表
            
        Returns:
            (valid_data, invalid_data) / (有效数据, 无效数据)
        """
        valid_data = []
        invalid_data = []
        
        for i, data in enumerate(data_list):
            is_valid, errors = self.validate(data)
            if is_valid:
                valid_data.append(data)
            else:
                invalid_data.append({
                    "index": i,
                    "data": data,
                    "errors": errors
                })
        
        log_info(f"验证完成: 有效={len(valid_data)}, 无效={len(invalid_data)}")
        return valid_data, invalid_data


class DataDeduplicator:
    """Data deduplicator class / 数据去重器类"""
    
    def __init__(self, hash_fields: List[str] = None):
        """
        Initialize deduplicator
        初始化去重器
        
        Args:
            hash_fields: Fields to use for hash calculation / 用于哈希计算的字段
        """
        self.hash_fields = hash_fields or []
        self.seen_hashes: Set[str] = set()
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """
        Calculate hash for data
        计算数据的哈希值
        
        Args:
            data: Data to hash / 要哈希的数据
            
        Returns:
            Hash string / 哈希字符串
        """
        if self.hash_fields:
            # Hash specific fields
            hash_data = {k: data.get(k) for k in self.hash_fields if k in data}
        else:
            # Hash all data
            hash_data = data
        
        # Convert to JSON string and calculate hash
        json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def is_duplicate(self, data: Dict[str, Any]) -> bool:
        """
        Check if data is duplicate
        检查数据是否重复
        
        Args:
            data: Data to check / 要检查的数据
            
        Returns:
            True if duplicate / 如果重复则返回 True
        """
        hash_value = self._calculate_hash(data)
        return hash_value in self.seen_hashes
    
    def add(self, data: Dict[str, Any]) -> bool:
        """
        Add data to seen set
        将数据添加到已见集合
        
        Args:
            data: Data to add / 要添加的数据
            
        Returns:
            False if duplicate, True if new / 如果重复返回 False，新数据返回 True
        """
        hash_value = self._calculate_hash(data)
        
        if hash_value in self.seen_hashes:
            return False
        
        self.seen_hashes.add(hash_value)
        return True
    
    def deduplicate(self, data_list: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], int]:
        """
        Remove duplicates from data list
        从数据列表中移除重复项
        
        Args:
            data_list: List of data / 数据列表
            
        Returns:
            (unique_data, duplicate_count) / (唯一数据, 重复数量)
        """
        unique_data = []
        duplicate_count = 0
        
        for data in data_list:
            if self.add(data):
                unique_data.append(data)
            else:
                duplicate_count += 1
        
        log_info(f"去重完成: 唯一={len(unique_data)}, 重复={duplicate_count}")
        return unique_data, duplicate_count
    
    def reset(self):
        """Clear seen hashes / 清除已见哈希"""
        self.seen_hashes.clear()
        log_info("去重器已重置")


class DataQualityChecker:
    """Comprehensive data quality checker / 综合数据质量检查器"""
    
    def __init__(self, validator: DataValidator = None, deduplicator: DataDeduplicator = None):
        """
        Initialize quality checker
        初始化质量检查器
        
        Args:
            validator: Data validator / 数据验证器
            deduplicator: Data deduplicator / 数据去重器
        """
        self.validator = validator or DataValidator()
        self.deduplicator = deduplicator or DataDeduplicator()
    
    def check(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive quality check
        执行综合质量检查
        
        Args:
            data_list: List of data to check / 要检查的数据列表
            
        Returns:
            Quality check report / 质量检查报告
        """
        log_info(f"开始数据质量检查，数据量: {len(data_list)}")
        start_time = datetime.now()
        
        # Validation
        valid_data, invalid_data = self.validator.validate_batch(data_list)
        
        # Deduplication
        unique_data, duplicate_count = self.deduplicator.deduplicate(valid_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration,
            "input_count": len(data_list),
            "valid_count": len(valid_data),
            "invalid_count": len(invalid_data),
            "unique_count": len(unique_data),
            "duplicate_count": duplicate_count,
            "quality_score": len(unique_data) / len(data_list) if data_list else 0,
            "valid_data": unique_data,
            "invalid_data": invalid_data
        }
        
        log_info(f"质量检查完成: 输入={report['input_count']}, "
                f"有效={report['valid_count']}, "
                f"无效={report['invalid_count']}, "
                f"唯一={report['unique_count']}, "
                f"重复={report['duplicate_count']}, "
                f"质量分数={report['quality_score']:.2%}")
        
        return report


# Predefined validators for common use cases / 常见用例的预定义验证器

def create_amazon_validator() -> DataValidator:
    """
    Create validator for Amazon product data
    创建 Amazon 商品数据验证器
    
    Returns:
        Configured validator / 配置好的验证器
    """
    validator = DataValidator()
    
    # Required fields
    validator.add_rule(ValidationRule("asin", "type", {"type": "string"}, required=True))
    validator.add_rule(ValidationRule("title", "type", {"type": "string"}, required=True))
    validator.add_rule(ValidationRule("title", "length", {"min": 1}, required=True))
    
    # Optional fields with type checks
    validator.add_rule(ValidationRule("price", "type", {"type": "string"}, required=False))
    validator.add_rule(ValidationRule("rating", "type", {"type": "string"}, required=False))
    validator.add_rule(ValidationRule("review_count", "type", {"type": "string"}, required=False))
    validator.add_rule(ValidationRule("url", "type", {"type": "string"}, required=False))
    
    # ASIN format validation
    validator.add_rule(ValidationRule("asin", "regex", {"pattern": r"^[A-Z0-9]{10}$"}, required=True))
    
    log_info("Amazon 产品验证器已创建")
    return validator


def create_amazon_deduplicator() -> DataDeduplicator:
    """
    Create deduplicator for Amazon product data
    创建 Amazon 商品数据去重器
    
    Returns:
        Configured deduplicator / 配置好的去重器
    """
    # Deduplicate based on ASIN (unique product identifier)
    return DataDeduplicator(hash_fields=["asin"])
