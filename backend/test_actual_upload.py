#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试实际的简历上传功能
"""
import requests
import json
import time
from pathlib import Path

# 创建一个测试简历文本文件
test_resume_txt = """姓名: 张三
邮箱: zhangsan.dev@company.com
电话: 13812345678

教育经历
--------
学历: 本科 计算机科学与技术

工作经验
--------
2023-至今：高级工程师
  - 负责系统架构设计和优化
  - 使用 Python, Java, React 进行开发
  - 管理 MySQL, Redis 数据库

2021-2023：中级工程师  
  - 从事 Django Web 开发
  - 参与 Docker, Kubernetes 容器化工作
  - 部署到 AWS 云平台

技能与特长
--------
编程语言: Python, Java, JavaScript, C++, Go
框架: Django, FastAPI, React, Vue, Spring Boot
数据库: MySQL, MongoDB, PostgreSQL, Redis
工具: Docker, Kubernetes, Git, Jenkins
云平台: AWS, Alibaba Cloud, Docker Swarm

软技能
--------
- 沟通能力强，能够有效协调跨部门团队
- 团队合作意识强，配合度高，主动承担任务
- 创新思维活跃，提出过多项改进方案和技术创新
- 善于解决问题，能快速调试复杂程序bug
- 具有一定领导能力，已带领过3-5人小团队
- 学习能力强，快速掌握新技术和框架
"""

# 保存测试文件
test_file = Path("temp_resume_test.txt")
test_file.write_text(test_resume_txt, encoding='utf-8')

print("=" * 60)
print("测试简历上传API功能")
print("=" * 60)

try:
    # 准备上传
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'text/plain')}
        data = {}
        
        print(f"\n📤 上传测试文件: {test_file.name}")
        print(f"📝 文件内容预览:\n{test_resume_txt[:200]}...\n")
        
        # 发送请求到后端
        response = requests.post(
            'http://localhost:8000/assessment/immersive/upload-resume',
            files=files,
            params={'candidate_id': 'test_candidate_001'},  # 添加 candidate_id 参数
            timeout=10
        )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 上传成功!\n")
        
        # 显示完整的响应结构
        print("📋 完整响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 兼容不同的返回格式
        data = result.get('data', result)
        info = data.get('candidate_info', {})
        
        print("\n📊 解析结果:")
        print(f"  文件名: {data.get('filename')}")
        print(f"  文件大小: {data.get('file_size')} 字节")
        print(f"  提取方式: {data.get('extraction_method')}")
        
        if info:
            print(f"\n👤 候选人信息:")
            print(f"  姓名: {info.get('name')}")
            print(f"  邮箱: {info.get('email')}")
            print(f"  电话: {info.get('phone')}")
            print(f"  学历: {info.get('education')}")
        
        if 'technical_skills' in data:
            print(f"\n💻 技术技能: {', '.join(data['technical_skills'])}")
        
        if 'assessed_dimensions' in data:
            dims = data['assessed_dimensions']
            print(f"\n🎯 评估维度 ({len(dims)} 个):")
            # 处理维度可能是字符串或对象的情况
            for dim in dims[:5]:
                if isinstance(dim, dict):
                    print(f"  - {dim.get('dimension', dim)}: {dim.get('score', '未评分')} 分")
                else:
                    print(f"  - {dim}")
            if len(dims) > 5:
                print(f"  ... 还有 {len(dims) - 5} 个维度")
        
        # 检查关键信息是否提取正确
        print("\n🔍 验证提取结果:")
        if info:
            checks = [
                ("姓名", info.get('name') == "张三"),
                ("邮箱", "zhangsan.dev" in info.get('email', '')),
                ("电话", info.get('phone') == "13812345678"),
                ("学历", info.get('education') == "本科"),
                ("技能总数", len(data.get('technical_skills', [])) > 0),
                ("软技能数", len(info.get('soft_skills', [])) > 0),
            ]
            
            passed = 0
            for check_name, result_bool in checks:
                status = "✅" if result_bool else "❌"
                print(f"  {status} {check_name}")
                if result_bool:
                    passed += 1
            
            print(f"\n✅ 通过检查: {passed}/{len(checks)}")
            
    else:
        print(f"❌ 上传失败!")
        print(f"响应: {response.text[:200]}")

except requests.exceptions.ConnectionError:
    print("❌ 连接失败，后端服务未运行")
    print("   请确保后端运行: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
except Exception as e:
    print(f"❌ 发生错误: {e}")

finally:
    # 清理临时文件
    if test_file.exists():
        test_file.unlink()
        print("\n🧹 已清理临时文件")

print("\n" + "=" * 60)
