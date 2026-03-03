@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 听写软件 - 自动打包脚本
echo ========================================
echo.

REM 设置 Python 版本和路径
set PYTHON_VERSION=3.11.6
set PYTHON_DIR=python-portable
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_ZIP=python.zip

REM 检查是否已存在便携版 Python
if exist "%PYTHON_DIR%\python.exe" (
    echo [√] 便携版 Python 已存在
    goto :install_deps
)

REM 下载便携版 Python
echo [1/5] 下载便携版 Python...
if not exist "%PYTHON_ZIP%" (
    echo 正在下载: %PYTHON_URL%
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'}"
    if errorlevel 1 (
        echo [×] 下载失败！
        echo 请手动下载: %PYTHON_URL%
        echo 并保存为: %PYTHON_ZIP%
        pause
        exit /b 1
    )
)

REM 解压 Python
echo [2/5] 解压 Python...
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
if errorlevel 1 (
    echo [×] 解压失败！
    pause
    exit /b 1
)

REM 配置嵌入式 Python
echo [3/5] 配置 Python...
(
echo Lib
echo Lib/site-packages
echo .
echo import site
) > "%PYTHON_DIR%\python%PYTHON_VERSION:.=%._pth"

REM 下载 get-pip.py
echo [4/5] 安装 pip...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py'}"
%PYTHON_DIR%\python.exe %PYTHON_DIR%\get-pip.py --no-warn-script-location
if errorlevel 1 (
    echo [×] pip 安装失败！
    pause
    exit /b 1
)

:install_deps
REM 安装依赖
echo [5/5] 安装项目依赖...
%PYTHON_DIR%\python.exe -m pip install --upgrade pip --no-warn-script-location
%PYTHON_DIR%\python.exe -m pip install -r requirements.txt --no-warn-script-location
%PYTHON_DIR%\python.exe -m pip install pyinstaller --no-warn-script-location
if errorlevel 1 (
    echo [×] 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 开始打包...
echo ========================================
echo.

REM 执行打包
%PYTHON_DIR%\python.exe build.py
if errorlevel 1 (
    echo [×] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 生成的文件：
dir /b dist
echo.
echo 按任意键清理临时文件...
pause >nul

REM 清理临时文件
echo.
echo 清理临时文件...
if exist "%PYTHON_ZIP%" del "%PYTHON_ZIP%"
if exist "%PYTHON_DIR%" rd /s /q "%PYTHON_DIR%"
if exist "build" rd /s /q "build"
if exist "*.spec" del "*.spec"

echo.
echo 清理完成！
echo 最终产物在 dist 目录下。
echo.
pause