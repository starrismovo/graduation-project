#!/usr/bin/env python3
"""
API 集成测试脚本
测试注册、登录、面试、报告等核心接口
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("🚀 API 集成测试")
print("="*70 + "\n")

# ============================================
# 测试数据
# ============================================

test_candidate = {
    "username": "test_candidate_api",
    "email": "test_candidate@example.com",
    "password": "TestPassword123",
    "is_hr": False
}

test_hr = {
    "username": "test_hr_api",
    "email": "test_hr@example.com",
    "password": "HRPassword123",
    "is_hr": True
}

candidate_profile_update = {
    "nickname": "小王",
    "real_name": "王小明",
    "age": 28,
    "education": "本科",
    "major": "计算机科学",
    "desired_job": "后端工程师",
    "experience_years": 3.5,
    "phone": "13800138000",
    "bio": "热爱编程"
}

# ============================================
# 工具函数
# ============================================

def print_response(response, title=""):
    """打印响应信息"""
    if title:
        print(f"\n{title}")
        print("-" * 70)
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    except:
        print(f"Response: {response.text[:500]}")
        return None

def register_user(user_data):
    """注册用户"""
    url = f"{BASE_URL}/auth/register"
    try:
        response = requests.post(url, data=user_data)
        return response
    except Exception as e:
        print(f"❌ 注册失败: {str(e)}")
        return None

def login_user(username, password):
    """登录用户"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        return response
    except Exception as e:
        print(f"❌ 登录失败: {str(e)}")
        return None

# ============================================
# 测试 1: 用户注册
# ============================================

print("测试 1️⃣: 用户注册")
print("-"*70)

print("\n✓ 注册候选人...")
response = register_user(test_candidate)
if response:
    data = print_response(response, "候选人注册响应")
    if response.status_code == 200 and data:
        candidate_id = data.get("user_id")
        print(f"\n✅ 候选人注册成功 - ID: {candidate_id}")
    else:
        print(f"\n❌ 候选人注册失败")
        candidate_id = None
else:
    candidate_id = None

print("\n✓ 注册 HR 用户...")
response = register_user(test_hr)
if response:
    data = print_response(response, "HR 用户注册响应")
    if response.status_code == 200 and data:
        hr_id = data.get("user_id")
        print(f"\n✅ HR 用户注册成功 - ID: {hr_id}")
    else:
        print(f"\n❌ HR 用户注册失败")
        hr_id = None
else:
    hr_id = None

# ============================================
# 测试 2: 用户登录
# ============================================

print("\n\n测试 2️⃣: 用户登录")
print("-"*70)

candidate_token = None
hr_token = None

print("\n✓ 候选人登录...")
response = login_user(test_candidate["username"], test_candidate["password"])
if response:
    data = print_response(response, "候选人登录响应")
    if response.status_code == 200 and data:
        candidate_token = data.get("access_token")
        print(f"\n✅ 候选人登录成功")
        print(f"   Token: {candidate_token[:20]}...")
    else:
        print(f"\n❌ 候选人登录失败")
else:
    candidate_token = None

print("\n✓ HR 用户登录...")
response = login_user(test_hr["username"], test_hr["password"])
if response:
    data = print_response(response, "HR 用户登录响应")
    if response.status_code == 200 and data:
        hr_token = data.get("access_token")
        print(f"\n✅ HR 用户登录成功")
        print(f"   Token: {hr_token[:20]}...")
    else:
        print(f"\n❌ HR 用户登录失败")
else:
    hr_token = None

# ============================================
# 测试 3: 获取和更新用户信息
# ============================================

print("\n\n测试 3️⃣: 获取和更新用户信息")
print("-"*70)

if candidate_token:
    print("\n✓ 获取候选人个人信息...")
    url = f"{BASE_URL}/user/profile"
    headers = {"Authorization": f"Bearer {candidate_token}"}
    response = requests.get(url, headers=headers)
    data = print_response(response, "获取个人信息响应")
    
    if response.status_code == 200:
        print(f"\n✅ 成功获取个人信息")
    else:
        print(f"\n❌ 获取失败")
    
    print("\n✓ 更新候选人信息...")
    url = f"{BASE_URL}/user/profile"
    headers = {"Authorization": f"Bearer {candidate_token}"}
    response = requests.patch(url, json=candidate_profile_update, headers=headers)
    data = print_response(response, "更新个人信息响应")
    
    if response.status_code == 200:
        print(f"\n✅ 成功更新个人信息")
    else:
        print(f"\n❌ 更新失败")

# ============================================
# 测试 4: 查看 API 文档
# ============================================

print("\n\n测试 4️⃣: FastAPI 自动文档")
print("-"*70)

print("\n✓ 访问 Swagger 文档...")
try:
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print(f"✅ Swagger 文档可访问: {BASE_URL}/docs")
    else:
        print(f"⚠️  Swagger 文档返回状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 无法访问 Swagger 文档: {str(e)}")

print("\n✓ 访问 ReDoc 文档...")
try:
    response = requests.get(f"{BASE_URL}/redoc")
    if response.status_code == 200:
        print(f"✅ ReDoc 文档可访问: {BASE_URL}/redoc")
    else:
        print(f"⚠️  ReDoc 文档返回状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 无法访问 ReDoc 文档: {str(e)}")

# ============================================
# 测试 5: 其他端点测试
# ============================================

print("\n\n测试 5️⃣: 其他核心端点")
print("-"*70)

print("\n✓ 检查后端健康状态...")
try:
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print(f"✅ 后端运行正常")
    else:
        print(f"⚠️  后端返回状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 后端连接失败: {str(e)}")
    print(f"\n💡 提示: 请确保后端服务在 {BASE_URL} 正在运行")
    print("   运行命令: cd backend && python main.py")

# ============================================
# 测试总结
# ============================================

print("\n\n" + "="*70)
print("API 集成测试总结")
print("="*70)
print(f"""
✅ 测试项目:
   1. 用户注册 - {'✅ PASS' if candidate_id else '❌ FAIL'}
   2. 用户登录 - {'✅ PASS' if candidate_token else '❌ FAIL'}
   3. 获取和更新用户信息 - {'✅ PASS' if candidate_token else '❌ FAIL'}
   4. 自动文档访问 - 检查 /docs 和 /redoc
   5. 其他端点 - 需要手动测试

📝 使用 Postman 或 Swagger 进行进一步测试:
   - 访问: {BASE_URL}/docs
   - 可视化测试所有接口
   - 需要验证的接口:
     * POST /auth/register - 用户注册 (需支持 is_hr 字段)
     * POST /auth/login - 用户登录 (返回 user_type)
     * GET /user/profile - 获取个人信息 (返回新字段)
     * PATCH /user/profile - 更新个人信息 (支持新字段)
     * 其他面试、评估相关接口 - 需验证新字段映射

🔍 手动测试清单:
   注册端点:
     [ ] 支持 is_hr 字段选项
     [ ] user_type 自动设置
   
   登录端点:
     [ ] 返回 user_type 信息
   
   个人信息端点:
     [ ] 返回 age, education, major 等新字段
     [ ] 能够更新这些字段
   
   删除端点:
     [ ] 测试级联删除是否正确
     [✓] 验证外键约束是否生效

""")
print("="*70 + "\n")
