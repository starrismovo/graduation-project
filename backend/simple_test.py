#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

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
        
        # Try to apply for the job
        print("\n[2] Try to apply for job...")
        payload = {
            "candidate_id": 1,
            "job_id": job['id'],
            "notes": "Test application"
        }
        
        resp = requests.post(f"{BASE_URL}/jobs/apply", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        if resp.status_code == 200:
            print("[OK] Application successful")
        elif resp.status_code == 400 and "already" in resp.text.lower():
            print("[OK] Already applied (expected)")
        else:
            print(f"[ERROR] Application failed")
    else:
        print("[ERROR] No jobs found")
        
except Exception as e:
    print(f"[ERROR] {e}")
