@echo off
cd /d D:\Desktop\graduation-project\backend
call venv\Scripts\activate.bat
python test_paddleocr_init.py
echo.
echo Exit code: %errorlevel%
