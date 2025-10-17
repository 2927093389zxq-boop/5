# 快速启动指南 / Quick Start Guide

## 系统已验证可运行 / System Verified and Ready

✅ 所有代码已通过健康检查  
✅ All code has passed health checks

---

## 1. 启动Web界面 / Start Web Interface

最简单的方式 / The simplest way:

```bash
streamlit run run_launcher.py
```

然后在浏览器中打开 / Then open in browser:
```
http://localhost:8501
```

---

## 2. 运行健康检查 / Run Health Check

验证系统状态 / Verify system status:

```bash
python scripts/code_health_check.py
```

预期输出 / Expected output:
```
✓ 通过: 57 项
✗ 失败: 0 项
⚠ 警告: 0 项
✅ 所有代码检查通过，系统可以正常运行!
```

---

## 3. 运行示例 / Run Examples

### Amazon爬虫示例 / Amazon Scraper Examples
```bash
python examples/amazon_scraper_examples.py
```

### 增强管道演示 / Enhanced Pipeline Demo
```bash
python examples/enhanced_pipeline_demo.py
```

### 多平台爬虫示例 / Multi-Platform Scraper Examples
```bash
python examples/multi_platform_scraper_examples.py
```

---

## 4. 运行测试 / Run Tests

### 所有测试 / All Tests
```bash
python -m pytest test/ -v
```

### 仅单元测试 / Unit Tests Only
```bash
python -m pytest test/unit/ -v
```

### 仅集成测试 / Integration Tests Only
```bash
python -m pytest test/integration/ -v
```

---

## 5. 使用批处理文件 (Windows) / Using Batch Files

### 启动系统 / Start System
```cmd
smart_start.bat
```

### 启动调度器 / Start Scheduler
```cmd
smart_scheduler.bat
```

---

## 6. Python代码快速使用 / Quick Python Usage

### Amazon爬虫 / Amazon Scraper
```python
from scrapers.amazon_scraper import scrape_amazon

# 快速采集
products = scrape_amazon(
    url="https://www.amazon.com/bestsellers",
    max_items=50
)

print(f"采集到 {len(products)} 个商品")
```

### 多平台爬虫 / Multi-Platform Scraper
```python
from scrapers.multi_platform_scraper import scrape_platform

# 采集Shopee数据
products = scrape_platform(
    platform_name="shopee",
    url="https://shopee.ph/search?keyword=phone",
    max_items=50
)
```

---

## 7. 查看文档 / View Documentation

- **项目说明**: `README.md`
- **验证报告**: `VALIDATION_REPORT.md`
- **质量总结**: `CODE_QUALITY_SUMMARY.md`
- **快速指南**: `QUICK_START_GUIDE.md` (当前文件)

---

## 8. 常见问题 / FAQ

### Q: 如何停止Streamlit应用？
A: 在终端按 `Ctrl+C`

### Q: 数据保存在哪里？
A: `data/amazon/` 目录

### Q: 如何查看日志？
A: 查看 `scraper.log` 和 `logs/` 目录

### Q: 如何配置OpenAI API？
A: 在 `.env` 文件中设置 `OPENAI_API_KEY`

---

## 9. 获取帮助 / Get Help

如遇到问题 / If you encounter issues:

1. 运行健康检查 / Run health check:
   ```bash
   python scripts/code_health_check.py
   ```

2. 查看日志文件 / Check log files:
   ```bash
   cat scraper.log
   ```

3. 运行测试 / Run tests:
   ```bash
   python -m pytest test/ -v
   ```

4. 查看文档 / Check documentation:
   - README.md
   - VALIDATION_REPORT.md

---

## 10. 下一步 / Next Steps

1. ✅ 启动Web界面浏览功能
2. ✅ 运行示例代码了解用法
3. ✅ 查看README.md了解详细功能
4. ✅ 根据需求配置和使用

---

**提示**: 所有功能都已验证可用，放心使用！  
**Tip**: All features have been verified and are ready to use!

---

**最后更新 / Last Updated**: 2025-10-17
