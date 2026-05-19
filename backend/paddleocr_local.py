# -*- coding: utf-8 -*-
"""
本地 PaddleOCR 模型配置（延迟加载以避免兼容性问题）
"""
import os
import logging
import sys
import threading
from pathlib import Path

logger = logging.getLogger(__name__)
_OCR_INSTANCE = None
_OCR_INIT_LOCK = threading.Lock()

# 环境变量预设（在任何导入之前）
OCR_CACHE_DIR = Path(__file__).resolve().parent / ".ocr_cache"
PADDLEX_CACHE_DIR = OCR_CACHE_DIR / "paddlex"
PADDLEOCR_HOME_DIR = OCR_CACHE_DIR / "paddleocr"
PADDLEOCR_MODEL_DIR = PADDLEOCR_HOME_DIR / "models"

for cache_dir in (PADDLEX_CACHE_DIR, PADDLEOCR_HOME_DIR, PADDLEOCR_MODEL_DIR):
    cache_dir.mkdir(parents=True, exist_ok=True)

os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
os.environ['PADDLE_PDX_CACHE_HOME'] = str(PADDLEX_CACHE_DIR)
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(PADDLEOCR_MODEL_DIR)
os.environ['PADDLEOCR_HOME'] = str(PADDLEOCR_HOME_DIR)
os.environ['FLAGS_use_cinn'] = '0'
os.environ['PADDLE_INFER_DEVICE_ID'] = '-1'
os.environ['FLAGS_disable_memory_optimize'] = '1'
os.environ['PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT'] = 'False'
os.environ['PADDLE_PDX_DISABLE_MKLDNN_MODEL_BL'] = 'True'

# 实际的 PaddleOCR 导入将延迟到 create_paddleocr() 调用时

def get_local_model_paths():
    """获取本地模型路径"""
    model_base = PADDLEOCR_MODEL_DIR
    
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
                logger.info(f"{model_type}旧版本地模型文件不完整: 缺失 inference.pdmodel")
        else:
            logger.info(f"{model_type}旧版本地模型目录不存在: {path}")
    
    return paths

def _has_inference_model(model_dir: str) -> bool:
    model_path = Path(model_dir)
    return (
        (model_path / "inference.pdmodel").exists()
        or (model_path / "inference.yml").exists()
    )

def create_paddleocr(**kwargs):
    """返回全局复用的 PaddleOCR 实例，避免并发请求重复初始化模型。"""
    global _OCR_INSTANCE

    if _OCR_INSTANCE is not None:
        logger.info("复用已初始化的 PaddleOCR 实例")
        return _OCR_INSTANCE

    with _OCR_INIT_LOCK:
        if _OCR_INSTANCE is not None:
            logger.info("复用已初始化的 PaddleOCR 实例")
            return _OCR_INSTANCE
        return _create_paddleocr_unlocked(**kwargs)


def _create_paddleocr_unlocked(**kwargs):
    """创建使用本地模型的 PaddleOCR 实例（延迟加载）
    
    Args:
        **kwargs: 其他 PaddleOCR 参数
    
    Returns:
        PaddleOCR: 配置了本地模型的 OCR 实例
        
    Raises:
        Exception: 如果初始化失败
    """
    global _OCR_INSTANCE

    if _OCR_INSTANCE is not None:
        logger.info("复用已初始化的 PaddleOCR 实例")
        return _OCR_INSTANCE

    # 延迟导入：只在实际使用时导入 PaddleOCR
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        logger.error(f"❌ PaddleOCR 导入失败: {e}")
        raise
    
    paths = get_local_model_paths()
    logger.info(f"🚀 初始化 PaddleOCR...")
    
    import inspect

    init_params = inspect.signature(PaddleOCR.__init__).parameters
    config = {
        "lang": kwargs.pop("lang", "ch"),
        "use_doc_orientation_classify": kwargs.pop("use_doc_orientation_classify", False),
        "use_doc_unwarping": kwargs.pop("use_doc_unwarping", False),
        "use_textline_orientation": kwargs.pop("use_textline_orientation", False),
    }

    if "text_detection_model_name" in init_params:
        config["text_detection_model_name"] = kwargs.pop(
            "text_detection_model_name",
            "PP-OCRv5_mobile_det",
        )
    if "text_recognition_model_name" in init_params:
        config["text_recognition_model_name"] = kwargs.pop(
            "text_recognition_model_name",
            "PP-OCRv5_mobile_rec",
        )
    if "text_det_limit_side_len" in init_params:
        config["text_det_limit_side_len"] = kwargs.pop("text_det_limit_side_len", 960)
    if "text_det_limit_type" in init_params:
        config["text_det_limit_type"] = kwargs.pop("text_det_limit_type", "max")
    if "text_recognition_batch_size" in init_params:
        config["text_recognition_batch_size"] = kwargs.pop("text_recognition_batch_size", 8)

    if _has_inference_model(paths["det"]):
        if "text_detection_model_dir" in init_params:
            config["text_detection_model_dir"] = paths["det"]
        else:
            config["det_model_dir"] = paths["det"]
    else:
        logger.info("未找到旧版本地文本检测模型，将使用 PaddleOCR 官方模型缓存/下载机制")

    if _has_inference_model(paths["rec"]):
        if "text_recognition_model_dir" in init_params:
            config["text_recognition_model_dir"] = paths["rec"]
        else:
            config["rec_model_dir"] = paths["rec"]
    else:
        logger.info("未找到旧版本地文本识别模型，将使用 PaddleOCR 官方模型缓存/下载机制")
    
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
        _OCR_INSTANCE = ocr
        logger.info(f"✅ PaddleOCR 初始化成功")
        return ocr
    except ValueError as e:
        if "Unknown argument" in str(e):
            logger.warning("⚠️ 重试使用最小化配置...")
            try:
                config_minimal = {"lang": "ch"}
                ocr = PaddleOCR(**config_minimal)
                _OCR_INSTANCE = ocr
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


def preload_paddleocr_async() -> None:
    """在后台线程预热 PaddleOCR，减少第一次上传简历时的等待时间。"""

    if _OCR_INSTANCE is not None:
        return

    def _preload() -> None:
        try:
            logger.info("后台预热 PaddleOCR 模型...")
            create_paddleocr()
        except Exception as exc:
            logger.warning("PaddleOCR 后台预热失败: %s: %s", type(exc).__name__, exc)

    thread = threading.Thread(target=_preload, name="paddleocr-preload", daemon=True)
    thread.start()
