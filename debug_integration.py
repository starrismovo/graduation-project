#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前后端集成详细调试工具
"""

import requests
import json
from typing import Optional

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"

class APITester:
    """API测试工具"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def test_endpoint(self, method: str, path: str, data: Optional[dict] = None, 
                      json_data: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
        """测试API端点"""
        url = f"{self.base_url}{path}"
        
        try:
            if method.upper() == "GET":
                resp = self.session.get(url, headers=headers, timeout=5)
            elif method.upper() == "POST":
                if json_data:
                    resp = self.session.post(url, json=json_data, headers=headers, timeout=5)
                else:
                    resp = self.session.post(url, data=data, headers=headers, timeout=5)
            else:
                return {"error": f"不支持的方法: {method}"}
            
            return {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.json() if resp.text else None,
                "text": resp.text[:500] if resp.text else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def register_user(self, username: str, email: str, password: str, is_hr: bool = False) -> dict:
        """注册用户"""
        print(f"\n📝 注册用户: {username}")
        result = self.test_endpoint("POST", "/auth/register", data={
            "username": username,
            "email": email,
            "password": password,
            "is_hr": is_hr
        })
        self.print_result(result)
        return result
    
    def login_user(self, username: str, password: str) -> dict:
        """登录用户"""
        print(f"\n🔐 登录用户: {username}")
        result = self.test_endpoint("POST", "/auth/login", data={
            "username": username,
            "password": password
        })
        if result.get("status") == 200 and result.get("body"):
            self.token = result["body"].get("access_token")
            print(f"  Token 已获取: {self.token[:20]}...")
        self.print_result(result)
        return result
    
    def get_jobs(self) -> dict:
        """获取岗位列表"""
        print(f"\n🏢 获取岗位列表")
        result = self.test_endpoint("GET", "/jobs/")
        self.print_result(result)
        return result
    
    def get_home_data(self) -> dict:
        """获取首页数据"""
        print(f"\n🏠 获取首页数据")
        result = self.test_endpoint("GET", "/jobs/home")
        self.print_result(result)
        return result
    
    def print_result(self, result: dict):
        """打印结果"""
        if "error" in result:
            print(f"  ❌ 错误: {result['error']}")
        else:
            print(f"  状态码: {result.get('status')}")
            if result.get('body'):
                print(f"  响应: {json.dumps(result['body'], ensure_ascii=False, indent=2)[:300]}")

def main():
    print("""
    ╔════════════════════════════════════╗
    ║   前后端集成详细调试工具            ║
    ║                                    ║
    ║  后端地址: http://127.0.0.1:8000  ║
    ╚════════════════════════════════════╝
    """)
    
    tester = APITester(BACKEND_URL)
    
    print("\n" + "="*50)
    print("开始测试")
    print("="*50)
    
    # 测试各个端点
    tester.register_user("debuguser_001", "debug001@test.com", "Debugpass123")
    
    tester.login_user("debuguser_001", "Debugpass123")
    
    tester.get_jobs()
    
    tester.get_home_data()
    
    print("\n" + "="*50)
    print("✅ 调试测试完成")
    print("="*50)
    print(f"""
📌 快速参考：

后端API文档: {BACKEND_URL}/docs
前端应用: {FRONTEND_URL}

📝 常见问题排查：

1️⃣  如果看到 CORS 错误：
   - 检查后端的 main.py 中的 allow_origins 配置
   - 确保包含你的前端URL

2️⃣  如果看到 404 错误：
   - 访问 /docs 查看所有可用的API端点
   - 检查路由前缀是否正确

3️⃣  如果看到 500 错误：
   - 查看后端控制台的错误日志
   - 检查数据库连接是否正常

4️⃣  如果MySQL连接失败：
   - 确保MySQL服务正在运行: tasklist | findstr mysql
   - 检查 .env 文件中的数据库连接字符串

    """)

if __name__ == "__main__":
    main()
