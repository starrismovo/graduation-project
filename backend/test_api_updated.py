#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试更新的 API 路由"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def print_response(title: str, response: requests.Response):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"测试: {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_register():
    """测试注册端点"""
    # 测试 HR 用户注册
    data = {
        "username": f"test_hr_{int(__import__('time').time() * 1000) % 10000}",
        "email": f"test_hr_{int(__import__('time').time() * 1000) % 10000}@example.com",
        "password": "password123",
        "is_hr": True
    }
    response = requests.post(f"{BASE_URL}/auth/register", data=data)
    print_response("HR 用户注册", response)
    
    # 测试候选人用户注册
    data = {
        "username": f"test_candidate_{int(__import__('time').time() * 1000) % 10000}",
        "email": f"test_candidate_{int(__import__('time').time() * 1000) % 10000}@example.com",
        "password": "password123",
        "is_hr": False
    }
    response = requests.post(f"{BASE_URL}/auth/register", data=data)
    print_response("候选人注册", response)
    return response.json().get("user_id")


def test_login():
    """测试登录端点"""
    data = {
        "username": "test_candidate_2722",  # 使用之前创建的用户（如果存在）
        "password": "password123"
    }
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=data
    )
    print_response("登录测试", response)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def test_get_profile(token: str):
    """测试获取个人信息"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    print_response("获取个人信息", response)


def test_update_profile(token: str):
    """测试更新个人信息"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nickname": "测试用户",
        "real_name": "张三",
        "age": 28,
        "education": "本科",
        "major": "计算机科学",
        "desired_job": "数据分析师",
        "experience_years": 3.5,
        "skills": ["Python", "SQL", "Tableau"],
        "bio": "热爱数据分析"
    }
    response = requests.patch(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json=data
    )
    print_response("更新个人信息", response)


def test_candidate_basic_info(candidate_id: int = 14):
    """测试候选人基本信息接口"""
    # 获取
    response = requests.get(f"{BASE_URL}/api/candidates/{candidate_id}/basic-info")
    print_response(f"获取候选人 {candidate_id} 基本信息", response)
    
    # 更新
    data = {
        "name": "李四",
        "age": 26,
        "education": "硕士",
        "major": "人工智能",
        "desired_job": "机器学习工程师",
        "experience_years": 2.0,
        "skills": ["Python", "TensorFlow", "PyTorch"]
    }
    response = requests.post(
        f"{BASE_URL}/api/candidates/{candidate_id}/basic-info",
        json=data
    )
    print_response(f"更新候选人 {candidate_id} 基本信息", response)


def main():
    """主函数"""
    print("开始测试更新的 API 路由...\n")
    
    try:
        # 1. 测试注册
        print("="*60)
        print("1. 测试注册端点")
        print("="*60)
        candidate_id = test_register()
        
        # 2. 测试登录
        print("\n" + "="*60)
        print("2. 测试登录端点")
        print("="*60)
        token = test_login()
        
        if token:
            # 3. 测试获取个人信息
            print("\n" + "="*60)
            print("3. 测试获取个人信息")
            print("="*60)
            test_get_profile(token)
            
            # 4. 测试更新个人信息
            print("\n" + "="*60)
            print("4. 测试更新个人信息（包含新字段）")
            print("="*60)
            test_update_profile(token)
        
        # 5. 测试候选人基本信息
        print("\n" + "="*60)
        print("5. 测试候选人基本信息接口")
        print("="*60)
        test_candidate_basic_info()
        
        print("\n" + "="*60)
        print("✅ 测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
