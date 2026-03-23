# -*- coding: utf-8 -*-
"""
本地 PaddleOCR 模型配置（最小化配置以避免版本兼容性问题）
确保所有 PaddleOCR 实例都使用本地模型，不会尝试下载
"""
import os
import logging
from pathlib import Path

# ⚠️ 必须在导入 PaddleOCR 之前设置这些环境变量
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(Path.home() / ".paddleocr" / "models")
os.environ['PADDLE_REPO'] = ''
os.environ['PADDLEOCR_HOME'] = str(Path.home() / ".paddleocr")
# 禁用可能导致兼容性问题的功能
os.environ['PADDLE_FLAGS'] = 'FLAGS_runtime_eager_delete=1'
os.environ['DISABLE_TRIE_OP'] = '1'

from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

def get_local_model_paths():
    """获取本地模型路径"""
    model_base = Path.home() / ".paddleocr" / "models"
    
    paths = {
        "det": str(model_base / "ch_PP-OCRv4_det_infer"),
        "rec": str(model_base / "ch_PP-OCRv4_rec_infer"),
    }
    
    # 验证模型文件存在
    for model_type in ["det", "rec"]:
        path = paths[model_type]
        model_dir = Path(path)
        if model_dir.exists():
            pdmodel = model_dir / "inference.pdmodel"
            if pdmodel.exists():
                logger.debug(f"✅ {model_type}模型就绪: {path}")
            else:
                logger.warning(f"⚠️ {model_type}模型文件不完整: 缺失 inference.pdmodel")
        else:
            logger.warning(f"⚠️ {model_type}模型目录不存在: {path}")
    
    return paths

def create_paddleocr(**kwargs):
    """创建使用本地模型的 PaddleOCR 实例（最小化配置）
    
    Args:
        **kwargs: 其他 PaddleOCR 参数
    
    Returns:
        PaddleOCR: 配置了本地模型的 OCR 实例
        
    Raises:
        Exception: 如果初始化失败
    """
    paths = get_local_model_paths()
    
    logger.info(f"🚀 初始化 PaddleOCR...")
    
    # 只使用必要的最小参数
    config = {
        "det_model_dir": paths["det"],
        "rec_model_dir": paths["rec"],
    }
    
    # 合并用户参数（用户参数优先级更低）
    config_final = config.copy()
    config_final.update(kwargs)
    
    try:
        logger.debug(f"初始化参数: {config_final}")
        ocr = PaddleOCR(**config_final)
        logger.info(f"✅ PaddleOCR 初始化成功")
        return ocr
    except Exception as e:
        logger.error(f"❌ PaddleOCR 初始化失败: {type(e).__name__}: {e}")
        raise
