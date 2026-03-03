import os
import json
import ssl
import urllib.request

API_URL = os.getenv('ROAD2ALL_API_URL', 'https://api.road2all.com/v1/chat/completions')
API_KEY = os.getenv('ROAD2ALL_API_KEY')

if not API_KEY:
    print('ERROR: ROAD2ALL_API_KEY not set in environment')
    raise SystemExit(1)

payload = {
    "model": os.getenv('ROAD2ALL_MODEL','gpt4o'),
    "messages": [
        {"role": "system", "content": "你是用于测试的系统提示"},
        {"role": "user", "content": "请用一句话回答：你好"}
    ],
    "temperature": 0.2,
    "max_tokens": 64
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(API_URL, data=data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
})

context = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=context, timeout=30) as resp:
        status = resp.getcode()
        body = resp.read().decode('utf-8')
        print('STATUS:', status)
        print('BODY:', body)
except Exception as e:
    print('ERROR:', e)
    raise
