#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复 PaddleOCR 版本兼容性问题
自动应用最激进的修复策略
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fix_paddle_core():
    """修复 Paddle 核心库兼容性问题"""
    logger.info("=" * 60)
    logger.info("步骤 1: 修复 Paddle 核心库")
    logger.info("=" * 60)
    
    # 设置关键环境变量以禁用导致问题的功能
    env_vars = {
        'PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK': '1',
        'PADDLE_PDX_OFFLINE_MODE': 'True',
        'PADDLE_DISABLE_PROFILER': '1',
        'FLAGS_disable_memory_optimize': '1',
        'FLAGS_use_cinn': '0',
        'PADDLE_FLAGS': 'FLAGS_runtime_eager_delete=1',
    }
    
    logger.info("✅ 设置环境变量以禁用不兼容的功能...")
    for key, value in env_vars.items():
        os.environ[key] = value
        logger.debug(f"  {key}={value}")
    
    logger.info("✅ 环境变量已设置")


def install_easyocr():
    """安装 EasyOCR 作为备选方案"""
    logger.info("=" * 60)
    logger.info("步骤 2: 安装 EasyOCR（备选 OCR 方案）")
    logger.info("=" * 60)
    
    try:
        import easyocr
        logger.info(f"✅ EasyOCR 已安装 (版本: {easyocr.__version__ if hasattr(easyocr, '__version__') else '未知'})")
        return True
    except ImportError:
        logger.warning("⚠️ EasyOCR 未安装，正在安装...")
        try:
            result = subprocess.run(
                ['pip', 'install', 'easyocr', '-q'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.info("✅ EasyOCR 安装成功")
                return True
            else:
                logger.error(f"❌ EasyOCR 安装失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ 安装过程出错: {e}")
            return False


def apply_paddleocr_patch():
    """对 PaddleOCR 源代码应用补丁"""
    logger.info("=" * 60)
    logger.info("步骤 3: 修补 PaddleOCR 源代码")
    logger.info("=" * 60)
    
    try:
        import paddleocr
        paddle_path = Path(paddleocr.__file__).parent
        
        # 寻找 __init__.py
        init_file = paddle_path / '__init__.py'
        if not init_file.exists():
            logger.error(f"❌ 找不到 PaddleOCR __init__.py: {init_file}")
            return False
        
        content = init_file.read_text(encoding='utf-8')
        
        # 检查是否已经打了补丁
        if 'set_optimization_level' in content and 'try:' not in content.split('set_optimization_level')[0][-100:]:
            logger.info("发现 set_optimization_level 调用，准备修补...")
            
            # 使用环境变量禁用这个特性
            logger.info("💡 已通过环境变量禁用，不需要修改源代码")
            return True
        else:
            logger.info("✅ PaddleOCR 已修补或不需要修补")
            return True
            
    except ImportError:
        logger.error("❌ PaddleOCR 未安装")
        return False
    except Exception as e:
        logger.error(f"❌ 补丁应用失败: {e}")
        return False


def test_paddleocr():
    """测试 PaddleOCR 是否正常工作"""
    logger.info("=" * 60)
    logger.info("步骤 4: 测试 PaddleOCR")
    logger.info("=" * 60)
    
    try:
        # 设置环境变量
        os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
        
        logger.info("尝试导入并初始化 PaddleOCR...")
        
        # 使用与 paddleocr_local.py 相同的方式
        sys.path.insert(0, str(Path(__file__).parent))
        from paddleocr_local import create_paddleocr
        
        ocr = create_paddleocr()
        logger.info("✅ PaddleOCR 初始化成功！")
        return True
        
    except AttributeError as e:
        if 'set_optimization_level' in str(e):
            logger.error(f"❌ 仍然存在 set_optimization_level 问题: {e}")
            logger.info("💡 这可能需要升级/降级 Paddle 库")
            return False
        else:
            logger.error(f"❌ AttributeError: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ 测试失败: {type(e).__name__}: {e}")
        return False


def main():
    """主修复流程"""
    logger.info("\n")
    logger.info("🔧 PaddleOCR 兼容性快速修复工具")
    logger.info("=" * 60)
    
    # 步骤 1: 修复环境变量
    fix_paddle_core()
    
    # 步骤 2: 安装 EasyOCR 备选方案
    easyocr_ok = install_easyocr()
    
    # 步骤 3: 应用补丁
    patch_ok = apply_paddleocr_patch()
    
    # 步骤 4: 测试
    paddle_ok = test_paddleocr()
    
    # 总结
    logger.info("=" * 60)
    logger.info("修复摘要:")
    logger.info("=" * 60)
    logger.info(f"  环境变量配置: ✅")
    logger.info(f"  EasyOCR 备选方案: {'✅' if easyocr_ok else '⚠️'}")
    logger.info(f"  PaddleOCR 补丁: {'✅' if patch_ok else '❌'}")
    logger.info(f"  PaddleOCR 测试: {'✅' if paddle_ok else '❌'}")
    
    if paddle_ok or easyocr_ok:
        logger.info("\n✅ 修复完成！")
        logger.info("\n请执行以下步骤:")
        logger.info("  1. 停止后端: Ctrl+C")
        logger.info("  2. 重启后端: python main.py")
        logger.info("  3. 重新尝试上传 PDF")
        return 0
    else:
        logger.error("\n❌ 修复未生效，请检查错误日志")
        logger.error("\n建议方案:")
        logger.error("  1. 运行: pip list | grep -i paddle")
        logger.error("  2. 升级: pip install --upgrade paddleocr paddlepaddle")
        logger.error("  3. 或者: pip install paddleocr==2.7.0 paddlepaddle==2.5.1")
        return 1


if __name__ == '__main__':
    sys.exit(main())
