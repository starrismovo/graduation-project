#!/usr/bin/env python3
"""测试GET /jobs端点"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("测试 GET /jobs/ 端点")
print("=" * 60)

try:
    response = requests.get(f"{BASE_URL}/jobs/")
    print(f"状态码: {response.status_code}")
    print(f"响应头: Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 成功获取 {len(data)} 个岗位")
        
        if data:
            job = data[0]
            print(f"\n第一个岗位详情:")
            print(f"  ID: {job['id']}")
            print(f"  名称: {job['name']}")
            print(f"  公司: {job['company']}")
            print(f"  文化要求: {job['required_traits']}")
            print(f"  文化要求类型: {type(job['required_traits']).__name__}")
            
            if isinstance(job['required_traits'], dict):
                print(f"\n  ✅ required_traits 是字典类型 (正确)")
            else:
                print(f"\n  ❌ required_traits 是 {type(job['required_traits']).__name__} 类型 (错误)")
    else:
        print(f"❌ 错误: {response.status_code}")
        print(f"响应: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到后端 (确保 python main.py 已启动)")
except Exception as e:
    print(f"❌ 错误: {e}")
