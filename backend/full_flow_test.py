#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

# 创建新的候选人
print("[0] Create a new candidate...")
try:
    # 注册新候选人
    reg_resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": f"test_candidate_{int(__import__('time').time())}",
            "email": f"test_{int(__import__('time').time())}@example.com",
            "password": "test_password123",
            "is_hr": False
        }
    )
    
    if reg_resp.status_code == 200:
        user_data = reg_resp.json()
        candidate_id = user_data.get('id')
        print(f"[OK] Created candidate ID: {candidate_id}")
    else:
        print(f"[Skip] Could not create candidate: {reg_resp.status_code}")
        candidate_id = 1
except Exception as e:
    print(f"[Skip] Error creating candidate: {e}")
    candidate_id = 1

print(f"Using candidate ID: {candidate_id}")

# Get jobs
print("\n[1] Get available jobs...")
try:
    response = requests.get(f"{BASE_URL}/jobs/")
    print(f"Status: {response.status_code}")
    
    jobs = response.json()
    if jobs:
        job = jobs[0]
        print(f"[OK] Got {len(jobs)} jobs")
        print(f"  - Job ID: {job['id']}")
        print(f"  - Job name: {job['name']}")
        
        # Apply for the job
        print("\n[2] Apply for the job...")
        payload = {
            "candidate_id": candidate_id,
            "job_id": job['id'],
            "notes": "Test application from diagnostic"
        }
        
        resp = requests.post(f"{BASE_URL}/jobs/apply", json=payload)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print("[OK] Application successful!")
            print(f"  - Application ID: {result.get('id')}")
            print(f"  - Status: {result.get('application_status')}")
            print(f"  - Match score: {result.get('personality_match_score', 'N/A')}%")
            print("\n[SUCCESS] Full flow works!")
        else:
            print(f"Error: {resp.text[:200]}")
    else:
        print("[ERROR] No jobs found")
        
except Exception as e:
    print(f"[ERROR] {e}")
