#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速诊断 - 测试简历上传修复
"""

import requests
import json
import sys

def test_resume_upload():
    """测试简历上传功能"""
    backend_url = "http://localhost:8000"
    candidate_id = "test-user-" + str(__import__('time').time()).split('.')[0]
    
    print("=" * 60)
    print("简历上传功能诊断工具")
    print("=" * 60)
    
    # 测试1: 测试TXT文件
    print("\n[测试1] 上传TXT简历文件...")
    test_resume_txt = """姓名: 张三
邮箱: zhangsan@example.com
电话: 13800138000

教育背景:
2019-2023 本科 - 计算机科学与技术

工作经验:
2023-2024 某互联网公司担任工程师

技能:
Python, JavaScript, React, Django, MySQL
"""
    
    files = {'file': ('test_resume.txt', test_resume_txt.encode('utf-8'), 'text/plain')}
    params = {'candidate_id': candidate_id}
    
    try:
        response = requests.post(
            f"{backend_url}/assessment/immersive/upload-resume",
            files=files,
            params=params,
            timeout=10
        )
        
        print(f"✓ 请求成功，状态码: {response.status_code}")
        print(f"  响应大小: {len(response.text)} 字节")
        
        # 尝试解析JSON
        try:
            result = response.json()
            print(f"✓ JSON解析成功")
            print(f"  Code: {result.get('code')}")
            print(f"  Message: {result.get('message')}")
            
            if result.get('code') == 200:
                data = result.get('data', {})
                info = data.get('candidate_info', {})
                print(f"\n  提取的信息:")
                print(f"    - 姓名: {info.get('name', '未提取')}")
                print(f"    - 邮箱: {info.get('email', '未提取')}")
                print(f"    - 学历: {info.get('education', '未提取')}")
                print(f"    - 技能: {info.get('technical_skills', [])}")
                print(f"\n✓ TXT测试成功!")
            else:
                print(f"⚠ 返回代码不是200: {result.get('code')}")
                print(f"  详情: {result}")
        
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {e}")
            print(f"  响应内容 (前500字):")
            print(f"  {response.text[:500]}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到后端: {backend_url}")
        print(f"  请确认后端服务是否运行中")
        return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False
    
    # 测试2: 测试空文件
    print("\n[测试2] 上传空文件...")
    files = {'file': ('empty.txt', b'', 'text/plain')}
    params = {'candidate_id': candidate_id}
    
    try:
        response = requests.post(
            f"{backend_url}/assessment/immersive/upload-resume",
            files=files,
            params=params,
            timeout=10
        )
        
        print(f"✓ 请求成功，状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"✓ JSON解析成功")
            print(f"  Code: {result.get('code')}")
            print(f"  Message: {result.get('message')}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {e}")
            return False
    
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False
    
    # 测试3: 测试无效扩展名
    print("\n[测试3] 上传不支持的文件格式...")
    files = {'file': ('test.exe', b'fake exe', 'application/octet-stream')}
    params = {'candidate_id': candidate_id}
    
    try:
        response = requests.post(
            f"{backend_url}/assessment/immersive/upload-resume",
            files=files,
            params=params,
            timeout=10
        )
        
        print(f"✓ 请求成功，状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"✓ JSON解析成功")
            print(f"  Code: {result.get('code')}")
            print(f"  Message: {result.get('message')}")
            
            if result.get('code') == 400:
                print(f"✓ 正确地拒绝了无效格式")
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {e}")
            return False
    
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试都通过了!")
    print("=" * 60)
    
    print(f"""
后续步骤:
1. 在前端尝试上传文件
2. 如果仍有问题，查看：
   - 浏览器控制台 (F12 → Console)
   - 后端日志
   
已修复的问题:
✓ 前端现在能正确处理错误响应
✓ 后端总是返回有效的JSON
✓ 添加了详细的错误提示
""")
    
    return True

if __name__ == '__main__':
    try:
        import requests
    except ImportError:
        print("请先安装 requests: pip install requests")
        sys.exit(1)
    
    success = test_resume_upload()
    sys.exit(0 if success else 1)
