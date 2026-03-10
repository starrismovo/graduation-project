#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简历解析逻辑测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from routers.immersive_dialogue import _parse_resume_info, _extract_resume_text
from io import BytesIO

def test_parse_resume_info():
    """测试简历信息解析"""
    print("=" * 60)
    print("测试 1: 简历信息解析 (_parse_resume_info)")
    print("=" * 60)
    
    # 测试文本 1: 标准简历
    test_text_1 = """
    姓名: 张三
    邮箱: zhangsan@example.com
    电话: 13912345678
    学历: 本科
    
    技术栈: Python, Java, React, Django, MySQL, Docker
    
    工作经验:
    2023-至今: 高级工程师，负责系统架构设计
    2022-2023: 中级工程师，负责项目开发
    
    软技能特点: 
    - 沟通能力强，能够有效协调团队
    - 团队合作意识强，配合度高
    - 创新思维活跃，提出过多项改进方案
    - 善于解决问题，调试复杂bug
    - 具有一定领导能力，带领过小团队
    """
    
    result = _parse_resume_info(test_text_1)
    print("\n输入文本:")
    print(test_text_1)
    print("\n解析结果:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # 检查结果
    errors = []
    if result['name'] != '张三':
        errors.append(f"❌ 姓名提取错误: 期望 '张三', 得到 '{result['name']}'")
    if result['email'] != 'zhangsan@example.com':
        errors.append(f"❌ 邮箱提取错误: 期望 'zhangsan@example.com', 得到 '{result['email']}'")
    if result['phone'] != '13912345678':
        errors.append(f"❌ 电话提取错误: 期望 '13912345678', 得到 '{result['phone']}'")
    if result['education'] != '本科':
        errors.append(f"❌ 学历提取错误: 期望 '本科', 得到 '{result['education']}'")
    if not result['technical_skills']:
        errors.append(f"❌ 技能提取错误: 没有提取到任何技能")
    if not result['soft_skills']:
        errors.append(f"❌ 软技能提取错误: 没有提取到任何软技能")
    
    if errors:
        print("\n⚠️ 发现问题:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ 所有检查通过!")
    
    return len(errors) == 0

def test_empty_text():
    """测试空文本处理"""
    print("\n" + "=" * 60)
    print("测试 2: 空文本处理")
    print("=" * 60)
    
    result = _parse_resume_info("")
    print(f"空文本解析结果: name='{result['name']}'\n")
    
    if result['name'] == '未提取':
        print("✅ 空文本处理正确")
        return True
    else:
        print(f"❌ 空文本处理错误: 期望 '未提取', 得到 '{result['name']}'")
        return False

def test_error_text():
    """测试包含提示信息的文本"""
    print("\n" + "=" * 60)
    print("测试 3: 包含提示信息的文本处理")
    print("=" * 60)
    
    error_text = "【⚠️ OCR功能暂不可用】\n系统暂无法进行自动识别"
    result = _parse_resume_info(error_text)
    print(f"错误文本解析结果: name='{result['name']}'\n")
    
    if result['name'] == '未提取':
        print("✅ 错误文本处理正确")
        return True
    else:
        print(f"❌ 错误文本处理错误: 期望 '未提取', 得到 '{result['name']}'")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试 4: 边界情况")
    print("=" * 60)
    
    test_cases = [
        ("Name: 张三丰", "张三丰", "英文 Name 格式"),
        ("名字: 李四", "李四", "名字 而非 姓名"),
        ("姓名： 王五", "王五", "全角冒号"),
        ("姓名: 赵六a", "赵六a", "包含字母的名字"),
    ]
    
    all_pass = True
    for text, expected, description in test_cases:
        result = _parse_resume_info(text)
        if result['name'] == expected:
            print(f"✅ {description}: '{result['name']}'")
        else:
            print(f"❌ {description}: 期望 '{expected}', 得到 '{result['name']}'")
            all_pass = False
    
    return all_pass

if __name__ == "__main__":
    print("\n🧪 开始简历解析逻辑测试\n")
    
    results = []
    results.append(("简历信息解析", test_parse_resume_info()))
    results.append(("空文本处理", test_empty_text()))
    results.append(("错误文本处理", test_error_text()))
    results.append(("边界情况", test_edge_cases()))
    
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        sys.exit(0)
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
        sys.exit(1)
