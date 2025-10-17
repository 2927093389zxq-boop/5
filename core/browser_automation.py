"""
Browser Automation Module - Playwright Integration
浏览器自动化模块 - Playwright 集成

Supports JavaScript-rendered content scraping
支持 JavaScript 渲染内容的抓取
"""

import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from scrapers.logger import log_info, log_error, log_warning


class BrowserAutomation:
    """Browser automation class using Playwright / 使用 Playwright 的浏览器自动化类"""
    
    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        """
        Initialize browser automation
        初始化浏览器自动化
        
        Args:
            headless: Run browser in headless mode / 无头模式运行浏览器
            browser_type: Browser type (chromium, firefox, webkit) / 浏览器类型
        """
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def start(self):
        """Start browser / 启动浏览器"""
        try:
            from playwright.async_api import async_playwright
            
            log_info(f"启动 {self.browser_type} 浏览器 (headless={self.headless})")
            self.playwright = await async_playwright().start()
            
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
            
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            self.page = await self.context.new_page()
            
            log_info("浏览器启动成功")
            return True
            
        except ImportError:
            log_error("Playwright 未安装，请运行: pip install playwright && playwright install")
            return False
        except Exception as e:
            log_error(f"启动浏览器失败: {e}")
            return False
    
    async def close(self):
        """Close browser / 关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            log_info("浏览器已关闭")
        except Exception as e:
            log_error(f"关闭浏览器时出错: {e}")
    
    async def get_page_content(self, url: str, wait_for: str = None, timeout: int = 30000) -> Optional[str]:
        """
        Get page content with JavaScript rendering
        获取经过 JavaScript 渲染的页面内容
        
        Args:
            url: Target URL / 目标 URL
            wait_for: Selector to wait for / 等待的选择器
            timeout: Timeout in milliseconds / 超时时间（毫秒）
            
        Returns:
            Page HTML content / 页面 HTML 内容
        """
        try:
            if not self.page:
                await self.start()
            
            log_info(f"正在访问: {url}")
            await self.page.goto(url, wait_until="networkidle", timeout=timeout)
            
            # Wait for specific element if provided
            if wait_for:
                log_info(f"等待元素: {wait_for}")
                await self.page.wait_for_selector(wait_for, timeout=timeout)
            
            # Get page content
            content = await self.page.content()
            log_info(f"成功获取页面内容，长度: {len(content)}")
            
            return content
            
        except Exception as e:
            log_error(f"获取页面内容失败: {e}")
            return None
    
    async def get_page_with_scroll(self, url: str, scroll_times: int = 3, wait_for: str = None) -> Optional[str]:
        """
        Get page content with scrolling for lazy-loaded content
        通过滚动获取延迟加载内容的页面
        
        Args:
            url: Target URL / 目标 URL
            scroll_times: Number of times to scroll / 滚动次数
            wait_for: Selector to wait for / 等待的选择器
            
        Returns:
            Page HTML content / 页面 HTML 内容
        """
        try:
            if not self.page:
                await self.start()
            
            log_info(f"正在访问并滚动页面: {url}")
            await self.page.goto(url, wait_until="networkidle")
            
            if wait_for:
                await self.page.wait_for_selector(wait_for)
            
            # Scroll to load lazy content
            for i in range(scroll_times):
                log_info(f"滚动页面 {i+1}/{scroll_times}")
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            
            content = await self.page.content()
            log_info(f"成功获取页面内容，长度: {len(content)}")
            
            return content
            
        except Exception as e:
            log_error(f"获取页面内容失败: {e}")
            return None
    
    async def screenshot(self, filepath: str = None) -> Optional[str]:
        """
        Take screenshot / 截图
        
        Args:
            filepath: Screenshot file path / 截图文件路径
            
        Returns:
            Screenshot file path / 截图文件路径
        """
        try:
            if not self.page:
                log_error("页面未初始化")
                return None
            
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"screenshots/screenshot_{timestamp}.png"
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            await self.page.screenshot(path=filepath, full_page=True)
            log_info(f"截图已保存: {filepath}")
            
            return filepath
            
        except Exception as e:
            log_error(f"截图失败: {e}")
            return None


class BrowserScraperMixin:
    """
    Mixin class to add browser automation to scrapers
    混合类，为爬虫添加浏览器自动化功能
    """
    
    def __init__(self, *args, use_browser: bool = False, **kwargs):
        """
        Initialize with browser automation option
        使用浏览器自动化选项初始化
        
        Args:
            use_browser: Enable browser automation / 启用浏览器自动化
        """
        super().__init__(*args, **kwargs)
        self.use_browser = use_browser
        self.browser_automation = None
        if use_browser:
            self.browser_automation = BrowserAutomation()
    
    async def fetch_with_browser(self, url: str, wait_for: str = None, scroll: bool = False) -> Optional[str]:
        """
        Fetch page using browser automation
        使用浏览器自动化获取页面
        
        Args:
            url: Target URL / 目标 URL
            wait_for: Selector to wait for / 等待的选择器
            scroll: Enable scrolling / 启用滚动
            
        Returns:
            Page HTML content / 页面 HTML 内容
        """
        if not self.browser_automation:
            self.browser_automation = BrowserAutomation()
        
        try:
            if scroll:
                content = await self.browser_automation.get_page_with_scroll(url, wait_for=wait_for)
            else:
                content = await self.browser_automation.get_page_content(url, wait_for=wait_for)
            
            return content
            
        except Exception as e:
            log_error(f"浏览器获取页面失败: {e}")
            return None
        finally:
            if self.browser_automation:
                await self.browser_automation.close()


# Convenience functions / 便捷函数

async def scrape_with_browser(
    url: str,
    wait_for: str = None,
    scroll: bool = False,
    headless: bool = True,
    browser_type: str = "chromium"
) -> Optional[str]:
    """
    Convenience function to scrape with browser
    便捷函数，使用浏览器抓取
    
    Args:
        url: Target URL / 目标 URL
        wait_for: Selector to wait for / 等待的选择器
        scroll: Enable scrolling / 启用滚动
        headless: Run in headless mode / 无头模式运行
        browser_type: Browser type / 浏览器类型
        
    Returns:
        Page HTML content / 页面 HTML 内容
    """
    browser = BrowserAutomation(headless=headless, browser_type=browser_type)
    
    try:
        if scroll:
            content = await browser.get_page_with_scroll(url, wait_for=wait_for)
        else:
            content = await browser.get_page_content(url, wait_for=wait_for)
        
        return content
        
    finally:
        await browser.close()


def scrape_with_browser_sync(
    url: str,
    wait_for: str = None,
    scroll: bool = False,
    headless: bool = True,
    browser_type: str = "chromium"
) -> Optional[str]:
    """
    Synchronous wrapper for browser scraping
    浏览器抓取的同步包装器
    
    Args:
        url: Target URL / 目标 URL
        wait_for: Selector to wait for / 等待的选择器
        scroll: Enable scrolling / 启用滚动
        headless: Run in headless mode / 无头模式运行
        browser_type: Browser type / 浏览器类型
        
    Returns:
        Page HTML content / 页面 HTML 内容
    """
    return asyncio.run(scrape_with_browser(url, wait_for, scroll, headless, browser_type))
