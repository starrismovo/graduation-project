#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试简历上传和解析功能
"""

import sys
import os
from pathlib import Path

# 确保能导入backend目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_extract_resume_text():
    """测试文本提取功能"""
    from routers.immersive_dialogue import _extract_resume_text
    
    print("="*50)
    print("测试文本提取功能")
    print("="*50)
    
    # 测试1: TXT格式
    print("\n[测试1] TXT文件提取:")
    txt_content = "姓名: 张三\n邮箱: zhangsan@example.com".encode('utf-8')
    result = _extract_resume_text(txt_content, '.txt')
    print(f"✓ TXT提取成功: {result[:50]}...")
    assert "张三" in result
    
    # 测试2: 不支持的格式
    print("\n[测试2] 图片文件处理:")
    img_content = b"fake image data"
    result = _extract_resume_text(img_content, '.jpg')
    print(f"✓ 图片处理成功: {result}")
    assert "暂不支持OCR" in result
    
    # 测试3: 未知格式
    print("\n[测试3] 未知格式处理:")
    unknown_content = b"some data"
    result = _extract_resume_text(unknown_content, '.unknown')
    print(f"✓ 未知格式处理成功: {result}")
    
    print("\n✓ 所有文本提取测试通过!")
    return True

def test_parse_resume_info():
    """测试简历信息解析功能"""
    from routers.immersive_dialogue import _parse_resume_info
    
    print("\n" + "="*50)
    print("测试简历信息解析功能")
    print("="*50)
    
    # 测试文本
    resume_text = """
    姓名: 王五
    邮箱: wangwu@example.com
    电话: 13800138000
    
    教育背景:
    本科 - 计算机科学与技术
    
    技能:
    - Python
    - Java
    - JavaScript
    - Django
    - React
    - MySQL
    
    工作经验:
    在某公司从事后端开发工作，主要使用Python和Django框架
    """
    
    print("\n[测试1] 解析简历信息:")
    result = _parse_resume_info(resume_text)
    
    print(f"  邮箱: {result['email']}")
    assert result['email'] == 'wangwu@example.com', f"邮箱提取失败: {result['email']}"
    
    print(f"  电话: {result['phone']}")
    assert result['phone'] == '13800138000', f"电话提取失败: {result['phone']}"
    
    print(f"  学历: {result['education']}")
    assert result['education'] == '本科', f"学历提取失败: {result['education']}"
    
    print(f"  技能: {result['technical_skills']}")
    assert 'Python' in result['technical_skills'], "Python未被识别"
    assert 'Java' in result['technical_skills'], "Java未被识别"
    
    print(f"  工作经验: {result['work_experience'][:50]}...")
    
    print("\n✓ 所有解析测试通过!")
    return True

def test_dependencies():
    """测试所有依赖库是否可用"""
    print("\n" + "="*50)
    print("测试依赖库可用性")
    print("="*50)
    
    dependencies = [
        ('FastAPI', 'fastapi'),
        ('SQLAlchemy', 'sqlalchemy'),
        ('Pydantic', 'pydantic'),
        ('python-docx', 'docx'),
        ('pdfplumber', 'pdfplumber'),
    ]
    
    missing = []
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✓ {name:<20} - 可用")
        except ImportError:
            print(f"✗ {name:<20} - 不可用")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  缺失库: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    else:
        print("\n✓ 所有依赖库都可用!")
        return True

def create_test_file():
    """创建测试文件"""
    test_dir = Path(__file__).parent / 'test_files'
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试TXT文件
    txt_file = test_dir / 'test_resume.txt'
    txt_file.write_text("""姓名: 李四
邮箱: lisi@qq.com
电话: 15900000000

教育背景:
硕士 - 计算机科学与技术

工作经验:
在互联网公司担任高级工程师

技能:
Python, JavaScript, MySQL, Redis, Docker
""", encoding='utf-8')
    
    print(f"\n✓ 创建测试文件: {txt_file}")
    return test_dir

if __name__ == '__main__':
    try:
        # 第一步: 测试依赖库
        if not test_dependencies():
            print("\n⚠️  部分依赖库不可用，请先安装")
            print("运行: python check_dependencies.py")
            sys.exit(1)
        
        # 第二步: 测试提取功能
        test_extract_resume_text()
        
        # 第三步: 测试解析功能
        test_parse_resume_info()
        
        # 第四步: 创建测试文件
        test_dir = create_test_file()
        
        print("\n" + "="*50)
        print("✓ 所有测试通过!")
        print("="*50)
        print(f"\n下一步:")
        print(f"1. 运行后端服务: python main.py")
        print(f"2. 测试文件位置: {test_dir}")
        print(f"3. 在前端上传文件进行完整测试")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
