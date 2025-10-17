"""
Tests for Data Validation Module
数据验证模块测试
"""

import pytest
from core.data_validation import (
    ValidationRule, DataValidator, DataDeduplicator, DataQualityChecker,
    create_amazon_validator, create_amazon_deduplicator
)


class TestValidationRule:
    """Test ValidationRule class / 测试 ValidationRule 类"""
    
    def test_required_field_present(self):
        """Test validation with required field present / 测试必需字段存在时的验证"""
        rule = ValidationRule("name", "type", {"type": "string"}, required=True)
        data = {"name": "Test"}
        
        is_valid, error = rule.validate(data)
        
        assert is_valid is True
        assert error is None
    
    def test_required_field_missing(self):
        """Test validation with required field missing / 测试必需字段缺失时的验证"""
        rule = ValidationRule("name", "type", {"type": "string"}, required=True)
        data = {}
        
        is_valid, error = rule.validate(data)
        
        assert is_valid is False
        assert "缺失" in error
    
    def test_optional_field_missing(self):
        """Test validation with optional field missing / 测试可选字段缺失时的验证"""
        rule = ValidationRule("name", "type", {"type": "string"}, required=False)
        data = {}
        
        is_valid, error = rule.validate(data)
        
        assert is_valid is True
    
    def test_type_validation_string(self):
        """Test string type validation / 测试字符串类型验证"""
        rule = ValidationRule("name", "type", {"type": "string"})
        
        is_valid, _ = rule.validate({"name": "test"})
        assert is_valid is True
        
        is_valid, _ = rule.validate({"name": 123})
        assert is_valid is False
    
    def test_type_validation_number(self):
        """Test number type validation / 测试数字类型验证"""
        rule = ValidationRule("age", "type", {"type": "number"})
        
        is_valid, _ = rule.validate({"age": 25})
        assert is_valid is True
        
        is_valid, _ = rule.validate({"age": 25.5})
        assert is_valid is True
        
        is_valid, _ = rule.validate({"age": "25"})
        assert is_valid is False
    
    def test_regex_validation(self):
        """Test regex pattern validation / 测试正则表达式验证"""
        rule = ValidationRule("asin", "regex", {"pattern": r"^[A-Z0-9]{10}$"})
        
        is_valid, _ = rule.validate({"asin": "B08N5WRWNW"})
        assert is_valid is True
        
        is_valid, _ = rule.validate({"asin": "invalid"})
        assert is_valid is False
    
    def test_length_validation(self):
        """Test length validation / 测试长度验证"""
        rule = ValidationRule("title", "length", {"min": 5, "max": 100})
        
        is_valid, _ = rule.validate({"title": "Valid Title"})
        assert is_valid is True
        
        is_valid, _ = rule.validate({"title": "Hi"})
        assert is_valid is False
        
        is_valid, _ = rule.validate({"title": "x" * 150})
        assert is_valid is False
    
    def test_range_validation(self):
        """Test range validation / 测试范围验证"""
        rule = ValidationRule("price", "range", {"min": 0, "max": 10000})
        
        is_valid, _ = rule.validate({"price": 50})
        assert is_valid is True
        
        is_valid, _ = rule.validate({"price": -10})
        assert is_valid is False
        
        is_valid, _ = rule.validate({"price": 20000})
        assert is_valid is False


class TestDataValidator:
    """Test DataValidator class / 测试 DataValidator 类"""
    
    def test_validator_initialization(self):
        """Test validator initialization / 测试验证器初始化"""
        validator = DataValidator()
        assert len(validator.rules) == 0
    
    def test_add_rule(self):
        """Test adding validation rule / 测试添加验证规则"""
        validator = DataValidator()
        rule = ValidationRule("name", "type", {"type": "string"})
        
        validator.add_rule(rule)
        
        assert len(validator.rules) == 1
    
    def test_validate_single_data(self):
        """Test validating single data / 测试验证单个数据"""
        validator = DataValidator()
        validator.add_rule(ValidationRule("name", "type", {"type": "string"}, required=True))
        validator.add_rule(ValidationRule("age", "type", {"type": "number"}, required=True))
        
        # Valid data
        is_valid, errors = validator.validate({"name": "John", "age": 30})
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid data
        is_valid, errors = validator.validate({"name": "John"})
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_batch(self):
        """Test validating batch data / 测试批量验证数据"""
        validator = DataValidator()
        validator.add_rule(ValidationRule("name", "type", {"type": "string"}, required=True))
        
        data_list = [
            {"name": "John"},
            {"name": "Jane"},
            {"age": 30},  # Missing name
            {"name": "Bob"}
        ]
        
        valid_data, invalid_data = validator.validate_batch(data_list)
        
        assert len(valid_data) == 3
        assert len(invalid_data) == 1
        assert invalid_data[0]["index"] == 2


class TestDataDeduplicator:
    """Test DataDeduplicator class / 测试 DataDeduplicator 类"""
    
    def test_deduplicator_initialization(self):
        """Test deduplicator initialization / 测试去重器初始化"""
        dedup = DataDeduplicator()
        assert len(dedup.seen_hashes) == 0
    
    def test_deduplicator_with_hash_fields(self):
        """Test deduplicator with specific hash fields / 测试使用特定哈希字段的去重器"""
        dedup = DataDeduplicator(hash_fields=["id"])
        assert dedup.hash_fields == ["id"]
    
    def test_is_duplicate(self):
        """Test duplicate detection / 测试重复检测"""
        dedup = DataDeduplicator()
        
        data1 = {"id": 1, "name": "John"}
        data2 = {"id": 1, "name": "John"}
        
        # First time - not duplicate
        assert dedup.is_duplicate(data1) is False
        
        # Add to seen
        dedup.add(data1)
        
        # Second time - is duplicate
        assert dedup.is_duplicate(data2) is True
    
    def test_add_unique_data(self):
        """Test adding unique data / 测试添加唯一数据"""
        dedup = DataDeduplicator()
        
        data = {"id": 1, "name": "John"}
        
        result = dedup.add(data)
        
        assert result is True
        assert len(dedup.seen_hashes) == 1
    
    def test_add_duplicate_data(self):
        """Test adding duplicate data / 测试添加重复数据"""
        dedup = DataDeduplicator()
        
        data1 = {"id": 1, "name": "John"}
        data2 = {"id": 1, "name": "John"}
        
        result1 = dedup.add(data1)
        result2 = dedup.add(data2)
        
        assert result1 is True
        assert result2 is False
        assert len(dedup.seen_hashes) == 1
    
    def test_deduplicate_list(self):
        """Test deduplicating a list / 测试去重列表"""
        dedup = DataDeduplicator()
        
        data_list = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
            {"id": 1, "name": "John"},  # Duplicate
            {"id": 3, "name": "Bob"}
        ]
        
        unique_data, duplicate_count = dedup.deduplicate(data_list)
        
        assert len(unique_data) == 3
        assert duplicate_count == 1
    
    def test_hash_specific_fields(self):
        """Test hashing specific fields / 测试哈希特定字段"""
        dedup = DataDeduplicator(hash_fields=["id"])
        
        data1 = {"id": 1, "name": "John"}
        data2 = {"id": 1, "name": "Jane"}  # Same ID, different name
        
        dedup.add(data1)
        
        # Should be considered duplicate based on ID only
        assert dedup.is_duplicate(data2) is True
    
    def test_reset(self):
        """Test resetting deduplicator / 测试重置去重器"""
        dedup = DataDeduplicator()
        
        data = {"id": 1, "name": "John"}
        dedup.add(data)
        
        assert len(dedup.seen_hashes) == 1
        
        dedup.reset()
        
        assert len(dedup.seen_hashes) == 0


class TestDataQualityChecker:
    """Test DataQualityChecker class / 测试 DataQualityChecker 类"""
    
    def test_quality_checker_initialization(self):
        """Test quality checker initialization / 测试质量检查器初始化"""
        checker = DataQualityChecker()
        assert checker.validator is not None
        assert checker.deduplicator is not None
    
    def test_comprehensive_check(self):
        """Test comprehensive quality check / 测试综合质量检查"""
        validator = DataValidator()
        validator.add_rule(ValidationRule("name", "type", {"type": "string"}, required=True))
        
        dedup = DataDeduplicator()
        
        checker = DataQualityChecker(validator, dedup)
        
        data_list = [
            {"name": "John"},
            {"name": "Jane"},
            {"name": "John"},  # Duplicate
            {"age": 30},  # Invalid - missing name
        ]
        
        report = checker.check(data_list)
        
        assert report["input_count"] == 4
        assert report["valid_count"] == 3
        assert report["invalid_count"] == 1
        assert report["unique_count"] == 2
        assert report["duplicate_count"] == 1
        assert "quality_score" in report
        assert "valid_data" in report
        assert "invalid_data" in report


class TestPredefinedValidators:
    """Test predefined validators / 测试预定义验证器"""
    
    def test_create_amazon_validator(self):
        """Test creating Amazon validator / 测试创建 Amazon 验证器"""
        validator = create_amazon_validator()
        
        # Valid Amazon product
        valid_product = {
            "asin": "B08N5WRWNW",
            "title": "Apple MacBook Pro",
            "price": "$1299.99"
        }
        
        is_valid, errors = validator.validate(valid_product)
        assert is_valid is True
        
        # Invalid product - missing required field
        invalid_product = {
            "title": "Product"
        }
        
        is_valid, errors = validator.validate(invalid_product)
        assert is_valid is False
    
    def test_amazon_asin_validation(self):
        """Test Amazon ASIN format validation / 测试 Amazon ASIN 格式验证"""
        validator = create_amazon_validator()
        
        # Valid ASIN
        product1 = {"asin": "B08N5WRWNW", "title": "Product"}
        is_valid, _ = validator.validate(product1)
        assert is_valid is True
        
        # Invalid ASIN - too short
        product2 = {"asin": "B08N5", "title": "Product"}
        is_valid, _ = validator.validate(product2)
        assert is_valid is False
        
        # Invalid ASIN - contains lowercase
        product3 = {"asin": "b08n5wrwnw", "title": "Product"}
        is_valid, _ = validator.validate(product3)
        assert is_valid is False
    
    def test_create_amazon_deduplicator(self):
        """Test creating Amazon deduplicator / 测试创建 Amazon 去重器"""
        dedup = create_amazon_deduplicator()
        
        assert dedup.hash_fields == ["asin"]
        
        # Same ASIN, different other fields
        product1 = {"asin": "B08N5WRWNW", "title": "Product 1", "price": "$10"}
        product2 = {"asin": "B08N5WRWNW", "title": "Product 2", "price": "$20"}
        
        dedup.add(product1)
        
        # Should be duplicate based on ASIN
        assert dedup.is_duplicate(product2) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
