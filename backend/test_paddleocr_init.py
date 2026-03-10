#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断脚本：检查 PaddleOCR 本地模型初始化
"""

import os
import sys
from pathlib import Path

# 设置所有环境变量
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(Path.home() / ".paddleocr" / "models")
os.environ['PADDLE_REPO'] = ''
os.environ['PADDLEOCR_HOME'] = str(Path.home() / ".paddleocr")

print("=" * 70)
print("PaddleOCR Local Model Diagnosis")
print("=" * 70)

# 1. 检查本地模型文件
print("\n[1] Checking local model files...")
model_base = Path.home() / ".paddleocr" / "models"
models = {
    "det": model_base / "ch_PP-OCRv4_det_infer",
    "rec": model_base / "ch_PP-OCRv4_rec_infer",
    "cls": model_base / "ch_ppocr_mobile_v2.0_cls_infer",
}

for name, path in models.items():
    if path.exists():
        pdmodel = path / "inference.pdmodel"
        if pdmodel.exists():
            print("  [OK] %s: %s" % (name, path))
            print("       -> inference.pdmodel: %d bytes" % pdmodel.stat().st_size)
        else:
            print("  [ERROR] %s: inference.pdmodel not found!" % name)
    else:
        print("  [ERROR] %s: path not found!" % name)

# 2. 导入 PaddleOCR
print("\n[2] Importing PaddleOCR...")
try:
    print("  Importing paddleocr...")
    from paddleocr import PaddleOCR
    print("  [OK] PaddleOCR imported successfully")
except ImportError as e:
    print("  [ERROR] Import error: %s" % e)
    sys.exit(1)
except Exception as e:
    print("  [ERROR] Other error: %s: %s" % (type(e).__name__, e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试初始化（仅本地模型）
print("\n[3] Initialize PaddleOCR (local models + classifier)...")
try:
    paddleocr_config = {
        "det_model_dir": str(models["det"]),
        "rec_model_dir": str(models["rec"]),
        "use_angle_cls": False,
        "use_textline_orientation": False,
        "lang": "ch",
    }
    
    print("  Config:")
    for k, v in paddleocr_config.items():
        print("    - %s: %s" % (k, v))
    
    print("\n  Initializing...")
    ocr = PaddleOCR(**paddleocr_config)
    print("  [OK] PaddleOCR initialized successfully!")
    
except Exception as e:
    print("  [ERROR] Initialization failed: %s" % e)
    print("\n  Trying without classifier...")
    
    try:
        paddleocr_config = {
            "det_model_dir": str(models["det"]),
            "rec_model_dir": str(models["rec"]),
            "lang": "ch",
        }
        ocr = PaddleOCR(**paddleocr_config)
        print("  [OK] PaddleOCR initialized (det + rec only)")
    except Exception as e2:
        print("  [ERROR] Still failed: %s" % e2)
        sys.exit(1)

print("\n" + "=" * 70)
print("Diagnosis complete")
print("=" * 70)
