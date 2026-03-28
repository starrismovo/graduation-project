#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速验证 API 更新"""

import sys
import time

print("等待后端启动...")
time.sleep(2)

try:
    import requests
    
    # 测试服务器连接
    print("\n✓ 正在连接到后端服务器...")
    response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
    print(f"✓ 服务器响应: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✅ 后端服务器正常运行！")
        print("\n可用的 API 文档: http://127.0.0.1:8000/docs")
        
        # 快速测试注册
        print("\n" + "="*60)
        print("快速测试: 注册新用户")
        print("="*60)
        
        import time
        ts = int(time.time() * 1000) % 100000
        
        register_data = {
            "username": f"test_user_{ts}",
            "email": f"test_{ts}@example.com",
            "password": "password123",
            "is_hr": False
        }
        
        reg_response = requests.post(
            "http://127.0.0.1:8000/auth/register",
            data=register_data,
            timeout=10
        )
        
        print(f"\nStatus: {reg_response.status_code}")
        print(f"Response: {reg_response.json()}")
        
        if reg_response.status_code == 200:
            response_data = reg_response.json()
            print(f"\n✅ 注册成功!")
            print(f"   - User ID: {response_data.get('user_id')}")
            print(f"   - User Type: {response_data.get('user_type')}")
        else:
            print(f"\n⚠️  注册完成，状态码: {reg_response.status_code}")
        
    else:
        print(f"\n❌ 服务器返回状态码: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ 无法连接到后端服务器")
    print("请确保后端已启动: python main.py")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ API 路由更新验证完成！")
print("="*60)
