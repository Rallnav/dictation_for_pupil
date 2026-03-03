@echo off
chcp 65001 >nul
echo ========================================
echo 听写软件 - Windows 打包脚本
echo ========================================
echo.

REM 设置便携版 Python 路径
set PYTHON_DIR=python-portable
set PYTHON_EXE=%PYTHON_DIR%\python.exe

REM 检查是否已下载便携版 Python
if not exist "%PYTHON_EXE%" (
    echo 正在下载便携版 Python...
    echo 请手动下载以下文件并解压到 python-portable 目录：
    echo https://github.com/winpython/winpython/releases/download/4.5.20231217/Winpython64-3.11.6.0.exe
    echo.
    echo 或者使用嵌入式版本：
    echo https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip
    echo.
    pause
    exit /b 1
)

echo 使用便携版 Python: %PYTHON_EXE%
echo.

REM 安装依赖
echo 正在安装依赖...
%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install -r requirements.txt
%PYTHON_EXE% -m pip install pyinstaller
echo.

REM 打包
echo 开始打包...
%PYTHON_EXE% build.py
echo.

echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 生成的文件在 dist 目录下：
echo   - 听写软件.exe
echo   - 使用说明.txt
echo.
pause