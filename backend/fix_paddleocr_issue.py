#!/usr/bin/env python3
"""
PaddleOCR 兼容性问题快速修复工具
用于处理 AttributeError: 'paddle.base.libpaddle.AnalysisConfig' object has no attribute 'set_optimization_level'
"""

import subprocess
import sys
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(cmd, description=""):
    """运行系统命令"""
    if description:
        logger.info(f"📝 {description}")
    logger.info(f"  执行: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"  ❌ 命令失败: {result.stderr}")
        return False
    else:
        logger.info(f"  ✅ 成功")
        if result.stdout:
            logger.debug(f"  输出: {result.stdout[:200]}")
        return True

def check_environment():
    """检查当前环境"""
    logger.info("\n" + "="*60)
    logger.info("🔍 检查环境信息")
    logger.info("="*60)
    
    # 检查 Python 版本
    logger.info(f"Python 版本: {sys.version}")
    
    # 检查已安装的相关包
    packages = ["paddleocr", "paddle", "paddlepaddle"]
    for pkg in packages:
        result = subprocess.run(
            f'pip show {pkg}',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith(('Name:', 'Version:', 'Location:')):
                    logger.info(f"  {line}")

def method1_update_packages():
    """方案 1: 更新所有相关包"""
    logger.info("\n" + "="*60)
    logger.info("📝 方案 1: 更新 PaddleOCR 和 Paddle")
    logger.info("="*60)
    
    logger.info("⚠️  这可能需要 5-10 分钟...")
    
    commands = [
        ("pip install --upgrade paddleocr", "升级 PaddleOCR"),
        ("pip install --upgrade paddlepaddle", "升级 Paddle"),  # 可能需要 opencv-contrib-python、numpy 等
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            logger.warning(f"  ⚠️  {desc} 可能失败，继续尝试其他方案...")

def method2_reinstall_compatible():
    """方案 2: 安装已知兼容的版本"""
    logger.info("\n" + "="*60)
    logger.info("📝 方案 2: 安装已知兼容的版本")
    logger.info("="*60)
    
    # 已知工作的版本组合
    compatible_versions = [
        ("paddleocr==2.7.0.3", "paddlepaddle==2.5.0"),
        ("paddleocr==2.6.0.3", "paddlepaddle==2.4.2"),
        ("paddleocr==2.5.0.3", "paddlepaddle==2.3.0"),
    ]
    
    for paddle_ocr_ver, paddle_ver in compatible_versions:
        logger.info(f"\n尝试安装: {paddle_ocr_ver} + {paddle_ver}")
        
        commands = [
            (f"pip install --user {paddle_ocr_ver}", "安装 PaddleOCR"),
            (f"pip install --user {paddle_ver}", "安装 Paddle"),
        ]
        
        success = True
        for cmd, desc in commands:
            if not run_command(cmd, desc):
                success = False
                break
        
        if success:
            logger.info(f"✅ {paddle_ocr_ver} + {paddle_ver} 安装完成")
            return True
        else:
            logger.info(f"⏭️  {paddle_ocr_ver} 失败，尝试下一个版本...")
    
    return False

def method3_disable_optimization():
    """方案 3: 通过环境变量禁用优化级别 (已在代码中实现)"""
    logger.info("\n" + "="*60)
    logger.info("📝 方案 3: 环境变量禁用优化")
    logger.info("="*60)
    
    logger.info("✅ 已在 paddleocr_local.py 中添加以下环境变量:")
    logger.info("  - PADDLE_FLAGS= 多个标志")
    logger.info("  - PADDLE_DISABLE_PROFILER=1")
    logger.info("  - FLAGS_disable_memory_optimize=1")
    logger.info("  - FLAGS_use_cinn=0")
    logger.info("\n💡 如果上面的方案不行，这会自动生效")

def method4_use_easyocr():
    """方案 4: 使用 EasyOCR 替代 PaddleOCR"""
    logger.info("\n" + "="*60)
    logger.info("📝 方案 4: 安装 EasyOCR 作为备选方案")
    logger.info("="*60)
    
    logger.info("EasyOCR 将自动作为 PaddleOCR 的备选方案...")
    
    if run_command("pip install easyocr", "安装 EasyOCR"):
        logger.info("✅ EasyOCR 已安装，系统会自动使用")
        return True
    return False

def test_paddleocr():
    """测试 PaddleOCR 是否可以正常初始化"""
    logger.info("\n" + "="*60)
    logger.info("🧪 测试 PaddleOCR 初始化")
    logger.info("="*60)
    
    try:
        # 设置环保变量
        os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
        os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'
        os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
        os.environ['PADDLE_DISABLE_PROFILER'] = '1'
        os.environ['FLAGS_disable_memory_optimize'] = '1'
        os.environ['FLAGS_use_cinn'] = '0'
        
        logger.info("尝试导入 paddleocr_local...")
        from paddleocr_local import create_paddleocr
        
        logger.info("尝试初始化 PaddleOCR...")
        ocr = create_paddleocr()
        
        logger.info("✅ PaddleOCR 初始化成功!")
        return True
    except AttributeError as e:
        logger.error(f"❌ 版本兼容性问题: {e}")
        return False
    except ImportError as e:
        logger.error(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 初始化失败: {type(e).__name__}: {e}")
        return False

def main():
    """主函数"""
    logger.info("\n")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*58 + "║")
    logger.info("║  🔧 PaddleOCR 兼容性问题快速修复工具v1.0".ljust(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("╚" + "="*58 + "╝")
    
    # 检查环境
    check_environment()
    
    # 尝试多个修复方案
    solutions = [
        ("更新所有包", method1_update_packages),
        ("安装兼容版本", method2_reinstall_compatible),
        ("禁用优化级别", method3_disable_optimization),
        ("安装 EasyOCR 备选", method4_use_easyocr),
    ]
    
    logger.info("\n" + "="*60)
    logger.info("🚀 开始修复...")
    logger.info("="*60)
    
    logger.info("""
建议执行顺序:
1️⃣  尝试更新所有包（最快）
2️⃣  如果失败，下载兼容版本
3️⃣  环境变量禁用会自动应用
4️⃣  最后安装 EasyOCR 作为备选
    """)
    
    for name, method in solutions[:2]:  # 只自动尝试前两个
        try:
            logger.info(f"\n尝试: {name}...")
            method()
        except Exception as e:
            logger.error(f"执行失败: {e}")
    
    # 方案 3 是自动的
    method3_disable_optimization()
    
    # 测试
    logger.info("\n")
    logger.info("="*60)
    logger.info("🧪 最后测试...")
    logger.info("="*60)
    
    if test_paddleocr():
        logger.info("""
✅ 修复成功！现在可以:
  1. 重启后端服务
  2. 测试简历上传功能
  3. 检查日志确认 PaddleOCR 正常加载
        """)
    else:
        logger.warning("""
⚠️  PaddleOCR 仍然有问题。请尝试:
  1. 手动运行: pip install -U paddleocr paddlepaddle
  2. 或使用 EasyOCR 替代: pip install easyocr
  3. 查看详细日志了解具体错误
        """)

if __name__ == "__main__":
    main()
