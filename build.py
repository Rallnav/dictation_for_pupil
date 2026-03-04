#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将听写软件打包成exe
使用 PyInstaller 进行打包

注意：
- 在 Windows 环境下运行此脚本，可以直接生成 Windows exe 文件
- 在 Linux/Mac 环境下运行此脚本，生成的是对应平台的可执行文件
- 要在 Linux 上打包 Windows exe，需要安装 Wine 和 pyinstaller 的 Windows 版本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 设置标准输出编码为 UTF-8，解决 Windows 控制台中文显示问题
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller 安装完成")
    
    # 检查依赖
    try:
        import edge_tts
        print("✓ edge-tts 已安装")
    except ImportError:
        print("✗ edge-tts 未安装，请先安装: pip install edge-tts")
        sys.exit(1)
    
    try:
        import textual
        print("✓ textual 已安装")
    except ImportError:
        print("✗ textual 未安装，请先安装: pip install textual")
        sys.exit(1)
    
    try:
        import playsound3
        print("✓ playsound3 已安装")
    except ImportError:
        print("✗ playsound3 未安装，请先安装: pip install playsound3")
        sys.exit(1)


def get_executable_name():
    """根据平台获取可执行文件名"""
    system = platform.system()
    if system == "Windows":
        return "听写软件.exe"
    elif system == "Darwin":  # macOS
        return "听写软件.app"
    else:  # Linux
        return "听写软件"


def build_exe():
    """构建可执行文件"""
    print("\n开始打包...")
    
    exe_name = get_executable_name()
    is_windows = platform.system() == "Windows"
    
    # 检查必要的文件是否存在
    required_files = ["ui.py", "config.json"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"✗ 错误: 找不到必要的文件 {file}")
            sys.exit(1)
    
    # PyInstaller 参数说明：
    # --onefile: 打包成单个可执行文件
    # --windowed: 不显示控制台窗口（Windows）
    # --name: 生成的可执行文件名
    # --icon: 设置图标（可选）
    # --add-data: 添加数据文件（格式：源文件;目标目录，Windows 用 ; Linux/Mac 用 :）
    # --hidden-import: 隐藏导入的模块
    # --collect-all: 收集所有依赖
    
    # 根据平台设置分隔符
    separator = ";" if is_windows else ":"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "听写软件",
        "--add-data", f"config.json{separator}.",
        "--hidden-import", "edge_tts",
        "--hidden-import", "textual",
        "--hidden-import", "playsound3",
        "--collect-all", "textual",
    ]
    
    # 注意：Textual 需要控制台窗口，不能添加 --windowed 参数
    # --windowed 会导致 Textual 无法正常工作
    
    cmd.append("ui.py")
    
    print("执行命令:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("打包失败！")
        print("错误输出:", result.stderr)
        sys.exit(1)
    
    print("\n✓ 打包完成！")
    print(f"可执行文件位置: dist/{exe_name}")
    
    return exe_name


def create_readme_for_dist(exe_name):
    """创建打包后的说明文件"""
    system = platform.system()
    
    if system == "Windows":
        run_command = f"双击运行 `{exe_name}`"
        requirements = "Windows 10 或更高版本"
    elif system == "Darwin":
        run_command = f"双击运行 `{exe_name}` 或将应用拖到应用程序文件夹"
        requirements = "macOS 10.14 或更高版本"
    else:
        run_command = f"在终端中运行: ./{exe_name}"
        requirements = "Linux 系统（Ubuntu 18.04+ 或其他主流发行版）"
    
    readme_content = f"""# 听写软件 - 使用说明

## 系统要求

1. {requirements}
2. 无需安装额外依赖

## 安装步骤

1. 将 `{exe_name}` 复制到任意目录
2. {run_command}

## 首次使用

1. 首次运行会自动创建 `config.json` 配置文件
2. 在界面中添加或编辑词汇组
3. 点击"预生成音频"生成所有音频文件
4. 开始听写

## 常见问题

### 1. 音频无法播放
**解决方法**：
- 检查音频文件是否正确生成
- 查看程序输出日志
- 确保系统有音频输出设备

### 2. 界面显示异常
**解决方法**：
- 确保终端窗口足够大（建议 80x24 或更大）
- 尝试最大化终端窗口

## 配置文件

配置文件 `config.json` 会自动创建在程序所在目录，可以手动编辑或通过界面修改。

## 技术支持

如有问题，请查看项目 GitHub 仓库或提交 Issue。
"""
    
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    readme_path = dist_dir / "使用说明.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✓ 已创建使用说明: {readme_path}")


def print_cross_compile_info():
    """打印交叉编译说明"""
    print("\n" + "=" * 60)
    print("交叉编译说明")
    print("=" * 60)
    print("""
当前环境是 Linux，默认生成的是 Linux 可执行文件。

要在 Linux 上打包 Windows 的 exe 文件，有以下几种方法：

方法 1: 在 Windows 环境下打包（推荐）
-----------------------------------
1. 在 Windows 电脑上安装 Python
2. 安装依赖: pip install -r requirements.txt pyinstaller
3. 运行打包脚本: python build.py
4. 生成的 exe 文件在 dist/ 目录下

方法 2: 使用 Wine（Linux 上模拟 Windows）
---------------------------------------
1. 安装 Wine:
   sudo apt install wine
   
2. 安装 Python for Windows（通过 Wine）:
   wine msiexec /i python-3.11.0-amd64.msi
   
3. 使用 Wine 安装依赖:
   wine pip install -r requirements.txt pyinstaller
   
4. 使用 Wine 运行打包:
   wine python build.py

方法 3: 使用 Docker 交叉编译
--------------------------
1. 安装 Docker
2. 使用包含 Windows 交叉编译工具的 Docker 镜像:
   docker run -v $(pwd):/src cdrx/pyinstaller-windows

方法 4: 使用 GitHub Actions 自动打包
----------------------------------
1. 在项目中添加 .github/workflows/build.yml
2. 配置 GitHub Actions 在 Windows 环境下自动打包
3. 每次推送代码时自动构建 exe 文件

推荐使用方法 1（在 Windows 环境下打包）或方法 4（GitHub Actions），
这两种方法最稳定可靠。
""")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("听写软件 - 打包脚本")
    print("=" * 60)
    print(f"当前平台: {platform.system()}")
    print("=" * 60)
    
    # 检查依赖
    check_dependencies()
    
    # 构建可执行文件
    exe_name = build_exe()
    
    # 创建说明文件
    create_readme_for_dist(exe_name)
    
    print("\n" + "=" * 60)
    print("打包完成！")
    print("=" * 60)
    print(f"\n生成文件:")
    print(f"  - dist/{exe_name}")
    print(f"  - dist/使用说明.txt")
    print("\n注意事项:")
    print("  1. 用户无需安装任何额外依赖")
    print("  2. 将上述文件分发给用户即可")
    print("=" * 60)
    
    # 如果不是 Windows 平台，打印交叉编译说明
    if platform.system() != "Windows":
        print_cross_compile_info()