import urllib.request
import json
import sys

try:
    req = urllib.request.Request('http://127.0.0.1:8000/')
    resp = urllib.request.urlopen(req, timeout=5)
    data = resp.read().decode()
    print('✓ 后端运行中')
    print('响应:', data)
except Exception as e:
    print('✗ 后端未响应:', e)
    sys.exit(1)

# 测试登录端点
try:
    payload = json.dumps({"username": "test", "password": "test"}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:8000/auth/login',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    resp = urllib.request.urlopen(req, timeout=5)
    print('✓ 登录端点存在')
    print('登录响应:', resp.read().decode())
except urllib.error.HTTPError as e:
    if e.code == 404:
        print('✗ 登录端点不存在 (/auth/login)')
    elif e.code == 422:
        print('✓ 登录端点存在 (422 = 参数验证失败)')
    else:
        print(f'✗ 登录失败: {e.code}')
except Exception as e:
    print('✗ 无法连接登录端点:', e)
