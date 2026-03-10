# -*- coding: utf-8 -*-
"""
本地 PaddleOCR 模型配置
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

# 禁用网络模型检查
os.environ['PADDLE_REPO'] = ''
os.environ['PADDLEOCR_HOME'] = str(Path.home() / ".paddleocr")

from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

def get_local_model_paths():
    """获取本地模型路径"""
    model_base = Path.home() / ".paddleocr" / "models"
    
    paths = {
        "det": str(model_base / "ch_PP-OCRv4_det_infer"),
        "rec": str(model_base / "ch_PP-OCRv4_rec_infer"),
        "cls": str(model_base / "ch_ppocr_mobile_v2.0_cls_infer"),  # ✅ 使用本地分类器
    }
    
    # 验证模型文件存在
    for model_type in ["det", "rec", "cls"]:
        path = paths[model_type]
        model_dir = Path(path)
        if not model_dir.exists():
            logger.warning(f"❌ {model_type}模型目录不存在: {path}")
        else:
            pdmodel = model_dir / "inference.pdmodel"
            if not pdmodel.exists():
                logger.warning(f"❌ {model_type}模型文件不完整: 缺失 inference.pdmodel")
            else:
                logger.info(f"✅ {model_type}模型就绪: {path}")
    
    return paths

def create_paddleocr(**kwargs):
    """创建使用本地模型的 PaddleOCR 实例
    
    Args:
        **kwargs: 其他 PaddleOCR 参数 (如 lang, use_angle_cls 等)
    
    Returns:
        PaddleOCR: 配置了本地模型的 OCR 实例
    """
    paths = get_local_model_paths()
    
    # 基础配置：仅使用 detection + recognition（禁用分类器以避免下载）
    # 注意：分类器模型可能版本不兼容，禁用它防止 PaddleOCR 下载官方模型
    paddleocr_config = {
        "det_model_dir": paths["det"],
        "rec_model_dir": paths["rec"],
        "lang": "ch",  # 中文
        "use_angle_cls": False,  # 禁用分类器，防止自动下载
    }
    
    # 合并用户参数
    paddleocr_config.update(kwargs)
    
    logger.info(f"🚀 初始化 PaddleOCR (本地模型 - det+rec only)")
    logger.info(f"   Det: {paths['det']}")
    logger.info(f"   Rec: {paths['rec']}")
    logger.info(f"   分类器: 禁用（防止下载）")
    logger.info(f"   其他参数: {kwargs}")
    
    try:
        ocr = PaddleOCR(**paddleocr_config)
        logger.info("✅ PaddleOCR 初始化成功")
        return ocr
    except TypeError as e:
        # 如果某个参数不支持，尝试简化
        logger.warning(f"⚠️ 参数不支持: {e}，尝试移除不兼容参数")
        # 只保留基础参数
        simple_config = {
            "det_model_dir": paths["det"],
            "rec_model_dir": paths["rec"],
            "lang": "ch",
        }
        try:
            ocr = PaddleOCR(**simple_config)
            logger.info("✅ PaddleOCR 初始化成功 (已简化参数)")
            return ocr
        except Exception as retry_e:
            logger.error(f"❌ PaddleOCR 初始化失败: {retry_e}")
            raise
    except Exception as e:
        logger.error(f"❌ PaddleOCR 初始化失败: {e}")
        raise
