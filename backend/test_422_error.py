#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("[TEST 1] 测试有效的应聘请求")
print("=" * 70)

payload_valid = {
    "candidate_id": 1,
    "job_id": 1,
    "notes": "测试"
}

print(f"请求数据: {json.dumps(payload_valid, indent=2)}")
resp = requests.post(f"{BASE_URL}/jobs/apply", json=payload_valid)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:300]}")

print("\n[TEST 2] 测试无效的应聘请求 (candidate_id 为 NaN/null)")
print("=" * 70)

# 模拟前端 parseInt(null) 的结果
payload_invalid_1 = {
    "candidate_id": None,  # JSON 中为 null
    "job_id": 1,
}

print(f"请求数据: {json.dumps(payload_invalid_1, indent=2)}")
resp = requests.post(f"{BASE_URL}/jobs/apply", json=payload_invalid_1)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:300]}")

print("\n[TEST 3] 测试无效的应聘请求 (缺少 job_id)")
print("=" * 70)

payload_invalid_2 = {
    "candidate_id": 1,
}

print(f"请求数据: {json.dumps(payload_invalid_2, indent=2)}")
resp = requests.post(f"{BASE_URL}/jobs/apply", json=payload_invalid_2)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:300]}")

print("\n[TEST 4] 测试无效的应聘请求 (candidate_id 为字符串)")
print("=" * 70)

payload_invalid_3 = {
    "candidate_id": "candidate_123",
    "job_id": 1,
}

print(f"请求数据: {json.dumps(payload_invalid_3, indent=2)}")
resp = requests.post(f"{BASE_URL}/jobs/apply", json=payload_invalid_3)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text[:300]}")
