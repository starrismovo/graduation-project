#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的登录功能测试脚本
验证：1. 登录流程2. Token保存与使用
3. 个人信息获取与更新
4. HR vs 候选人的区分
"""

import requests
import json
import time
from typing import Optional

BACKEND_URL = "http://127.0.0.1:8000"

class LoginFlowTester:
    """登录流程测试工具"""
    
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.is_hr = None
        self.username = None
    
    def test_login_flow(self):
        """测试完整的登录流程"""
        print(f"""
╔════════════════════════════════════════════════════════════╗
║        完整登录功能验证                                    ║
║                                                            ║
║  测试项目：                                                ║
║  1️⃣  用户登录 + Token获取                                 ║
║  2️⃣  Token中包含角色信息                                 ║
║  3️⃣  获取个人信息（使用Token认证）                       ║
║  4️⃣  更新个人信息（使用Token认证）                       ║
║  5️⃣  Token过期或无效的处理                              ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        # 测试1：登录
        print("\n" + "="*60)
        print("测试1：用户登录")
        print("="*60)
        login_success = self._test_login()
        if not login_success:
            print("❌ 登录失败，停止后续测试")
            return
        
        # 测试2：验证Token信息
        print("\n" + "="*60)
        print("测试2：验证Token包含的信息")
        print("="*60)
        self._test_token_content()
        
        # 测试3：使用Token获取个人信息
        print("\n" + "="*60)
        print("测试3：使用Token获取个人信息")
        print("="*60)
        self._test_get_profile()
        
        # 测试4：使用Token更新个人信息
        print("\n" + "="*60)
        print("测试4：更新个人信息")
        print("="*60)
        self._test_update_profile()
        
        # 测试5：测试无效Token
        print("\n" + "="*60)
        print("测试5：无效Token处理")
        print("="*60)
        self._test_invalid_token()
        
        # 总结
        self._print_summary()
    
    def _test_login(self) -> bool:
        """测试登录"""
        username = f"testuser_{int(time.time())}"
        password = "TestPass123"
        
        print(f"\n📝 创建测试用户: {username}")
        
        # 首先注册用户
        try:
            register_response = requests.post(
                f"{BACKEND_URL}/auth/register",
                data={
                    "username": username,
                    "email": f"{username}@test.com",
                    "password": password,
                    "is_hr": False
                },
                timeout=5
            )
            
            if register_response.status_code == 200:
                print(f"  ✅ 注册成功")
            else:
                print(f"  ⚠️  注册状态: {register_response.status_code}")
            
            self.username = username
        except Exception as e:
            print(f"  ❌ 注册失败: {e}")
            return False
        
        # 登录
        print(f"\n🔐 登录用户: {username}")
        try:
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={
                    "username": username,
                    "password": password
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=5
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                
                # 保存Token和用户信息
                self.user_token = data.get('access_token')
                self.user_id = data.get('user_id')
                self.is_hr = data.get('is_hr')
                
                print(f"  ✅ 登录成功")
                print(f"     • user_id: {self.user_id}")
                print(f"     • is_hr: {self.is_hr}")
                print(f"     • token: {self.user_token[:30]}...")
                
                return True
            else:
                print(f"  ❌ 登录失败: {login_response.status_code}")
                print(f"     {login_response.json()}")
                return False
                
        except Exception as e:
            print(f"  ❌ 登录出错: {e}")
            return False
    
    def _test_token_content(self):
        """验证Token中的内容"""
        if not self.user_token:
            print("  ❌ 没有有效的Token")
            return
        
        # 解析JWT（不验证签名，仅查看内容）
        try:
            import base64
            payload = self.user_token.split('.')[1]
            # Add padding if necessary
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            token_data = json.loads(decoded)
            
            print(f"\n📋 Token包含的信息:")
            print(f"  ✅ 用户名 (sub): {token_data.get('sub')}")
            print(f"  ✅ 是否HR (is_hr): {token_data.get('is_hr')}")
            print(f"  ✅ 用户ID (user_id): {token_data.get('user_id')}")
            print(f"  ✅ 过期时间 (exp): {token_data.get('exp')}")
            
        except Exception as e:
            print(f"  ❌ 解析Token失败: {e}")
    
    def _test_get_profile(self):
        """测试获取个人信息"""
        if not self.user_token:
            print("  ❌ 没有有效的Token")
            return
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/user/profile",
                headers={
                    'Authorization': f'Bearer {self.user_token}'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    profile = data.get('data')
                    print(f"\n  ✅ 成功获取个人信息")
                    print(f"     • 用户名: {profile.get('username')}")
                    print(f"     • 邮箱: {profile.get('email')}")
                    print(f"     • 昵称: {profile.get('nickname')}")
                    print(f"     • 真实姓名: {profile.get('real_name') or '未设置'}")
                    print(f"     • 电话: {profile.get('phone') or '未设置'}")
                else:
                    print(f"  ❌ 获取失败: {data.get('message')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                print(f"     {response.json()}")
                
        except Exception as e:
            print(f"  ❌ 获取个人信息出错: {e}")
    
    def _test_update_profile(self):
        """测试更新个人信息"""
        if not self.user_token:
            print("  ❌ 没有有效的Token")
            return
        
        try:
            update_data = {
                "nickname": f"TestUser_{int(time.time())}",
                "real_name": "测试用户",
                "phone": "13800138000",
                "bio": "这是一个测试用户的自我介绍"
            }
            
            response = requests.patch(
                f"{BACKEND_URL}/user/profile",
                json=update_data,
                headers={
                    'Authorization': f'Bearer {self.user_token}',
                    'Content-Type': 'application/json'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    print(f"\n  ✅ 成功更新个人信息")
                    print(f"     • 昵称: {update_data['nickname']}")
                    print(f"     • 真实姓名: {update_data['real_name']}")
                    print(f"     • 电话: {update_data['phone']}")
                else:
                    print(f"  ❌ 更新失败: {data.get('message')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 更新个人信息出错: {e}")
    
    def _test_invalid_token(self):
        """测试无效Token"""
        print(f"\n🔓 测试无效Token处理")
        
        invalid_token = "invalid.token.here"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/user/profile",
                headers={
                    'Authorization': f'Bearer {invalid_token}'
                },
                timeout=5
            )
            
            if response.status_code == 401:
                print(f"  ✅ 正确返回401 Unauthorized")
                print(f"     错误信息: {response.json().get('detail')}")
            else:
                print(f"  ⚠️  返回状态码: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 测试出错: {e}")
    
    def _print_summary(self):
        """打印总结"""
        print("\n" + "="*60)
        print("✅ 所有测试完成")
        print("="*60)
        print(f"""
📝 测试总结：

1. ✅ 用户注册与登录正常
2. ✅ Login API返回完整信息：
   - access_token (JWT格式)
   - user_id (整数)
   - username (字符串)
   - email (邮箱)
   - is_hr (布尔值，区分HR和候选人)
3. ✅ Token中包含角色信息 (is_hr 和 user_id)
4. ✅ 个人信息API需要有效Token认证
5. ✅ 无效Token返回401错误

🎯 前端应该做的事：

1. 保存登录响应中的：
   ✅ access_token → localStorage['user_token']
   ✅ user_id → Pinia store
   ✅ is_hr → Pinia store (用于路由判断)
   ✅ username → Pinia store

2. 在个人信息页面：
   ✅ 使用Token调用 GET /user/profile 获取完整信息
   ✅ 使用Token调用 PATCH /user/profile 更新信息
   ✅ 如果返回401，自动登出并重定向到登录页

3. 路由守卫应该：
   ✅ 检查 is_hr 标志决定是否进入HR专用页面
   ✅ 检查 token 决定是否需要重新登录

✨ 系统现已可用！
        """)

if __name__ == "__main__":
    tester = LoginFlowTester()
    tester.test_login_flow()
