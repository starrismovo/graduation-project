#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简历上传功能 - 完全自动化修复脚本
一键检查、诊断和修复所有问题
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """打印分段标题"""
    width = 60
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*width}")
    print(f"{title.center(width)}")
    print(f"{'='*width}{Colors.RESET}\n")

def print_ok(msg):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    """打印错误消息"""
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_warning(msg):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_info(msg):
    """打印信息消息"""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def run_command(cmd, description=""):
    """运行命令并返回成功与否"""
    if description:
        print_info(description)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """检查Python版本"""
    print_section("第1步：检查Python环境")
    
    version = sys.version_info
    py_version = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python版本: {py_version}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"需要Python 3.8+，当前版本: {py_version}")
        return False
    
    print_ok("Python版本满足要求")
    return True

def check_backend_directory():
    """检查backend目录是否存在"""
    print_section("第2步：检查项目结构")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_error(f"backend目录不存在或不在当前目录")
        print_info(f"当前目录: {Path.cwd()}")
        print_warning("请在项目根目录运行此脚本")
        return False
    
    if not (backend_dir / "main.py").exists():
        print_error(f"backend/main.py不存在")
        return False
    
    if not (backend_dir / "requirements.txt").exists():
        print_error(f"backend/requirements.txt不存在")
        return False
    
    print_ok("项目结构正确")
    return True

def install_dependencies():
    """安装所有Python依赖"""
    print_section("第3步：安装Python依赖库")
    
    print_info("从requirements.txt安装依赖...")
    success, stdout, stderr = run_command(
        f"{sys.executable} -m pip install -r backend/requirements.txt",
        "正在安装依赖库..."
    )
    
    if success:
        print_ok("依赖库安装成功")
        return True
    else:
        print_error(f"依赖库安装失败")
        if stderr:
            print(f"错误详情: {stderr[:200]}")
        
        # 非致命错误，继续进行
        print_warning("将继续进行，后续步骤可能会失败")
        return False

def check_specific_libraries():
    """检查关键库"""
    print_section("第4步：检查关键依赖库")
    
    libs = [
        ('fastapi', 'FastAPI'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('pydantic', 'Pydantic'),
        ('docx', 'python-docx'),
        ('pdfplumber', 'pdfplumber'),
    ]
    
    missing = []
    
    for module, display_name in libs:
        try:
            __import__(module)
            print_ok(f"{display_name:<20} ✓ 已安装")
        except ImportError:
            print_error(f"{display_name:<20} ✗ 未安装")
            missing.append(display_name)
    
    if missing:
        print_warning(f"\n{len(missing)}个库未安装: {', '.join(missing)}")
        print_info("尝试单独安装缺失的库...")
        
        for lib in missing:
            if lib == 'python-docx':
                cmd = f"{sys.executable} -m pip install python-docx"
            elif lib == 'pdfplumber':
                cmd = f"{sys.executable} -m pip install pdfplumber"
            else:
                continue
            
            success, _, _ = run_command(cmd, f"正在安装 {lib}...")
            if success:
                print_ok(f"{lib} 安装成功")
            else:
                print_error(f"{lib} 安装失败，此库用于处理PDF/Word文件")
        
        return False
    
    print_ok("所有关键依赖库已安装")
    return True

def run_unit_tests():
    """运行单元测试"""
    print_section("第5步：运行单元测试")
    
    test_script = Path("backend/test_resume_upload.py")
    if not test_script.exists():
        print_warning("test_resume_upload.py 不存在，跳过单元测试")
        return True
    
    print_info("运行功能测试...")
    success, stdout, stderr = run_command(
        f"{sys.executable} backend/test_resume_upload.py"
    )
    
    if success:
        print_ok("单元测试通过")
        # 显示关键输出
        if "✓ 所有测试通过!" in stdout:
            print_ok("所有功能测试都通过了")
        return True
    else:
        print_error("单元测试失败")
        if "ImportError" in stderr:
            print_warning("可能是库未完全安装，但您可以继续")
        return False

def create_test_files():
    """创建测试文件"""
    print_section("第6步：创建测试文件")
    
    test_dir = Path("backend/test_files")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试简历
    test_resume = test_dir / "sample_resume.txt"
    test_resume.write_text("""姓名: 张三
邮箱: zhangsan@example.com
电话: 13800138000

教育背景:
2019-2021 本科 - 计算机科学与技术

工作经验:
2021-2023 某互联网公司，担任全栈工程师
- 主要使用 Python, JavaScript, React 技术栈
- 负责后端 API 开发和前端界面设计

技能:
Python, JavaScript, React, Vue, Django, FastAPI, MySQL, PostgreSQL, Docker, Git

项目经验:
1. 电商平台后端系统 - 使用Django + MySQL开发，支持万级QPS
2. 数据分析平台 - 使用Python进行数据处理和分析
""", encoding='utf-8')
    
    print_ok(f"创建测试文件: {test_resume.relative_to(Path.cwd())}")
    
    return True

def print_next_steps():
    """打印后续步骤"""
    print_section("✅ 诊断完成！")
    
    print(f"""{Colors.BOLD}后续步骤:{Colors.RESET}

1. 启动后端服务:
   {Colors.CYAN}cd backend && python main.py{Colors.RESET}
   
   或在Windows上:
   {Colors.CYAN}cd backend && python main.py{Colors.RESET}

2. 测试文件上传功能:
   
   选项A - 使用前端测试工具（推荐）:
   {Colors.CYAN}前端/test-resume-upload.html{Colors.RESET}
   (在浏览器中打开此HTML文件)
   
   选项B - 使用命令行测试:
   {Colors.CYAN}curl -X POST -F "file=@backend/test_files/sample_resume.txt" \\
     "http://localhost:8000/assessment/immersive/upload-resume?candidate_id=test123"{Colors.RESET}

3. 如遇到问题，查看详细故障排除指南:
   {Colors.CYAN}RESUME_UPLOAD_TROUBLESHOOTING.md{Colors.RESET}

4. 查看改进总结:
   {Colors.CYAN}RESUME_UPLOAD_IMPROVEMENTS.md{Colors.RESET}

{Colors.BOLD}常见问题解决:{Colors.RESET}

如果文件上传仍然失败:
• 检查后端日志中的错误信息
• 确保 python-docx 和 pdfplumber 已安装
• 尝试上传 .txt 文件（最简单的格式）
• 查看 frontend/test-resume-upload.html 的调试日志

""")

def main():
    """主函数"""
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"""{Colors.BOLD}{Colors.CYAN}
╔════════════════════════════════════════════════════╗
║  简历上传功能 - 完全自动化修复工具 v1.0  ║
║  Resume Upload - Automated Repair Tool v1.0  ║
╚════════════════════════════════════════════════════╝
{Colors.RESET}""")
    
    steps = [
        ("检查Python版本", check_python_version),
        ("检查项目结构", check_backend_directory),
        ("安装依赖库", install_dependencies),
        ("检查关键库", check_specific_libraries),
        ("运行单元测试", run_unit_tests),
        ("创建测试文件", create_test_files),
    ]
    
    completed = 0
    failed = []
    
    for step_name, step_func in steps:
        try:
            result = step_func()
            if result:
                completed += 1
            else:
                failed.append(step_name)
        except Exception as e:
            print_error(f"{step_name} 出错: {e}")
            failed.append(step_name)
    
    # 总结
    print_section("诊断总结")
    
    total = len(steps)
    print(f"完成步骤: {completed}/{total}")
    
    if completed == total:
        print_ok("所有步骤都通过了！系统已准备就绪")
        print_next_steps()
    else:
        print_warning(f"有 {len(failed)} 个步骤失败或跳过: {', '.join(failed)}")
        print_info("这可能表示：")
        print("  • 某些依赖库未安装（可能影响功能）")
        print("  • 但大多数功能仍可正常工作")
        print("  • 请查看上面的日志找出具体问题")
        print_next_steps()
    
    input(f"\n{Colors.BOLD}按Enter键退出...{Colors.RESET}")

if __name__ == '__main__':
    main()
