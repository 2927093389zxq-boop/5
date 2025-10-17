"""
国际化(i18n)模块 - 多语言支持
Internationalization (i18n) Module - Multi-language support
"""
import json
import os
from typing import Dict, Optional


class I18n:
    """国际化管理器 / Internationalization Manager"""
    
    # 支持的语言 / Supported languages
    SUPPORTED_LANGUAGES = ['zh_CN', 'en_US']
    
    def __init__(self, config_dir: str = "config/i18n", default_lang: str = "zh_CN"):
        self.config_dir = config_dir
        self.current_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        
        # 加载所有语言包 / Load all language packs
        self._load_translations()
    
    def _load_translations(self):
        """加载翻译文件 / Load translation files"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        for lang in self.SUPPORTED_LANGUAGES:
            lang_file = os.path.join(self.config_dir, f"{lang}.json")
            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            else:
                self.translations[lang] = {}
    
    def set_language(self, lang: str):
        """设置当前语言 / Set current language"""
        if lang in self.SUPPORTED_LANGUAGES:
            self.current_lang = lang
        else:
            raise ValueError(f"不支持的语言 / Unsupported language: {lang}")
    
    def get_language(self) -> str:
        """获取当前语言 / Get current language"""
        return self.current_lang
    
    def t(self, key: str, **kwargs) -> str:
        """
        翻译文本 / Translate text
        
        Args:
            key: 翻译键 / Translation key
            **kwargs: 格式化参数 / Format parameters
        
        Returns:
            翻译后的文本 / Translated text
        """
        # 获取当前语言的翻译 / Get translation for current language
        translation = self.translations.get(self.current_lang, {}).get(key)
        
        # 如果没有翻译，尝试使用默认语言 / If no translation, try default language
        if translation is None and self.current_lang != 'zh_CN':
            translation = self.translations.get('zh_CN', {}).get(key)
        
        # 如果仍然没有，返回键本身 / If still no translation, return key itself
        if translation is None:
            translation = key
        
        # 格式化参数 / Format parameters
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass  # 忽略格式化错误 / Ignore format errors
        
        return translation
    
    def add_translation(self, lang: str, key: str, value: str):
        """
        添加翻译 / Add translation
        
        Args:
            lang: 语言代码 / Language code
            key: 翻译键 / Translation key
            value: 翻译值 / Translation value
        """
        if lang not in self.translations:
            self.translations[lang] = {}
        
        self.translations[lang][key] = value
    
    def save_translations(self):
        """保存翻译到文件 / Save translations to files"""
        for lang, translations in self.translations.items():
            lang_file = os.path.join(self.config_dir, f"{lang}.json")
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)


# 全局i18n实例 / Global i18n instance
_i18n_instance: Optional[I18n] = None


def get_i18n() -> I18n:
    """获取全局i18n实例 / Get global i18n instance"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """快捷翻译函数 / Shortcut translation function"""
    return get_i18n().t(key, **kwargs)


def set_language(lang: str):
    """设置语言 / Set language"""
    get_i18n().set_language(lang)


def get_language() -> str:
    """获取当前语言 / Get current language"""
    return get_i18n().get_language()
