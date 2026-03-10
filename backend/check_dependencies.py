#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查简历上传依赖库是否已正确安装
"""

import sys
import subprocess

def check_library(package_name, import_name=None):
    """检查单个库是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name:<20} - 已安装")
        return True
    except ImportError:
        print(f"✗ {package_name:<20} - 未安装")
        return False

def install_dependencies():
    """安装所有必需的依赖库"""
    packages_to_install = [
        'python-docx',
        'pdfplumber'
    ]
    
    print("\n" + "="*50)
    print("开始安装缺失的库...")
    print("="*50)
    
    for package in packages_to_install:
        print(f"\n安装 {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"✗ {package} 安装失败")

def main():
    print("="*50)
    print("简历上传依赖检查工具")
    print("="*50)
    print()
    
    # 检查核心依赖
    print("核心依赖库:")
    print("-"*50)
    
    core_libs = [
        ('FastAPI', 'fastapi'),
        ('SQLAlchemy', 'sqlalchemy'),
        ('Pydantic', 'pydantic'),
        ('python-dotenv', 'dotenv'),
    ]
    
    all_core_ok = all(check_library(name, import_name) for name, import_name in core_libs)
    
    # 检查简历处理依赖
    print("\n简历处理库 (文件解析):")
    print("-"*50)
    
    resume_libs = [
        ('python-docx', 'docx'),
        ('pdfplumber', 'pdfplumber'),
    ]
    
    missing_libs = []
    for package_name, import_name in resume_libs:
        if not check_library(package_name, import_name):
            missing_libs.append(package_name)
    
    print("\n" + "="*50)
    
    if all_core_ok:
        print("✓ 所有核心依赖已安装")
    else:
        print("✗ 部分核心依赖未安装，请运行: pip install -r requirements.txt")
    
    if missing_libs:
        print(f"\n✗ 缺失库: {', '.join(missing_libs)}")
        print(f"\n建议安装命令:")
        for lib in missing_libs:
            print(f"  pip install {lib}")
        
        response = input("\n是否现在安装这些库? (y/n): ").strip().lower()
        if response == 'y':
            install_dependencies()
    else:
        print("✓ 所有简历处理库已安装")
    
    print("\n" + "="*50)
    print("检查完成!")
    print("="*50)

if __name__ == '__main__':
    main()
