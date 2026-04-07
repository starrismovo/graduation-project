import requests

# 测试筛选选项API
r1 = requests.get('http://localhost:8000/jobs/filters')
print('=== /jobs/filters ===')
print(f'Status: {r1.status_code}')
if r1.ok:
    data = r1.json()
    cities = data.get('cities', [])
    categories = data.get('categories', [])
    print(f'Cities: {len(cities)} -> {cities[:5]}')
    print(f'Categories: {len(categories)} -> {categories[:5]}')

# 测试搜索API
r2 = requests.get('http://localhost:8000/jobs/search', params={'page': 1, 'page_size': 3})
print(f'\n=== /jobs/search ===')
print(f'Status: {r2.status_code}')
if r2.ok:
    data = r2.json()
    print(f'Total: {data.get("total", 0)}')
    for item in data.get('items', [])[:2]:
        print(f'  - {item["name"]} | {item["company"]} | {item["city"]} | {item.get("salary")}')

# 测试关键词搜索
r3 = requests.get('http://localhost:8000/jobs/search', params={'keyword': '工程师', 'page_size': 3})
print(f'\n=== keyword=工程师 ===')
print(f'Status: {r3.status_code}')
if r3.ok:
    data = r3.json()
    print(f'Total: {data.get("total", 0)}')
    for item in data.get('items', [])[:3]:
        print(f'  - {item["name"]} | {item["company"]} | {item["city"]}')
