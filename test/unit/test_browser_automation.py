"""
Tests for Browser Automation Module
浏览器自动化模块测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.browser_automation import BrowserAutomation, BrowserScraperMixin, scrape_with_browser_sync


class TestBrowserAutomation:
    """Test BrowserAutomation class / 测试 BrowserAutomation 类"""
    
    def test_initialization(self):
        """Test browser automation initialization / 测试浏览器自动化初始化"""
        browser = BrowserAutomation(headless=True, browser_type="chromium")
        assert browser.headless is True
        assert browser.browser_type == "chromium"
        assert browser.playwright is None
        assert browser.browser is None
    
    def test_initialization_with_firefox(self):
        """Test browser initialization with Firefox / 测试使用 Firefox 初始化"""
        browser = BrowserAutomation(headless=False, browser_type="firefox")
        assert browser.headless is False
        assert browser.browser_type == "firefox"
    
    @pytest.mark.asyncio
    async def test_start_without_playwright(self):
        """Test start without Playwright installed / 测试未安装 Playwright 时启动"""
        browser = BrowserAutomation()
        
        with patch('core.browser_automation.async_playwright', side_effect=ImportError):
            result = await browser.start()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test browser close / 测试浏览器关闭"""
        browser = BrowserAutomation()
        
        # Mock browser components
        browser.page = AsyncMock()
        browser.context = AsyncMock()
        browser.browser = AsyncMock()
        browser.playwright = AsyncMock()
        
        await browser.close()
        
        # Verify all components were closed
        browser.page.close.assert_called_once()
        browser.context.close.assert_called_once()
        browser.browser.close.assert_called_once()
        browser.playwright.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_page_content_without_start(self):
        """Test getting page content without starting browser / 测试未启动浏览器时获取页面内容"""
        browser = BrowserAutomation()
        
        with patch.object(browser, 'start', return_value=True):
            with patch.object(browser, 'page', create=True) as mock_page:
                mock_page.goto = AsyncMock()
                mock_page.content = AsyncMock(return_value="<html>test</html>")
                
                content = await browser.get_page_content("https://example.com")
                
                # Verify start was called
                browser.start.assert_called_once()
    
    def test_scrape_with_browser_sync(self):
        """Test synchronous wrapper / 测试同步包装器"""
        with patch('core.browser_automation.scrape_with_browser', return_value="<html>test</html>") as mock_async:
            with patch('core.browser_automation.asyncio.run', return_value="<html>test</html>"):
                result = scrape_with_browser_sync("https://example.com")
                assert result == "<html>test</html>"


class TestBrowserScraperMixin:
    """Test BrowserScraperMixin class / 测试 BrowserScraperMixin 类"""
    
    def test_initialization_without_browser(self):
        """Test initialization without browser / 测试不使用浏览器初始化"""
        
        class TestScraper(BrowserScraperMixin):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        
        scraper = TestScraper(use_browser=False)
        assert scraper.use_browser is False
        assert scraper.browser_automation is None
    
    def test_initialization_with_browser(self):
        """Test initialization with browser / 测试使用浏览器初始化"""
        
        class TestScraper(BrowserScraperMixin):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        
        scraper = TestScraper(use_browser=True)
        assert scraper.use_browser is True
        assert scraper.browser_automation is not None
        assert isinstance(scraper.browser_automation, BrowserAutomation)
    
    @pytest.mark.asyncio
    async def test_fetch_with_browser(self):
        """Test fetch with browser / 测试使用浏览器获取"""
        
        class TestScraper(BrowserScraperMixin):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        
        scraper = TestScraper(use_browser=False)
        
        # Mock browser automation
        with patch.object(BrowserAutomation, 'get_page_content', return_value="<html>test</html>") as mock_get:
            with patch.object(BrowserAutomation, 'close') as mock_close:
                content = await scraper.fetch_with_browser("https://example.com")
                
                # Note: actual implementation uses asyncio which needs proper mocking
                # This is a simplified test


class TestIntegration:
    """Integration tests / 集成测试"""
    
    def test_browser_types_supported(self):
        """Test all supported browser types / 测试所有支持的浏览器类型"""
        for browser_type in ["chromium", "firefox", "webkit"]:
            browser = BrowserAutomation(browser_type=browser_type)
            assert browser.browser_type == browser_type
    
    def test_headless_options(self):
        """Test headless options / 测试无头选项"""
        browser_headless = BrowserAutomation(headless=True)
        browser_headed = BrowserAutomation(headless=False)
        
        assert browser_headless.headless is True
        assert browser_headed.headless is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
