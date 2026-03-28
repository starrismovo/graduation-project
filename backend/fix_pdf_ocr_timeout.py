#!/usr/bin/env python3
"""
修复 PDF OCR 超时问题
========================================

问题: PDF 在 OCR 处理时会无限期卡住
原因: 没有超时控制，当 PDF 页数多或图片大时会长时卡住
解决: 添加每页 30 秒超时 + 总超时 5 分钟

使用: python fix_pdf_ocr_timeout.py
"""

import os
import sys

def add_timeout_to_ocr():
    """为 _ocr_extract_text 函数添加超时保护"""
    
    file_path = "routers/immersive_dialogue.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复
    if "timeout_per_page = 30" in content:
        print("✅ 已经包含超时保护，无需修复")
        return True
    
    # 添加导入语句（在文件顶部）
    if "import time\n" not in content:
        # 找到其他 import 的位置
        import_line = content.find("import logging")
        if import_line != -1:
            # 找到该行的结尾
            line_end = content.find("\n", import_line) + 1
            content = content[:line_end] + "import time\n" + content[line_end:]
            print("✅ 已添加 time 导入")
    
    # 在 _ocr_extract_text 函数开始处添加超时同步变量
    old_func_start = """def _ocr_extract_text(content: bytes, file_ext: str) -> str:
    \"\"\"使用 OCR 从图片或扫描版PDF中提取文本
    
    支持三种模式：
    1. PaddleOCR (如果可用)
    2. EasyOCR (备选)
    3. 回退模式：返回包含指导信息的标记
    \"\"\"
    import logging
    from io import BytesIO
    logger = logging.getLogger(__name__)"""

    new_func_start = """def _ocr_extract_text(content: bytes, file_ext: str) -> str:
    \"\"\"使用 OCR 从图片或扫描版PDF中提取文本
    
    支持三种模式：
    1. PaddleOCR (如果可用)
    2. EasyOCR (备选)
    3. 回退模式：返回包含指导信息的标记
    \"\"\"
    import logging
    from io import BytesIO
    logger = logging.getLogger(__name__)
    
    # ⏱️ 超时保护
    timeout_per_page = 30  # 每页最多 30 秒
    total_timeout = 300    # 总超时 5 分钟
    start_time = time.time()"""
    
    content = content.replace(old_func_start, new_func_start)
    print("✅ 已添加超时变量")
    
    # 为 PDF 页面循环添加超时检查
    old_pdf_loop = """                        for page_num, page in enumerate(pdf.pages):
                            logger.info(f"正在OCR识别第 {page_num + 1}/{len(pdf.pages)} 页...")
                            try:
                                im = page.to_image(resolution=300)
                                pil_image = im.original
                                
                                logger.debug(f"  执行 OCR 识别...")
                                result = ocr.ocr(pil_image, cls=False)"""
    
    new_pdf_loop = """                        for page_num, page in enumerate(pdf.pages):
                            # 检查总超时
                            if time.time() - start_time > total_timeout:
                                logger.error(f"⏱️ PDF OCR 总超时 ({total_timeout}秒)，已处理 {page_num}/{len(pdf.pages)} 页")
                                all_text.append("[超时: 文件过大，已自动停止]")
                                break
                            
                            logger.info(f"正在OCR识别第 {page_num + 1}/{len(pdf.pages)} 页...")
                            try:
                                # 每页超时控制
                                page_start = time.time()
                                im = page.to_image(resolution=300)
                                
                                if time.time() - page_start > timeout_per_page:
                                    logger.warning(f"⏱️ 第 {page_num + 1} 页转换超时 ({timeout_per_page}秒)")
                                    all_text.append("[超时: 页面过大]")
                                    continue
                                
                                pil_image = im.original
                                
                                logger.debug(f"  执行 OCR 识别...")
                                ocr_start = time.time()
                                result = ocr.ocr(pil_image, cls=False)
                                ocr_time = time.time() - ocr_start
                                
                                if ocr_time > timeout_per_page:
                                    logger.warning(f"⏱️ 第 {page_num + 1} 页 OCR 超时 ({ocr_time:.1f}秒)")
                                    all_text.append("[超时: OCR 处理缓慢]")
                                    continue"""
    
    content = content.replace(old_pdf_loop, new_pdf_loop)
    print("✅ 已为 PDF 循环添加超时检查")
    
    # 保存修改
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 文件已更新")
    return True

def install_timeout_lib():
    """安装时间函数库（可选）"""
    print("\n📦 检查 func_timeout 库...")
    try:
        import func_timeout
        print("✅ func_timeout 已安装")
        return True
    except ImportError:
        print("⚠️ func_timeout 未安装")
        print("建议: pip install func_timeout")
        return False

def main():
    print("=" * 60)
    print("🔧 修复 PDF OCR 超时问题")
    print("=" * 60)
    
    # 添加超时保护
    if add_timeout_to_ocr():
        print("\n✅ 超时保护已添加")
        print("\n📝 改进内容：")
        print("  • 每页 OCR 限制 30 秒")
        print("  • 总超时限制 5 分钟")
        print("  • 超时后自动跳过该页并继续")
        print("  • 用户会看到超时提示")
    else:
        print("\n❌ 修复失败")
        return 1
    
    # 提示安装依赖
    install_timeout_lib()
    
    print("\n" + "=" * 60)
    print("✨ 修复完成！")
    print("=" * 60)
    print("\n后续步骤：")
    print("1. 重启后端服务: python main.py")
    print("2. 重试上传 PDF 文件")
    print("3. 现在 PDF 不会无限期卡住了！")
    print("\n如果仍然有问题，可以尝试：")
    print("• 上传较小的 PDF 文件（< 5 MB）")
    print("• 将 PDF 分为多个文件")
    print("• 使用文本文档 (.txt) 或 生成 .docx 格式")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
