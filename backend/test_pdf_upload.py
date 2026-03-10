#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试PDF文件上传功能
"""
import requests
import json
from pathlib import Path
from io import BytesIO

# 创建一个简单的测试PDF
def create_test_pdf():
    """创建包含文本的测试PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # 创建PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # 添加中文文本（需要中文字体支持）
        # 由于reportlab对中文支持复杂，我们使用简化的方案
        c.drawString(100, 750, "Zhang San Resume")
        c.drawString(100, 730, "Email: zhangsan@example.com")
        c.drawString(100, 710, "Phone: 13812345678")
        c.drawString(100, 690, "Education: Bachelor")
        c.drawString(100, 670, "Skills: Python, Java, React")
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    except ImportError:
        # 如果reportlab不可用，创建一个最小的PDF
        import struct
        
        pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 200 >>
stream
BT
/F1 12 Tf
100 750 Td
(Resume of Zhang San) Tj
0 -20 Td
(Email: zhangsan@example.com) Tj
0 -20 Td
(Phone: 13812345678) Tj
0 -20 Td
(Skills: Python, Java, React, Django, MySQL) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000074 00000 n
0000000133 00000 n
0000000240 00000 n
0000000333 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
587
%%EOF"""
        return pdf

print("=" * 60)
print("测试PDF文件上传功能")
print("=" * 60)

# 创建测试PDF
print("\n📝 创建测试PDF文件...")
pdf_content = create_test_pdf()
test_file = Path("temp_test_resume.pdf")

with open(test_file, 'wb') as f:
    f.write(pdf_content)

print(f"✅ 创建完成，文件大小: {len(pdf_content)} 字节")

try:
    # 上传测试
    print("\n📤 上传PDF文件到后端...")
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/pdf')}
        
        response = requests.post(
            'http://localhost:8000/assessment/immersive/upload-resume',
            files=files,
            params={'candidate_id': 'test_pdf_candidate'},
            timeout=10
        )
    
    print(f"状态码: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 上传成功!\n")
        
        # 显示关键信息
        data = result.get('data', result)
        print("📋 响应摘要:")
        print(f"  文件名: {data.get('filename')}")
        print(f"  文件大小: {data.get('file_size')} 字节")
        print(f"  提取方式: {data.get('extraction_method')}")
        print(f"  状态: {result.get('message')}")
        
        # 显示提取的文本
        extracted = data.get('extracted_text', '')
        if extracted:
            print(f"\n📄 提取的文本预览:")
            print(f"  {extracted[:200]}...")
        else:
            print(f"\n⚠️  未能提取文本内容")
        
        # 显示候选人信息
        if 'candidate_info' in data:
            info = data['candidate_info']
            print(f"\n👤 候选人信息:")
            print(f"  姓名: {info.get('name')}")
            print(f"  邮箱: {info.get('email')}")
            print(f"  电话: {info.get('phone')}")
    else:
        print(f"❌ 上传失败!")
        print(f"响应: {response.text[:300]}")

except requests.exceptions.ConnectionError:
    print("❌ 连接失败，后端服务未运行")
    print("   请在另一个终端运行: python main.py")
except Exception as e:
    print(f"❌ 发生错误: {e}")

finally:
    # 清理
    if test_file.exists():
        test_file.unlink()
    print("\n✅ 已清理临时文件")

print("\n" + "=" * 60)
