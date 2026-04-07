# -*- coding: utf-8 -*-
"""深度测试：提取实际岗位数据"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import json


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


def test_51job_extract():
    print("=" * 60)
    print("前程无忧 - 提取岗位数据")
    print("=" * 60)
    driver = create_driver()
    try:
        driver.get('https://we.51job.com/pc/search?keyword=java&searchType=2&sortType=0&metro=')
        time.sleep(8)

        # 用 JS 直接提取页面中所有岗位数据
        data = driver.execute_script("""
            var results = [];
            // 尝试方法1: .joblist 下的 .j_joblist
            var items = document.querySelectorAll('.joblist .job-item, .j_joblist .e, .joblist-box .e');
            if (items.length === 0) {
                // 尝试方法2: 通用选择器
                items = document.querySelectorAll('[class*="job-item"], [class*="joblist"] > div');
            }
            for (var i = 0; i < Math.min(items.length, 5); i++) {
                var el = items[i];
                results.push({
                    text: el.innerText.substring(0, 300),
                    html: el.innerHTML.substring(0, 500),
                    classes: el.className
                });
            }
            // 如果没找到，返回页面结构信息
            if (results.length === 0) {
                var body = document.body;
                var allDivs = body.querySelectorAll('div[class]');
                var classMap = {};
                for (var j = 0; j < allDivs.length; j++) {
                    var cls = allDivs[j].className;
                    if (cls.match(/job|list|item|card|position/i)) {
                        if (!classMap[cls]) {
                            classMap[cls] = {count: 0, text: allDivs[j].innerText.substring(0, 100)};
                        }
                        classMap[cls].count++;
                    }
                }
                return {found: false, classes: classMap};
            }
            return {found: true, count: items.length, items: results};
        """)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])

    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()


def test_zhilian_extract():
    print("\n" + "=" * 60)
    print("智联招聘 - 提取岗位数据")
    print("=" * 60)
    driver = create_driver()
    try:
        driver.get('https://www.zhaopin.com/sou/jl530/kw01L00O80EO062/p1')
        time.sleep(8)

        data = driver.execute_script("""
            var results = [];
            var items = document.querySelectorAll('.joblist-box__item, [class*="jobCard"], [class*="job-card"], [class*="position-item"]');
            if (items.length === 0) {
                items = document.querySelectorAll('[class*="search-result"] > div, [class*="content-list"] > div');
            }
            for (var i = 0; i < Math.min(items.length, 5); i++) {
                var el = items[i];
                results.push({
                    text: el.innerText.substring(0, 300),
                    html: el.innerHTML.substring(0, 500),
                    classes: el.className
                });
            }
            if (results.length === 0) {
                var body = document.body;
                var allDivs = body.querySelectorAll('div[class]');
                var classMap = {};
                for (var j = 0; j < allDivs.length; j++) {
                    var cls = allDivs[j].className;
                    if (cls.match(/job|list|item|card|position|result/i)) {
                        if (!classMap[cls]) {
                            classMap[cls] = {count: 0, text: allDivs[j].innerText.substring(0, 100)};
                        }
                        classMap[cls].count++;
                    }
                }
                return {found: false, classes: classMap};
            }
            return {found: true, count: items.length, items: results};
        """)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])

    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()


def test_boss_extract():
    print("\n" + "=" * 60)
    print("Boss直聘 - 提取岗位数据")
    print("=" * 60)
    driver = create_driver()
    try:
        driver.get('https://www.zhipin.com/web/geek/job?query=java&city=101010100&page=1')
        time.sleep(10)

        data = driver.execute_script("""
            var results = [];
            var items = document.querySelectorAll('.job-card-wrapper, [class*="job-card"], .recommend-result-job li, .job-recommend-result li');
            if (items.length === 0) {
                items = document.querySelectorAll('[class*="recommend-result"] li, [class*="recommend-result"] > div');
            }
            for (var i = 0; i < Math.min(items.length, 5); i++) {
                var el = items[i];
                results.push({
                    text: el.innerText.substring(0, 300),
                    html: el.innerHTML.substring(0, 500),
                    classes: el.className
                });
            }
            if (results.length === 0) {
                var body = document.body;
                var allDivs = body.querySelectorAll('div[class], li[class], ul[class]');
                var classMap = {};
                for (var j = 0; j < allDivs.length; j++) {
                    var cls = allDivs[j].className;
                    if (cls.match(/job|list|item|card|recommend|result/i)) {
                        if (!classMap[cls]) {
                            classMap[cls] = {count: 0, tag: allDivs[j].tagName, text: allDivs[j].innerText.substring(0, 80)};
                        }
                        classMap[cls].count++;
                    }
                }
                return {found: false, classes: classMap};
            }
            return {found: true, count: items.length, items: results};
        """)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])

    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()


if __name__ == '__main__':
    test_51job_extract()
    test_zhilian_extract()
    test_boss_extract()
