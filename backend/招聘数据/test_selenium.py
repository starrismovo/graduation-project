# -*- coding: utf-8 -*-
"""快速测试 Selenium + Edge 能否抓取招聘网站"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


def create_driver():
    """创建反检测的 Edge 浏览器实例"""
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Edge(options=options)
    stealth_js = 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_js})
    return driver


def test_boss():
    driver = create_driver()

    try:
        print("=== 测试 Boss 直聘 ===")
        driver.get('https://www.zhipin.com/web/geek/job?query=前端工程师&city=101010100')
        time.sleep(8)
        print('Title:', driver.title)
        print('URL:', driver.current_url)
        src = driver.page_source
        print('Page length:', len(src))

        selectors = [
            '.job-card-wrapper',
            '.search-job-result .job-card-body',
            'a[href*="job_detail"]',
            '.job-list-box li',
            '[class*="job-card"]',
            '.job-name',
            '.search-job-result',
        ]
        for sel in selectors:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                print(f'  [{sel}] found {len(elems)} elements')
                for e in elems[:2]:
                    txt = e.text.strip()
                    if txt:
                        print(f'    -> {txt[:100]}')

    finally:
        driver.quit()


def test_51job():
    driver = create_driver()

    try:
        print("\n=== 测试 前程无忧 ===")
        url = 'https://we.51job.com/pc/search?keyword=前端工程师&searchType=2&sortType=0&metro='
        driver.get(url)
        time.sleep(8)
        print('Title:', driver.title)
        print('URL:', driver.current_url)

        # 多种选择器尝试
        selectors = [
            '.j_joblist',
            '.joblist-item',
            '.joblist-box',
            '.j_joblist .e',
            '[class*="joblist"]',
            '[class*="job_"]',
            '[class*="jname"]',
            'a[href*="job"]',
            '.el',
            '.ick',
        ]
        for sel in selectors:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                print(f'  [{sel}] found {len(elems)} elements')
                for e in elems[:3]:
                    txt = e.text.strip()
                    if txt:
                        print(f'    -> {txt[:120]}')

        # 打印页面部分 HTML 来分析结构
        src = driver.page_source
        print(f'\n  Page length: {len(src)}')
        # 找包含职位相关的 class
        import re
        classes = set(re.findall(r'class="([^"]*(?:job|position|item|card|list)[^"]*)"', src, re.I))
        print(f'  Job-related classes: {list(classes)[:15]}')

    finally:
        driver.quit()


def test_zhilian():
    driver = create_driver()

    try:
        print("\n=== 测试 智联招聘 ===")
        url = 'https://sou.zhaopin.com/?jl=530&kw=前端工程师&p=1'
        driver.get(url)
        time.sleep(8)
        print('Title:', driver.title)
        print('URL:', driver.current_url)

        selectors = [
            '.joblist-box__item',
            '.positionlist',
            '.sou-job-list',
            '[class*="joblist"]',
            '[class*="position"]',
            'a[href*="job"]',
        ]
        for sel in selectors:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                print(f'  [{sel}] found {len(elems)} elements')
                for e in elems[:3]:
                    txt = e.text.strip()
                    if txt:
                        print(f'    -> {txt[:120]}')

        src = driver.page_source
        print(f'\n  Page length: {len(src)}')
        import re
        classes = set(re.findall(r'class="([^"]*(?:job|position|item|card|list)[^"]*)"', src, re.I))
        print(f'  Job-related classes: {list(classes)[:15]}')

    finally:
        driver.quit()

    finally:
        driver.quit()


if __name__ == '__main__':
    test_51job()
    test_boss()
    test_zhilian()
