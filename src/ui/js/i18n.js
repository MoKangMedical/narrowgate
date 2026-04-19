/**
 * 窄门 NarrowGate 国际化模块
 * 支持静态文本和动态内容的多语言切换
 */

// 当前语言
let currentLang = localStorage.getItem('lang') || 'zh';

// 语言配置数据
let i18nData = {};

// 初始化国际化
async function initI18n() {
    try {
        // 加载语言配置
        const response = await fetch('locales/i18n.json');
        if (!response.ok) {
            throw new Error('Failed to load language config');
        }
        i18nData = await response.json();
        
        // 更新页面内容
        updatePageContent();
        updateLangButton();
        
        console.log('I18n initialized successfully');
    } catch (error) {
        console.error('Failed to initialize i18n:', error);
        // 使用内置的回退配置
        initFallbackConfig();
    }
}

// 回退配置（当无法加载配置文件时使用）
function initFallbackConfig() {
    i18nData = {
        zh: {
            nav: { brand: '窄门 NarrowGate' },
            hero: { 
                title: '你要进窄门',
                cta: '开始灵魂审计 →'
            },
            common: {
                loading: '加载中...',
                error: '错误',
                success: '成功'
            }
        },
        en: {
            nav: { brand: 'NarrowGate' },
            hero: { 
                title: 'Enter the Narrow Gate',
                cta: 'Start Soul Audit →'
            },
            common: {
                loading: 'Loading...',
                error: 'Error',
                success: 'Success'
            }
        }
    };
    updatePageContent();
    updateLangButton();
}

// 切换语言
function toggleLanguage() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('lang', currentLang);
    updatePageContent();
    updateLangButton();
    
    // 触发自定义事件，通知其他组件语言已更改
    window.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { language: currentLang } 
    }));
}

// 设置特定语言
function setLanguage(lang) {
    if (lang === 'zh' || lang === 'en') {
        currentLang = lang;
        localStorage.setItem('lang', currentLang);
        updatePageContent();
        updateLangButton();
        
        window.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: currentLang } 
        }));
    }
}

// 更新页面静态内容
function updatePageContent() {
    if (!i18nData[currentLang]) return;
    
    // 更新所有带有data-i18n属性的元素
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        const value = getNestedValue(i18nData[currentLang], key);
        
        if (value && typeof value === 'string') {
            el.textContent = value;
        }
    });
    
    // 更新所有带有data-i18n-placeholder属性的元素
    const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    placeholderElements.forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const value = getNestedValue(i18nData[currentLang], key);
        
        if (value && typeof value === 'string') {
            el.placeholder = value;
        }
    });
    
    // 更新HTML lang属性
    document.documentElement.lang = currentLang === 'zh' ? 'zh-CN' : 'en-US';
}

// 更新语言切换按钮
function updateLangButton() {
    const btn = document.getElementById('lang-switch');
    if (btn) {
        btn.textContent = currentLang === 'zh' ? 'EN' : '中';
        btn.title = currentLang === 'zh' ? 'Switch to English' : '切换到中文';
    }
}

// 获取嵌套对象的值
function getNestedValue(obj, path) {
    const keys = path.split('.');
    let value = obj;
    
    for (const key of keys) {
        if (value && typeof value === 'object' && key in value) {
            value = value[key];
        } else {
            return null;
        }
    }
    
    return value;
}

// 获取翻译文本
function t(key, params = {}) {
    if (!i18nData[currentLang]) return key;
    
    let value = getNestedValue(i18nData[currentLang], key);
    
    if (!value) return key;
    
    // 替换参数
    if (typeof value === 'string' && Object.keys(params).length > 0) {
        Object.keys(params).forEach(param => {
            value = value.replace(new RegExp(`{${param}}`, 'g'), params[param]);
        });
    }
    
    return value;
}

// 获取当前语言
function getCurrentLanguage() {
    return currentLang;
}

// 检测浏览器语言
function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    return browserLang.startsWith('zh') ? 'zh' : 'en';
}

// 自动检测并设置语言
function autoDetectLanguage() {
    const savedLang = localStorage.getItem('lang');
    if (savedLang) {
        currentLang = savedLang;
    } else {
        currentLang = detectBrowserLanguage();
        localStorage.setItem('lang', currentLang);
    }
}

// 动态内容国际化函数

// 获取大师问候语
function getMasterGreeting(masterId) {
    const key = `masters.${masterId}.greeting`;
    return t(key);
}

// 获取审计维度名称
function getAuditDimensionName(dimensionKey) {
    const key = `audit.dimensions.${dimensionKey}`;
    return t(key);
}

// 获取通用文本
function getCommonText(textKey) {
    const key = `common.${textKey}`;
    return t(key);
}

// 获取训练周标题
function getTrainingWeekTitle(weekIndex) {
    const key = `training.weeks.${weekIndex}.title`;
    return t(key);
}

// 获取训练周描述
function getTrainingWeekDesc(weekIndex) {
    const key = `training.weeks.${weekIndex}.desc`;
    return t(key);
}

// 获取训练周项目
function getTrainingWeekItems(weekIndex) {
    const key = `training.weeks.${weekIndex}.items`;
    const items = getNestedValue(i18nData[currentLang], key);
    return items || [];
}

// 导出函数供外部使用
window.i18n = {
    init: initI18n,
    toggle: toggleLanguage,
    set: setLanguage,
    t: t,
    getCurrentLanguage: getCurrentLanguage,
    getMasterGreeting: getMasterGreeting,
    getAuditDimensionName: getAuditDimensionName,
    getCommonText: getCommonText,
    getTrainingWeekTitle: getTrainingWeekTitle,
    getTrainingWeekDesc: getTrainingWeekDesc,
    getTrainingWeekItems: getTrainingWeekItems
};

// 页面加载时自动初始化
document.addEventListener('DOMContentLoaded', () => {
    autoDetectLanguage();
    initI18n();
});

// 如果页面已经加载完成，立即初始化
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    autoDetectLanguage();
    initI18n();
}