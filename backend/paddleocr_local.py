# -*- coding: utf-8 -*-
"""
本地 PaddleOCR 模型配置（延迟加载以避免兼容性问题）
"""
import os
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# 环境变量预设（在任何导入之前）
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(Path.home() / ".paddleocr" / "models")
os.environ['PADDLE_REPO'] = ''
os.environ['PADDLEOCR_HOME'] = str(Path.home() / ".paddleocr")
os.environ['FLAGS_use_cinn'] = '0'
os.environ['PADDLE_INFER_DEVICE_ID'] = '-1'
os.environ['FLAGS_disable_memory_optimize'] = '1'

# 实际的 PaddleOCR 导入将延迟到 create_paddleocr() 调用时

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
    """创建使用本地模型的 PaddleOCR 实例（延迟加载）
    
    Args:
        **kwargs: 其他 PaddleOCR 参数
    
    Returns:
        PaddleOCR: 配置了本地模型的 OCR 实例
        
    Raises:
        Exception: 如果初始化失败
    """
    # 延迟导入：只在实际使用时导入 PaddleOCR
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        logger.error(f"❌ PaddleOCR 导入失败: {e}")
        raise
    
    paths = get_local_model_paths()
    logger.info(f"🚀 初始化 PaddleOCR...")
    
    # 只使用必要的最小参数
    config = {
        "det_model_dir": paths["det"],
        "rec_model_dir": paths["rec"],
    }
    
    # 排除可能导致版本兼容性问题的参数
    excluded_params = [
        'optimization_level', 'ir_optim', 'tensorrt_engine_dir',
        'rec_algorithm', 'use_angle_cls',
    ]
    
    # 合并用户参数，但过滤掉有问题的参数
    config_final = config.copy()
    for key, value in kwargs.items():
        if key not in excluded_params:
            config_final[key] = value
        else:
            logger.debug(f"⚠️ 跳过参数: {key}")
    
    try:
        ocr = PaddleOCR(**config_final)
        logger.info(f"✅ PaddleOCR 初始化成功")
        return ocr
    except ValueError as e:
        if "Unknown argument" in str(e):
            logger.warning("⚠️ 重试使用最小化配置...")
            try:
                config_minimal = {"det_model_dir": paths["det"], "rec_model_dir": paths["rec"]}
                ocr = PaddleOCR(**config_minimal)
                logger.info(f"✅ PaddleOCR 初始化成功 (最小化)")
                return ocr
            except Exception as retry_err:
                logger.error(f"❌ 最小化失败: {retry_err}")
                raise
        raise
    except AttributeError as e:
        logger.error(f"❌ PaddleOCR 版本兼容性问题: {e}")
        if "set_optimization_level" in str(e):
            logger.info("💡 建议升级 paddlepaddle 或 paddleocr")
        raise
    except Exception as e:
        logger.error(f"❌ PaddleOCR 初始化失败: {type(e).__name__}: {e}")
        raise
