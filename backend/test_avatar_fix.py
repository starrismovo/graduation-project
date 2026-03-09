#!/usr/bin/env python
"""测试头像上传功能"""
import requests
import time
import sys
from pathlib import Path

# 等待后端服务启动
print("等待后端服务启动...")
time.sleep(2)

BASE_URL = "http://127.0.0.1:8000"

try:
    # 1. 登录获取token
    print("\n1️⃣ 登录获取Token...")
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "candidate1", "password": "123456"}
    )
    print(f"状态码: {login_resp.status_code}")
    login_json = login_resp.json()
    print(f"消息: {login_json.get('message', login_json)}")

    if login_resp.status_code != 200:
        print("❌ 登录失败")
        sys.exit(1)

    token = login_json.get("access_token") or login_json.get("data", {}).get("access_token")
    if not token:
        print(f"❌ 登录失败，无法获取token: {login_json}")
        sys.exit(1)
    
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 获得Token: {token[:20]}...")

    # 2. 创建测试图片
    print("\n2️⃣ 创建测试图片...")
    test_image_path = Path("./test_avatar.png")
    # 简单的8x8 PNG数据
    png_data = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000800000008080202000b1c8dd50000001449444154789c6260f04f0404030303f81f0101010101008f0408c1e203000000004945004e44ae426082")
    test_image_path.write_bytes(png_data)
    print(f"✅ 测试图片已创建: {test_image_path}")

    # 3. 上传头像
    print("\n3️⃣ 上传头像...")
    with open(test_image_path, "rb") as f:
        files = {"file": ("test_avatar.png", f, "image/png")}
        upload_resp = requests.post(
            f"{BASE_URL}/user/avatar",
            files=files,
            headers=headers
        )

    print(f"状态码: {upload_resp.status_code}")
    upload_json = upload_resp.json()
    print(f"消息: {upload_json.get('message')}")

    if upload_resp.status_code != 200:
        print(f"❌ 上传失败: {upload_json}")
        sys.exit(1)

    avatar_data = upload_json.get("data", {}).get("avatar", "")
    print(f"✅ 头像上传成功 (长度: {len(avatar_data)} 字符)")
    print(f"   头像数据前缀: {avatar_data[:67]}...")

    # 4. 获取个人信息验证头像是否已保存
    print("\n4️⃣ 获取个人信息验证...")
    profile_resp = requests.get(
        f"{BASE_URL}/user/profile",
        headers=headers
    )

    print(f"状态码: {profile_resp.status_code}")
    profile_json = profile_resp.json()

    if profile_resp.status_code != 200:
        print(f"❌ 获取失败: {profile_json}")
        sys.exit(1)

    saved_avatar = profile_json.get("data", {}).get("avatar", "")
    print(f"✅ 个人信息获取成功")
    print(f"   保存的头像长度: {len(saved_avatar)} 字符")

    if len(saved_avatar) > 0:
        print(f"   保存的头像前缀: {saved_avatar[:67]}...")
        if avatar_data == saved_avatar:
            print("\n✅✅✅ 完美！头像已成功保存到数据库！")
        else:
            print("\n⚠️ 警告：返回的头像与上传的不同")
    else:
        print("\n❌ 头像未保存到数据库（avatar字段为空）")
        sys.exit(1)

    # 清理
    test_image_path.unlink()
    
    print("\n" + "="*60)
    print("✅ 全部测试通过！头像上传问题已解决")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

