# -*- coding: utf-8 -*-
"""测试各招聘网站的页面结构和CSS选择器"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


def create_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Edge(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    driver.set_page_load_timeout(30)
    return driver


def test_boss():
    print("=" * 60)
    print("测试 Boss 直聘")
    print("=" * 60)
    driver = create_driver()
    try:
        driver.get('https://www.zhipin.com/web/geek/job?query=前端工程师&city=101010100&page=1')
        time.sleep(8)
        print(f'Title: {driver.title}')
        print(f'URL: {driver.current_url}')
        src = driver.page_source
        print(f'Page length: {len(src)}')

        # 查找所有 job 相关的 class
        classes = set(re.findall(r'class="([^"]*(?:job|card|list|item|search)[^"]*)"', src, re.I))
        print(f'\nJob-related classes ({len(classes)}):')
        for c in sorted(classes)[:20]:
            print(f'  .{c}')

        # 尝试各种选择器
        tests = [
            '.job-card-wrapper', '.job-card-left', '.job-card-body',
            '.search-job-result', '.job-list-box', '[class*="job-card"]',
            'li.job-card-wrapper', '.job-title', '.job-name',
            '.info-public', '.company-name', '.salary',
        ]
        for sel in tests:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                print(f'\n  ✓ [{sel}] → {len(elems)} 个元素')
                for e in elems[:2]:
                    txt = e.text.strip()[:150]
                    if txt:
                        print(f'    text: {txt}')
                    # 打印 innerHTML 片段
                    html = e.get_attribute('innerHTML')[:200] if e.get_attribute('innerHTML') else ''
                    if html:
                        print(f'    html: {html[:150]}')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()


def test_51job():
    print("\n" + "=" * 60)
    print("测试 前程无忧 (51job)")
    print("=" * 60)
    driver = create_driver()
    try:
        driver.get('https://we.51job.com/pc/search?keyword=java&searchType=2&sortType=0&metro=')
        time.sleep(8)
        print(f'Title: {driver.title}')
        print(f'URL: {driver.current_url}')
        src = driver.page_source
        print(f'Page length: {len(src)}')

        classes = set(re.findall(r'class="([^"]*(?:job|card|list|item|search|position)[^"]*)"', src, re.I))
        print(f'\nJob-related classes ({len(classes)}):')
        for c in sorted(classes)[:20]:
            print(f'  .{c}')

        tests = [
            '.j_joblist', '.joblist-box', '.e', '.el',
            '.j_joblist .e', '[class*="joblist"]',
            '.jname', '.cname', '.sal', '.d_at',
            'a[href*="job"]', '.job-card', '.job-item',
            '.ick-table-box', '.j_openDetail',
            'div[sensorsname]', '[class*="ItemStyles"]',
        ]
        for sel in tests:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                print(f'\n  ✓ [{sel}] → {len(elems)} 个元素')
                for e in elems[:2]:
                    txt = e.text.strip()[:150]
                    if txt:
                        print(f'    text: {txt}')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()


def test_zhilian():
    print("\n" + "=" * 60)
    print("测试 智联招聘")
    print("=" * 60)
    driver = create_driver()
    try:
        driver.get('https://sou.zhaopin.com/?jl=530&kw=java&p=1')
        time.sleep(8)
        print(f'Title: {driver.title}')
        print(f'URL: {driver.current_url}')
        src = driver.page_source
        print(f'Page length: {len(src)}')

        classes = set(re.findall(r'class="([^"]*(?:job|card|list|item|search|position)[^"]*)"', src, re.I))
        print(f'\nJob-related classes ({len(classes)}):')
        for c in sorted(classes)[:20]:
            print(f'  .{c}')

        tests = [
            '.joblist-box__item', '.positionlist', '.sou-job-list',
            '[class*="joblist"]', '[class*="position"]',
            'a[href*="job"]', '.jobinfo', '.company-name',
            '[class*="JobCard"]', '[class*="jobCard"]',
        ]
        for sel in tests:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                print(f'\n  ✓ [{sel}] → {len(elems)} 个元素')
                for e in elems[:2]:
                    txt = e.text.strip()[:150]
                    if txt:
                        print(f'    text: {txt}')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()


if __name__ == '__main__':
    test_boss()
    test_51job()
    test_zhilian()
