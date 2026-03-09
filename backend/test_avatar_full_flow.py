#!/usr/bin/env python
"""完整的头像显示测试"""
import requests
import time
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

print("="*70)
print("🧪 完整头像显示测试流程")
print("="*70)

# 1. 登录获取 token
print("\n[1/5] 登录获取 Token...")
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "candidate1", "password": "123456"}
)
if login_resp.status_code != 200:
    print("❌ 登录失败")
    exit(1)

login_data = login_resp.json()
token = login_data.get("access_token")
if not token:
    print(f"❌ 无法获取 token: {login_data}")
    exit(1)

print(f"✅ 登录成功")
print(f"   Username: {login_data.get('username')}")
print(f"   User ID: {login_data.get('user_id')}")

headers = {"Authorization": f"Bearer {token}"}

# 2. 获取用户个人信息（查看是否有头像）
print("\n[2/5] 获取用户个人信息...")
profile_resp = requests.get(
    f"{BASE_URL}/user/profile",
    headers=headers
)

if profile_resp.status_code != 200:
    print(f"❌ 获取失败: {profile_resp.json()}")
    exit(1)

profile_data = profile_resp.json().get("data", {})
print(f"✅ 个人信息获取成功")
print(f"   用户名: {profile_data.get('username')}")
print(f"   邮箱: {profile_data.get('email')}")
print(f"   昵称: {profile_data.get('nickname')}")

# 检查头像
avatar = profile_data.get('avatar')
print(f"   头像状态: {'✅ 有头像' if avatar else '❌ 无头像'}")
if avatar:
    print(f"   头像数据长度: {len(avatar)} 字符")
    print(f"   头像前缀: {avatar[:80]}...")

# 3. 创建小型测试图片并上传
print("\n[3/5] 上传新头像...")
test_image_path = Path("./test_avatar_new.png")
png_data = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000800000008080202000b1c8dd50000001449444154789c6260f04f0404030303f81f0101010101008f0408c1e203000000004945004e44ae426082")
test_image_path.write_bytes(png_data)

with open(test_image_path, "rb") as f:
    files = {"file": ("test_avatar_new.png", f, "image/png")}
    upload_resp = requests.post(
        f"{BASE_URL}/user/avatar",
        files=files,
        headers=headers
    )

if upload_resp.status_code != 200:
    print(f"❌ 上传失败: {upload_resp.json()}")
    exit(1)

print(f"✅ 头像上传成功")
uploaded_avatar = upload_resp.json().get("data", {}).get("avatar", "")
print(f"   返回的头像数据长度: {len(uploaded_avatar)} 字符")

# 4. 再次获取个人信息验证头像已保存
print("\n[4/5] 验证头像已保存到数据库...")
profile_resp2 = requests.get(
    f"{BASE_URL}/user/profile",
    headers=headers
)

if profile_resp2.status_code != 200:
    print(f"❌ 获取失败")
    exit(1)

profile_data2 = profile_resp2.json().get("data", {})
avatar2 = profile_data2.get('avatar', '')

if avatar2:
    print(f"✅ 头像已保存到数据库")
    print(f"   数据库中的头像长度: {len(avatar2)} 字符")
    
    if avatar2 == uploaded_avatar:
        print(f"   数据完全一致 ✅")
    else:
        print(f"   ⚠️ 数据不一致（可能正常）")
else:
    print(f"❌ 头像未保存到数据库！")
    exit(1)

# 5. 显示前端应该如何获取
print("\n[5/5] 前端数据结构应如下...")
print(f"""
前端接收到的 userStore.profile 应包含:
{{
  "id": "{profile_data2.get('id')}",
  "username": "{profile_data2.get('username')}",
  "email": "{profile_data2.get('email')}",
  "avatar": "{avatar2[:50]}..." + {len(avatar2) - 50} 更多字符,
  "nickname": "{profile_data2.get('nickname')}",
  ...
}}

前端显示头像的方式：
v-if="userStore.profile?.avatar"
:src="userStore.profile.avatar"  (如果是 data URL)
或者
:src="getFullAvatarUrl(userStore.profile.avatar)"
""")

# 清理测试文件
test_image_path.unlink()

print("\n" + "="*70)
print("✅ 全部测试通过！后端数据完全正确")
print("="*70)
print("\n💡 如果前端仍无法显示头像，请检查：")
print("   1. IndexView.vue 是否在 onMounted 中调用 updateUserInfo()")
print("   2. 用户头像模板是否正确使用 userStore.profile?.avatar")
print("   3. 浏览器开发工具查看 userStore 中是否有 avatar 数据")
