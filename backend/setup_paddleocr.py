#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PaddleOCR 模型预加载脚本
首次运行会下载并缓存OCR模型，之后离线使用也能工作
"""

import os
import sys
import time
from pathlib import Path

def setup_paddle_ocr():
    """初始化PaddleOCR并预加载模型"""
    
    print("=" * 60)
    print("🔧 PaddleOCR 模型预加载工具")
    print("=" * 60)
    
    # 设置环境变量（本地模式）
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
    os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'
    os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
    os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(Path.home() / ".paddleocr" / "models")
    os.environ['PADDLE_REPO'] = ''
    os.environ['PADDLEOCR_HOME'] = str(Path.home() / ".paddleocr")
    print("\n✅ 已设置离线模式环境变量")
    
    # 创建缓存目录
    paddle_home = os.path.join(os.path.expanduser("~"), ".paddleocr")
    os.makedirs(paddle_home, exist_ok=True)
    print(f"✅ 模型缓存目录: {paddle_home}")
    
    # 尝试导入
    print("\n📦 正在导入 PaddleOCR...")
    try:
        from paddleocr import PaddleOCR
        print("✅ PaddleOCR 库导入成功")
    except ImportError as e:
        print(f"❌ PaddleOCR 导入失败: {e}")
        print("请先安装: pip install paddleocr")
        return False
    
    # 初始化模型
    print("\n🚀 正在初始化 OCR 模型...")
    print("   使用本地模型（如果存在）或自动下载")
    
    try:
        start_time = time.time()
        
        # 中文识别模型
        print("\n   [1/1] 初始化中文识别模型...")
        try:
            # 使用最简单的本地模型配置
            ocr = PaddleOCR(
                det_model_dir=str(Path.home() / ".paddleocr" / "models" / "ch_PP-OCRv4_det_infer"),
                rec_model_dir=str(Path.home() / ".paddleocr" / "models" / "ch_PP-OCRv4_rec_infer")
            )
        except Exception:
            # 回退到默认参数
            ocr = PaddleOCR()
        
        elapsed = time.time() - start_time
        print(f"\n✅ 模型初始化成功！耗时: {elapsed:.1f} 秒")
        
        # 验证模型文件
        print(f"\n📁 检查模型文件...")
        model_dir = paddle_home
        if os.path.exists(model_dir):
            model_files = []
            for root, dirs, files in os.walk(model_dir):
                for file in files:
                    size_mb = os.path.getsize(os.path.join(root, file)) / (1024*1024)
                    model_files.append(f"   {os.path.relpath(os.path.join(root, file), paddle_home)}: {size_mb:.1f}MB")
            
            if model_files:
                print("✅ 已缓存的模型文件:")
                for f in model_files:
                    print(f)
                total_size = sum(os.path.getsize(os.path.join(root, file)) 
                               for root, dirs, files in os.walk(model_dir) 
                               for file in files) / (1024*1024)
                print(f"   总大小: {total_size:.1f}MB")
            else:
                print("⚠️  模型目录为空，可能下载失败")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 模型预加载完成!")
        print("=" * 60)
        print("\n现在可以:")
        print("1. 重启后端服务: python main.py")
        print("2. 上传扫描版PDF进行识别")
        print("3. 系统会使用缓存的离线模型")
        print("\n✨ 即使没有网络连接也能工作!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 模型初始化失败:")
        print(f"   {type(e).__name__}: {e}")
        
        # 检查是否是网络问题
        if "model hosting" in str(e) or "connection" in str(e).lower():
            print("\n⚠️  看起来是网络连接问题")
            print("   请尝试:")
            print("   1. 检查网络连接")
            print("   2. 使用代理或VPN访问国外资源")
            print("   3. 稍后重试")
        
        return False

if __name__ == "__main__":
    try:
        success = setup_paddle_ocr()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
