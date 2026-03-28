#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修补 Paddle 核心库中的 set_optimization_level 问题
"""

import os
import re
from pathlib import Path

def find_and_patch_paddle():
    """在 Paddle 源代码中找到并修复 set_optimization_level 调用"""
    
    try:
        import paddlepaddle as pd
        paddle_dir = Path(pd.__file__).parent.parent
        
        print(f"Paddle 安装目录: {paddle_dir}")
        
        # 寻找 inference 或 fluid 相关文件
        inference_files = list(paddle_dir.glob("paddlepaddle/inference.py")) if (paddle_dir / "paddlepaddle").exists() else []
        inference_files += list(paddle_dir.glob("paddlepaddle/fluid/**/*.py")) if (paddle_dir / "paddlepaddle/fluid").exists() else []
        inference_files += list(paddle_dir.glob("paddlepaddle/**/*.py"))
        
        print(f"找到 {len(inference_files)} 个可能相关的Python文件...")
        
        files_modified = 0
        found_count = 0
        
        # 优先检查几个关键文件
        priority_files = [
            paddle_dir / "paddlepaddle" / "inference.py",
            paddle_dir / "paddlepaddle" / "fluid" / "core.py",
            paddle_dir / "paddlepaddle" / "fluid" / "core_no_check.py",
            paddle_dir / "paddlepaddle" / "fluid" / "__init__.py",
        ]
        
        for py_file in priority_files + inference_files[:100]:
            if not py_file.exists():
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                if 'set_optimization_level' in content:
                    found_count += 1
                    print(f"\n✅ 找到: {py_file.relative_to(paddle_dir)}")
                    
                    # 修复：注释掉所有 set_optimization_level 调用
                    new_content = re.sub(
                        r'(\s*)(\w+\.set_optimization_level\([^)]*\))',
                        r'\1# PATCHED: \2  # Disabled for Paddle 2.6+ compatibility',
                        content,
                        flags=re.MULTILINE
                    )
                    
                    if new_content != content:
                        # 备份原文件
                        backup_file = py_file.with_suffix('.py.bak')
                        if not backup_file.exists():
                            backup_file.write_text(content, encoding='utf-8')
                            print(f"  备份: {backup_file.name}")
                        
                        # 保存修改
                        py_file.write_text(new_content, encoding='utf-8')
                        files_modified += 1
                        print(f"  ✅ 已修复")
                        
                        # 显示修改行数
                        old_lines = content.count('set_optimization_level')
                        new_lines = new_content.count('set_optimization_level')
                        print(f"  已禁用 {old_lines} 个调用")
            
            except Exception as e:
                pass
        
        print(f"\n{'='*60}")
        if found_count > 0:
            print(f"✅ 搜索完成: 在 {found_count} 个文件中找到问题")
            if files_modified > 0:
                print(f"✅ 修复完成: {files_modified} 个文件已修补")
                print(f"\n💡 已创建备份文件 (.bak)")
                print("\n请重启后端以应用更改:")
                print("  1. Ctrl+C 停止当前后端")
                print("  2. python main.py 重启")
                print("  3. 重新上传 PDF 文件测试")
            else:
                print("⚠️ 找到问题但无法修改")
            return files_modified > 0
        else:
            print("⚠️ 未找到 set_optimization_level 调用")
            print("❌ 可能的原因:")
            print("   - 问题出现在编译的 .so/.pyd 文件中，无法修改")
            print("   - 需要使用兼容的 Paddle 版本")
            return False
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = find_and_patch_paddle()
    exit(0 if success else 1)
