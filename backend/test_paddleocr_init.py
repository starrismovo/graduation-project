#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试 PaddleOCR 初始化"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("导入 paddleocr_local...")
    from paddleocr_local import create_paddleocr
    
    logger.info("初始化 PaddleOCR...")
    ocr = create_paddleocr()
    
    logger.info("✅✅✅ PaddleOCR 初始化成功！")
    sys.exit(0)
    
except AttributeError as e:
    if "set_optimization_level" in str(e):
        logger.error(f"❌ 仍然存在 set_optimization_level 问题: {e}")
    else:
        logger.error(f"❌ AttributeError: {e}")
    sys.exit(1)
    
except Exception as e:
    logger.error(f"❌ 初始化失败: {type(e).__name__}: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
