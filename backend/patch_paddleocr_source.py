#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接修复 PaddleOCR 源代码中的 set_optimization_level 问题
"""

import os
import re
from pathlib import Path

def find_and_patch_paddleocr():
    """在 PaddleOCR 源代码中找到并修复 set_optimization_level 调用"""
    
    try:
        import paddleocr
        paddle_dir = Path(paddleocr.__file__).parent
        
        print(f"PaddleOCR 目录: {paddle_dir}")
        
        # 递归查找所有 Python 文件
        files_to_check = list(paddle_dir.rglob("*.py"))
        print(f"检查 {len(files_to_check)} 个 Python 文件...")
        
        files_modified = 0
        
        for py_file in files_to_check:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # 查找 set_optimization_level 调用
                if 'set_optimization_level' in content:
                    print(f"\n找到: {py_file.relative_to(paddle_dir)}")
                    
                    # 无侵入式修复：用三引号注释掉调用
                    new_content = re.sub(
                        r'(\s*)(\w+\.set_optimization_level\([^)]*\))',
                        r'\1# DISABLED: \2  # Removed due to Paddle 2.6+ incompatibility',
                        content
                    )
                    
                    if new_content != content:
                        py_file.write_text(new_content, encoding='utf-8')
                        files_modified += 1
                        print(f"  ✅ 已修复")
                    
                    # 显示修改部分
                    lines = new_content.split('\n')
                    for i, line in enumerate(lines):
                        if 'set_optimization_level' in line:
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            print(f"  修改内容:")
                            for j in range(start, end):
                                prefix = "  >" if j == i else "   "
                                print(f"{prefix} {j+1}: {lines[j][:100]}")
            
            except Exception as e:
                pass
        
        print(f"\n{'='*60}")
        if files_modified > 0:
            print(f"✅ 修复完成: {files_modified} 个文件已修补")
            print("\n请重启后端以应用更改:")
            print("  1. Ctrl+C 停止当前后端")
            print("  2. python main.py 重启")
            print("  3. 重新上传 PDF 文件测试")
            return True
        else:
            print("⚠️ 未找到需要修复的代码")
            return False
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    find_and_patch_paddleocr()
