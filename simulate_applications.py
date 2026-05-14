#!/usr/bin/env python3
"""
真实模拟用户投递 admin 账户下的招聘岗位
Simulate real users applying for jobs created by admin
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# 配置
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}

# 颜色编码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_test(test_name: str, result: bool, message: str = ""):
    status = f"{Colors.GREEN}✅ 通过{Colors.ENDC}" if result else f"{Colors.RED}❌ 失败{Colors.ENDC}"
    print(f"  {status} {test_name}")
    if message:
        print(f"     {Colors.CYAN}{message}{Colors.ENDC}")

def print_info(message: str):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

# ============================================================================
# 主测试流程
# ============================================================================

def main():
    """主函数"""
    
    print_header("真实投递模拟系统")
    
    # 第0步：登录获取 admin token
    print_info("第0步: 登录 admin 账户获取认证令牌...")
    admin_token = None
    headers_with_auth = HEADERS
    try:
        login_data = {"username": "admin", "password": "123456"}
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            login_result = response.json()
            admin_token = login_result.get("access_token")
            if admin_token:
                print_test("登录成功", True, f"Token: {admin_token[:20]}...")
                headers_with_auth = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
            else:
                print_error("登录失败：无法获取token")
                return
        else:
            print_error(f"登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print_error(f"登录失败: {str(e)}")
        return
    
    # 第1步：获取岗位列表
    print_info("\n第1步: 获取 admin 创建的岗位列表...")
    try:
        response = requests.get(f"{BASE_URL}/jobs/", headers=headers_with_auth, timeout=5)
        jobs = response.json() if response.status_code == 200 else []
        
        print_test("获取岗位列表", response.status_code == 200, f"获取 {len(jobs)} 个岗位")
        
        if not jobs:
            print_error("系统中没有岗位，请先用 HR 账户创建岗位")
            return
        
        # 显示所有岗位
        print("\n📋 可用岗位列表:\n")
        for job in jobs[:5]:  # 显示前5个
            print(f"  [{job.get('id', 'N/A')}] {job.get('name', 'N/A')}")
            print(f"      📍 {job.get('city', 'N/A')} | 💼 {job.get('company', 'N/A')}")
            print(f"      💰 {job.get('salary_min', 0)}-{job.get('salary_max', 0)}K")
            print(f"      创建者ID: {job.get('creator_id', 'N/A')}\n")
        
    except Exception as e:
        print_error(f"获取岗位列表失败: {str(e)}")
        print_info("确保后端服务正在运行: python -m uvicorn backend.main:app --reload")
        return
    
    # 第2步：获取候选人列表
    print_info("\n第2步: 获取候选人账户列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/users", 
            headers=headers_with_auth, 
            timeout=5
        )
        users = response.json() if response.status_code == 200 else []
        
        # 筛选非HR的候选人
        candidates = [u for u in users if not u.get('is_hr') and u.get('username') != 'admin']
        
        if not candidates:
            # 如果没有候选人，我们使用固定的候选人ID列表来投递
            print_info("自动创建/使用测试候选人账户进行投递")
            candidates = [
                {"id": 1, "username": "candidate1"},
                {"id": 2, "username": "candidate2"},
                {"id": 3, "username": "candidate3"},
                {"id": 4, "username": "candidate4"},
                {"id": 5, "username": "candidate5"},
            ]
        else:
            print_test("获取候选人列表", True, f"找到 {len(candidates)} 个候选人")
        
        print(f"\n👥 候选人列表:\n")
        for candidate in candidates[:5]:
            cid = candidate.get('id') or candidate.get('candidate_id')
            username = candidate.get('username') or f"candidate_{cid}"
            print(f"  [{cid}] {username}")
        
    except Exception as e:
        print_info(f"获取候选人列表失败，将使用默认候选人ID: {str(e)}")
        candidates = [
            {"id": i, "username": f"candidate{i}"}
            for i in range(1, 6)
        ]
    
    # 第3步：执行投递
    print_header("开始投递流程")
    
    if not jobs:
        print_error("没有可投递的岗位")
        return
    
    successful_applications = []
    failed_applications = []
    
    # 选择前3个岗位和前3个候选人进行投递
    jobs_to_apply = jobs[:3]
    candidates_to_apply = candidates[:3]
    
    for candidate in candidates_to_apply:
        candidate_id = candidate.get('id') or candidate.get('candidate_id')
        candidate_name = candidate.get('username') or f"candidate_{candidate_id}"
        
        print(f"\n👤 候选人: {candidate_name} (ID: {candidate_id})")
        print("-" * 50)
        
        for job in jobs_to_apply:
            job_id = job.get('id')
            job_name = job.get('name', 'N/A')
            
            # 构建投递请求
            apply_data = {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "notes": f"我很感兴趣这个职位，希望能有面试机会。- {candidate_name}"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/jobs/apply",
                    json=apply_data,
                    headers=headers_with_auth,
                    timeout=5
                )
                
                # 检查响应
                if response.status_code == 200:
                    result = response.json()
                    
                    # 验证响应结构
                    application_id = result.get('data', {}).get('id') if isinstance(result.get('data'), dict) else result.get('id')
                    
                    print(f"  ✅ 投递成功 → {job_name}")
                    print(f"     应聘记录ID: {application_id}")
                    
                    successful_applications.append({
                        "candidate_id": candidate_id,
                        "candidate_name": candidate_name,
                        "job_id": job_id,
                        "job_name": job_name,
                        "status": "success"
                    })
                else:
                    error_msg = response.json().get('detail', response.text)
                    print(f"  ❌ 投递失败 → {job_name}")
                    print(f"     错误: {error_msg}")
                    
                    failed_applications.append({
                        "candidate_id": candidate_id,
                        "job_id": job_id,
                        "error": str(error_msg)
                    })
                    
            except requests.exceptions.Timeout:
                print(f"  ❌ 超时 → {job_name}")
                failed_applications.append({
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "error": "Request timeout"
                })
            except Exception as e:
                print(f"  ❌ 错误 → {job_name}: {str(e)}")
                failed_applications.append({
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "error": str(e)
                })
    
    # 第4步：验证投递结果
    print_header("投递结果总结")
    
    print(f"✅ 成功投递: {len(successful_applications)} 份")
    for app in successful_applications:
        print(f"   • {app['candidate_name']} → {app['job_name']}")
    
    if failed_applications:
        print(f"\n❌ 失败投递: {len(failed_applications)} 份")
        for app in failed_applications:
            print(f"   • 候选人ID {app['candidate_id']} → 岗位ID {app['job_id']}")
            print(f"     错误: {app['error']}")
    
    # 第5步：验证投递是否已保存
    if successful_applications:
        print_header("验证投递数据")
        
        sample_candidate = successful_applications[0]['candidate_id']
        
        print_info(f"查询候选人 {sample_candidate} 的应聘记录...")
        try:
            response = requests.get(
                f"{BASE_URL}/jobs/applications/{sample_candidate}",
                headers=headers_with_auth,
                timeout=5
            )
            
            if response.status_code == 200:
                applications = response.json()
                if isinstance(applications, dict) and 'data' in applications:
                    applications = applications['data']
                
                print_test("获取应聘记录", True, f"候选人有 {len(applications) if isinstance(applications, list) else 'N/A'} 条应聘记录")
                
                if isinstance(applications, list):
                    print("\n📊 应聘记录详情:\n")
                    for app in applications[:3]:
                        print(f"   • 岗位ID: {app.get('job_id')}, 状态: {app.get('application_status')}")
                        print(f"     投递时间: {app.get('applied_at')}\n")
            else:
                print_test("获取应聘记录", False, response.json().get('detail', response.text))
                
        except Exception as e:
            print_error(f"验证投递数据失败: {str(e)}")
    
    print_header("完成")
    print(f"✅ 本次模拟投递完成")
    print(f"   • 总投递数: {len(successful_applications) + len(failed_applications)}")
    print(f"   • 成功: {len(successful_applications)}")
    print(f"   • 失败: {len(failed_applications)}")
    print()

if __name__ == "__main__":
    main()
