#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索并修复 Paddle 中的 set_optimization_level 问题
"""

import sys
import os
from pathlib import Path

def main():
    venv_site_packages = Path(sys.executable).parent.parent / "Lib" / "site-packages"
    paddle_dir = venv_site_packages / "paddle"
    paddlepaddle_dir = venv_site_packages / "paddlepaddle"
    
    print(f"Python: {sys.executable}")
    print(f"Site-packages: {venv_site_packages}")
    print(f"Paddle dir (paddlepaddle): {paddlepaddle_dir}")
    
    # 搜索所有 Python 文件
    to_search = []
    if paddlepaddle_dir.exists():
        to_search = list(paddlepaddle_dir.glob("**/*.py"))
    if paddle_dir.exists():
        to_search += list(paddle_dir.glob("**/*.py"))
    
    print(f"\n找到 {len(to_search)} 个 Python 文件")
    
    files_with_problem = []
    
    # 逐个文件检查
    for py_file in to_search:
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if 'set_optimization_level' in content:
                files_with_problem.append((py_file, content))
                print(f"找到问题文件: {py_file.relative_to(venv_site_packages)}")
        except:
            pass
    
    if not files_with_problem:
        print("\n⚠️ 未在 Python 源代码中找到 set_optimization_level 调用")
        print("❌ 这个错误可能来自编译的 C++ 扩展 (.pyd/.so 文件)")
        print("\n可行的解决方案:")
        print("  1️⃣ 运行以下命令回退到兼容版本:")
        print("     pip install paddlepaddle==2.5.1 paddleocr==2.7.0.3")
        print("\n  2️⃣ 或使用 EasyOCR 代替（需要安装 pip install easyocr）")
        print("\n  3️⃣ 或在禁用优化的情况下运行:")
        print("     set PADDLE_PDX_ENABLE_ADVANCED_MODE=0")
        return 1
    
    # 修复所有文件
    files_fixed = 0
    for py_file, content in files_with_problem:
        # 注释掉 set_optimization_level 调用
        import re
        new_content = re.sub(
            r'(\s*)(\w+\.set_optimization_level)',
            r'\1# DISABLED_COMPATIBILITY: \2',
            content
        )
        
        if new_content != content:
            # 备份
            backup = py_file.with_suffix('.py.bak')
            if not backup.exists():
                backup.write_text(content, encoding='utf-8')
            
            # 保存修改
            py_file.write_text(new_content, encoding='utf-8')
            files_fixed += 1
            print(f"✅ 已修复: {py_file.relative_to(venv_site_packages)}")
    
    if files_fixed > 0:
        print(f"\n✅ 成功修复 {files_fixed} 个文件")
        print("\n请重启后端:")
        print("  1. Ctrl+C 停止后端")
        print("  2. python main.py 重启")
        print("  3. 重新测试 PDF 上传")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
