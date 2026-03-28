#!/usr/bin/env python3
"""
完整应聘流程验证脚本
Comprehensive Job Application Flow Verification Script

验证清单：
1. 创建新候选人
2. 测试 GET /jobs/ 获取岗位列表
3. 测试 POST /jobs/apply 应聘
4. 测试各种错误情况

使用方法:
python verify_complete_flow.py
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# 配置
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}

# 颜色编码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_test(test_name: str, result: bool, message: str = ""):
    status = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if result else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
    msg = f" - {message}" if message else ""
    print(f"  {status} {test_name}{msg}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

# ============================================================================
# 测试步骤
# ============================================================================

def test_1_create_candidate() -> Dict[str, Any]:
    """创建新候选人"""
    print_header("测试 1: 创建新候选人")
    
    payload = {
        "username": f"test_candidate_{datetime.now().timestamp()}",
        "password": "password123",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "role": "candidate"
    }
    
    print_info(f"发送请求到 POST /register")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload, headers=HEADERS, timeout=10)
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"候选人创建成功")
            print(f"  Response: {json.dumps(data, indent=2)}")
            
            if 'data' in data and 'id' in data['data']:
                return data['data']
            elif 'id' in data:
                return data
            else:
                print_error("Response 中找不到 id 字段")
                return None
        else:
            print_error(f"创建候选人失败: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return None

def test_2_get_jobs_list() -> Dict[str, Any]:
    """获取岗位列表"""
    print_header("测试 2: 获取岗位列表")
    
    print_info(f"发送请求到 GET /jobs/")
    
    try:
        response = requests.get(f"{BASE_URL}/jobs/", headers=HEADERS, timeout=10)
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"岗位列表获取成功")
            
            # 检查 data 结构
            if 'data' in data:
                jobs = data['data']
            else:
                jobs = data.get('jobs', []) if isinstance(data, dict) else data
            
            if isinstance(jobs, list):
                print_success(f"找到 {len(jobs)} 个岗位")
                
                if len(jobs) > 0:
                    first_job = jobs[0]
                    print_info(f"第一个岗位信息:")
                    print(f"  {json.dumps(first_job, indent=4, ensure_ascii=False)[:200]}...")
                    return first_job
                else:
                    print_error("岗位列表为空")
                    return None
            else:
                print_error(f"岗位列表格式错误: {type(jobs)}")
                return None
        else:
            print_error(f"获取岗位列表失败: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return None

def test_3_apply_for_job(candidate_id: int, job_id: int) -> bool:
    """应聘岗位"""
    print_header("测试 3: 应聘岗位")
    
    payload = {
        "candidate_id": candidate_id,
        "job_id": job_id
    }
    
    print_info(f"发送请求到 POST /jobs/apply")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/apply", json=payload, headers=HEADERS, timeout=10)
        print_info(f"响应状态码: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        
        # 预期成功 (200) 或重复申请 (400)
        if response.status_code == 200:
            print_success(f"应聘成功 (200)")
            return True
        elif response.status_code == 400:
            data = response.json()
            if 'detail' in data and '已经' in str(data['detail']):
                print_success(f"岗位已申请过 (400 - 预期)")
                return True
            else:
                print_test("应聘", False, f"400 错误: {data.get('detail', 'Unknown')}")
                return False
        elif response.status_code == 422:
            print_error(f"422 验证错误 - 这表示修复可能没有生效")
            data = response.json()
            print(f"  Details: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return False
        else:
            print_error(f"应聘失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return False

def test_4_apply_with_null_candidate() -> bool:
    """测试使用 null 候选人 ID 应聘（应该失败）"""
    print_header("测试 4: 验证 null 候选人 ID 会被拒绝 (422 错误)")
    
    payload = {
        "candidate_id": None,  # null
        "job_id": 1
    }
    
    print_info(f"发送请求到 POST /jobs/apply (with null candidate_id)")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/apply", json=payload, headers=HEADERS, timeout=10)
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 422:
            print_success(f"正确返回 422 (预期行为 - 无效的候选人 ID)")
            return True
        elif response.status_code == 400:
            print_success(f"返回 400 (也可接受 - 业务逻辑验证)")
            return True
        else:
            print_error(f"意外状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return False

def test_5_apply_with_string_candidate() -> bool:
    """测试使用字符串候选人 ID 应聘（应该失败）"""
    print_header("测试 5: 验证字符串候选人 ID 会被拒绝 (422 错误)")
    
    payload = {
        "candidate_id": "not_a_number",  # 字符串
        "job_id": 1
    }
    
    print_info(f"发送请求到 POST /jobs/apply (with string candidate_id)")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/apply", json=payload, headers=HEADERS, timeout=10)
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 422:
            print_success(f"正确返回 422 (预期行为 - 类型验证)")
            return True
        else:
            print_error(f"意外状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return False

def test_6_apply_with_invalid_job() -> bool:
    """测试使用无效岗位 ID 应聘（应该失败）"""
    print_header("测试 6: 验证无效岗位 ID 会被拒绝")
    
    payload = {
        "candidate_id": 1,
        "job_id": 999999  # 不存在的岗位
    }
    
    print_info(f"发送请求到 POST /jobs/apply (with invalid job_id)")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/apply", json=payload, headers=HEADERS, timeout=10)
        print_info(f"响应状态码: {response.status_code}")
        
        if response.status_code in [400, 404]:
            print_success(f"正确返回 {response.status_code} (预期行为)")
            return True
        else:
            print_error(f"意外状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"异常: {str(e)}")
        return False

# ============================================================================
# 主函数
# ============================================================================

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  应聘流程完整验证脚本 - Job Application Complete Test      ║")
    print("║  Comprehensive Verification Suite for Job Application Fix  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print_info(f"基础 URL: {BASE_URL}")
    print_info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ========== 测试执行 ==========
    
    # Test 1: 创建候选人
    candidate = test_1_create_candidate()
    if not candidate or not candidate.get('id'):
        print_error("无法创建候选人，终止测试")
        return
    candidate_id = candidate['id']
    print_success(f"使用候选人 ID: {candidate_id}")
    
    # Test 2: 获取岗位列表
    job = test_2_get_jobs_list()
    if not job or not job.get('id'):
        print_error("无法获取岗位列表，终止测试")
        return
    job_id = job['id']
    print_success(f"使用岗位 ID: {job_id}")
    
    # Test 3: 应聘岗位 (主要测试)
    success_apply = test_3_apply_for_job(candidate_id, job_id)
    
    # Test 4-6: 边界情况
    test_4_apply_with_null_candidate()
    test_5_apply_with_string_candidate()
    test_6_apply_with_invalid_job()
    
    # ========== 最终总结 ==========
    print_header("📊 测试总结")
    
    print_test("候选人创建", candidate is not None, f"ID: {candidate_id}")
    print_test("岗位列表获取", job is not None, f"ID: {job_id}")
    print_test("应聘流程主要测试", success_apply, "POST /jobs/apply 返回 200/400")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 所有关键测试完成！{Colors.ENDC}\n")
    
    print(f"{Colors.YELLOW}")
    print("📝 后续步骤:")
    print("  1. 在浏览器中刷新应聘界面: http://localhost:5173")
    print("  2. 选择一个岗位")
    print("  3. 点击'确认应聘'按钮")
    print("  4. 打开 DevTools (F12) Network 标签查看请求:")
    print("     - POST /jobs/apply 应该返回 200 OK (不是 422)")
    print(f"{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n测试被中断")
    except Exception as e:
        print_error(f"发生错误: {str(e)}")
