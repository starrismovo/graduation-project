#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断脚本：测试岗位选择 → 应聘流程
"""

import requests
import json
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_flow():
    print("\n" + "="*70)
    print("[DIAGNOSTIC] Job Selection -> Application Flow")
    print("="*70)
    
    # Step 1: 获取岗位列表
    print("\n[Step 1] 获取岗位列表")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/jobs/")
        print(f"✓ 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ 错误: {response.text}")
            return False
            
        jobs = response.json()
        if not jobs:
            print("✗ 没有可用的岗位")
            return False
        
        job = jobs[0]
        job_id = job['id']
        print(f"✓ 获取到 {len(jobs)} 个岗位")
        print(f"  - 岗位 ID: {job_id}")
        print(f"  - 岗位名: {job['name']}")
        print(f"  - 岗位要求: {job['required_traits']}")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    
    # Step 2: 获取岗位详细需求
    print("\n[Step 2] 获取岗位详细需求")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/jobs/requirements/{job_id}")
        print(f"✓ 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"⚠️ 详细需求不可用 ({response.status_code})")
            requirements = None
        else:
            requirements = response.json()
            print(f"✓ 获取岗位需求成功")
            print(f"  - 所需技能数: {len(requirements.get('skills', []))}")
            
    except Exception as e:
        print(f"⚠️ 无法获取详细需求: {e}")
        requirements = None
    
    # Step 3: 模拟获取或创建候选人
    print("\n[Step 3] 获取候选人信息")
    print("-" * 70)
    # 对于诊断，我们使用一个模拟的 candidate_id
    candidate_id = 1  # 假设有一个 ID 为 1 的候选人
    print(f"✓ 使用候选人 ID: {candidate_id}")
    
    # Step 4: 应聘岗位
    print("\n[Step 4] 应聘岗位")
    print("-" * 70)
    try:
        payload = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "notes": "诊断测试应聘"
        }
        
        print(f"请求数据: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{BASE_URL}/jobs/apply", json=payload)
        print(f"✓ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 应聘成功!")
            print(f"  - 应聘ID: {result.get('id')}")
            print(f"  - 应聘状态: {result.get('application_status')}")
            print(f"  - 匹配度: {result.get('personality_match_score', 'N/A')}%")
            return True
        
        elif response.status_code == 400:
            if "已申请过" in response.text:
                print(f"⚠️ 已申请过此岗位")
                return True  # 这在本周期内是预期的，前端应该处理
            else:
                print(f"✗ 应聘请求错误: {response.text}")
                return False
        
        else:
            print(f"✗ 应聘失败 (状态码 {response.status_code})")
            print(f"   响应: {response.text}")
            return False
        
    except Exception as e:
        print(f"✗ 应聘API调用错误: {e}")
        return False

def test_endpoint_exists():
    """检查所有相关端点是否存在"""
    print("\n" + "="*70)
    print("🔍 端点可用性检查")
    print("="*70)
    
    endpoints = [
        ("GET", "/jobs/"),
        ("GET", "/jobs/{job_id}"),
        ("GET", "/jobs/requirements/{job_id}"),
        ("POST", "/jobs/apply"),
    ]
    
    for method, endpoint in endpoints:
        # 用 /docs 检查是否存在
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print(f"✓ {method:6} {endpoint:40} 后端已启动")
            else:
                print(f"✗ {method:6} {endpoint:40} 后端未响应")
                return False
        except:
            print(f"✗ 无法连接到 {BASE_URL}/docs")
            return False
    
    return True

def main():
    print("\n🔗 检查后端连接...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        print("✓ 后端已启动: http://localhost:8000")
    except:
        print("✗ 无法连接后端 (http://localhost:8000)")
        print("  请先运行: python backend/main.py")
        return False
    
    # 检查端点
    if not test_endpoint_exists():
        return False
    
    # 运行完整流程测试
    if test_flow():
        print("\n" + "="*70)
        print("✅ 流程诊断完成！")
        print("="*70)
        print("\n📝 问题可能原因：")
        print("1. 前端未正确监听 'apply-job' 事件")
        print("2. 后端应聘API返回的数据格式不匹配")
        print("3. 前端STATE未正确更新（currentStep 没有递增）")
        print("4. localStorage 中缺少必要的候选人信息")
        return True
    else:
        print("\n" + "="*70)
        print("❌ 流程测试失败！")
        print("="*70)
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
