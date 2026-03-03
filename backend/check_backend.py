import time
import sys
import urllib.request
import json

print("等待后端启动...")
time.sleep(3)

try:
    req = urllib.request.Request('http://127.0.0.1:8000/')
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read().decode())
    print(f"✓ 后端已启动！")
    print(f"✓ 响应: {data}")
except Exception as e:
    print(f"✗ 后端未响应: {e}")
    sys.exit(1)
