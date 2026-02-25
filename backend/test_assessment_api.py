"""
评估系统 API 测试脚本
用于验证所有接口是否正常工作
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# 测试候选人 ID（对应初始化脚本中的数据）
TEST_CANDIDATE_ID = "cand_001"
TEST_RECORD_ID = 1
TEST_JOB_ID = 1

# ANSI 颜色代码
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    """打印测试标题"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")


def print_success(text: str):
    """打印成功消息"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """打印错误消息"""
    print(f"{RED}❌ {text}{RESET}")


def print_info(text: str):
    """打印信息"""
    print(f"{YELLOW}ℹ️  {text}{RESET}")


def test_endpoint(method: str, endpoint: str, expected_status: int = 200, data: Dict[str, Any] = None) -> bool:
    """
    测试单个接口
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PATCH":
            response = requests.patch(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print_error(f"未支持的方法: {method}")
            return False
        
        # 检查响应状态
        if response.status_code != expected_status:
            print_error(f"状态码错误: 期望 {expected_status}，实际 {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return False
        
        # 尝试解析 JSON
        result = response.json()
        
        # 检查 API 响应格式
        if "code" in result and "message" in result:
            if result["code"] == 200:
                print_success(f"{method} {endpoint}")
                return True
            else:
                print_error(f"API 返回错误代码: {result['code']} - {result.get('message', '')}")
                return False
        else:
            # 某些响应可能没有标准格式
            print_success(f"{method} {endpoint}")
            return True
            
    except requests.exceptions.ConnectionError:
        print_error(f"无法连接到服务器: {BASE_URL}")
        return False
    except json.JSONDecodeError:
        print_error(f"响应不是有效的 JSON")
        return False
    except Exception as e:
        print_error(f"错误: {str(e)}")
        return False


def test_portrait():
    """测试心理画像接口"""
    print_header("测试 1: 获取心理画像 (/assessment/portrait/{candidate_id})")
    
    endpoint = f"/assessment/portrait/{TEST_CANDIDATE_ID}"
    success = test_endpoint("GET", endpoint)
    
    if success:
        # 获取详细数据
        response = requests.get(f"{BASE_URL}{endpoint}")
        data = response.json()
        
        if data["data"]:
            print_info(f"返回 {len(data['data'])} 个特质评分:")
            for trait in data["data"]:
                print(f"  - {trait['name']}: {trait['score']}/10")
        else:
            print_info("候选人暂无评估数据（新用户）")
    
    return success


def test_history():
    """测试历史评估接口"""
    print_header("测试 2: 获取历史评估 (/assessment/history/{candidate_id})")
    
    endpoint = f"/assessment/history/{TEST_CANDIDATE_ID}"
    success = test_endpoint("GET", endpoint)
    
    if success:
        response = requests.get(f"{BASE_URL}{endpoint}")
        data = response.json()
        
        if data["data"]:
            print_info(f"返回 {len(data['data'])} 条历史记录:")
            for record in data["data"]:
                print(f"  - {record['job_title']} (匹配度: {record['match_score']}%)")
        else:
            print_info("候选人暂无历史记录")
    
    return success


def test_recommended_jobs():
    """测试推荐岗位接口"""
    print_header("测试 3: 获取推荐岗位 (/assessment/recommended-jobs/{candidate_id})")
    
    endpoint = f"/assessment/recommended-jobs/{TEST_CANDIDATE_ID}"
    success = test_endpoint("GET", endpoint)
    
    if success:
        response = requests.get(f"{BASE_URL}{endpoint}")
        data = response.json()
        
        if data["data"]:
            print_info(f"返回 {len(data['data'])} 个推荐岗位:")
            for job in data["data"]:
                print(f"  - {job['title']} ({job['department']}) - 匹配度: {job['match_score']}%")
        else:
            print_info("暂无推荐岗位")
    
    return success


def test_report():
    """测试报告详情接口"""
    print_header("测试 4: 获取评估报告 (/assessment/report/{record_id})")
    
    endpoint = f"/assessment/report/{TEST_RECORD_ID}"
    success = test_endpoint("GET", endpoint)
    
    if success:
        response = requests.get(f"{BASE_URL}{endpoint}")
        data = response.json()
        
        if "data" in data:
            report = data["data"]
            print_info(f"岗位: {report['job_title']}")
            print_info(f"匹配度: {report['match_score']}%")
            print_info(f"对话摘要: {report['conversation_summary'][:100]}...")
            
            if report.get("match_analysis"):
                print_info(f"优势: {', '.join(report['match_analysis']['strengths'][:2])}")
                print_info(f"改进空间: {', '.join(report['match_analysis']['gaps'][:2])}")
    
    return success


def test_create_assessment():
    """测试创建评估接口"""
    print_header("测试 5: 创建评估记录 (POST /assessment/records)")
    
    data = {
        "candidate_id": "cand_test",
        "job_id": TEST_JOB_ID
    }
    
    endpoint = "/assessment/records"
    success = test_endpoint("POST", endpoint, 200, data)
    
    return success


def test_update_assessment():
    """测试更新评估接口"""
    print_header("测试 6: 更新评估记录 (PATCH /assessment/records/{record_id})")
    
    data = {
        "match_score": 88.5,
        "assessment_status": "completed",
        "total_rounds": 30,
        "personality_traits": {
            "外向性": 7.5,
            "宜人性": 6.8,
            "尽责性": 8.9,
            "神经质": 3.2,
            "开放性": 8.1
        }
    }
    
    endpoint = f"/assessment/records/{TEST_RECORD_ID}"
    success = test_endpoint("PATCH", endpoint, 200, data)
    
    return success


def test_documentation():
    """测试是否可以访问 API 文档"""
    print_header("测试 7: API 文档 (GET /docs)")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print_success("访问 Swagger UI 文档")
            print_info("打开浏览器访问: http://localhost:8000/docs")
            return True
        else:
            print_error(f"文档访问失败 (状态码: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print_error("无法连接到服务器")
        return False


def run_all_tests():
    """运行所有测试"""
    print(f"\n{BLUE}{'#'*60}")
    print("# AI 智能面试系统 - 后端 API 测试套件")
    print(f"{'#'*60}{RESET}")
    print(f"📍 服务器地址: {BASE_URL}")
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 首先检查服务器连接
    print_header("预检查: 检查服务器连接")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"服务器正常运行: {response.json()['message']}")
        else:
            print_error("服务器响应异常")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"无法连接到 {BASE_URL}")
        print_info("请确保后端服务已启动: python -m uvicorn main:app --reload")
        return False
    
    # 运行测试
    tests = [
        ("心理画像", test_portrait),
        ("历史评估", test_history),
        ("推荐岗位", test_recommended_jobs),
        ("报告详情", test_report),
        ("创建评估（可选）", test_create_assessment),
        ("更新评估（可选）", test_update_assessment),
        ("API 文档", test_documentation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"测试 '{test_name}' 执行出错: {str(e)}")
            results[test_name] = False
    
    # 总结结果
    print_header("📊 测试结果总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print(f"\n{GREEN}🎉 所有测试通过！后端准备就绪{RESET}")
        return True
    else:
        print(f"\n{RED}⚠️  部分测试失败，请检查错误信息{RESET}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
