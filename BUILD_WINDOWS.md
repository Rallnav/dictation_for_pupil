# Windows 打包说明

## 方法 1：使用便携版 Python（推荐，无需安装）

### 步骤：

1. **下载便携版 Python**
   - 下载嵌入式 Python（约 10MB）：
     https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip
   
   - 解压到项目目录下的 `python-portable` 文件夹

2. **配置嵌入式 Python**
   - 编辑 `python-portable/python311._pth` 文件
   - 取消注释 `import site` 这一行
   - 添加以下内容：
     ```
     Lib
     Lib/site-packages
     .
     import site
     ```

3. **安装依赖**
   ```cmd
   python-portable\python.exe -m pip install --upgrade pip
   python-portable\python.exe -m pip install -r requirements.txt
   python-portable\python.exe -m pip install pyinstaller
   ```

4. **打包**
   ```cmd
   python-portable\python.exe build.py
   ```

5. **清理**
   - 打包完成后，可以删除 `python-portable` 目录
   - 只保留 `dist` 目录下的文件

---

## 方法 2：使用虚拟环境（推荐，完全隔离）

### 步骤：

1. **下载 Python 安装包**
   - 下载 Python 3.11：https://www.python.org/downloads/
   - **注意**：安装时勾选 "Add Python to PATH"

2. **创建虚拟环境**
   ```cmd
   python -m venv venv
   ```

3. **激活虚拟环境**
   ```cmd
   venv\Scripts\activate
   ```

4. **安装依赖**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

5. **打包**
   ```cmd
   python build.py
   ```

6. **清理**
   - 打包完成后，可以删除 `venv` 目录
   - 也可以卸载 Python（如果不再需要）

---

## 方法 3：使用 GitHub Actions（无需本地 Python）

### 步骤：

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "Add build workflow"
   git push
   ```

2. **查看构建结果**
   - 进入 GitHub 仓库页面
   - 点击 "Actions" 标签
   - 等待构建完成
   - 下载构建产物（听写软件.exe）

3. **发布版本**
   - 创建新的 tag：
     ```bash
     git tag v1.0.0
     git push origin v1.0.0
     ```
   - GitHub Actions 会自动创建 Release 并上传 exe 文件

---

## 方法 4：使用 Docker（Linux 用户）

如果您在 Linux 上，可以使用 Docker 在 Windows 容器中打包：

```bash
# 安装 Docker
sudo apt install docker.io

# 使用 Windows 容器打包
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-windows
```

---

## 推荐方案

根据您的需求选择：

1. **临时打包**：使用方法 1（便携版 Python）
   - 优点：无需安装，打包后可删除
   - 缺点：需要手动配置

2. **长期开发**：使用方法 2（虚拟环境）
   - 优点：环境隔离，易于管理
   - 缺点：需要安装 Python

3. **自动化构建**：使用方法 3（GitHub Actions）
   - 优点：无需本地环境，自动构建
   - 缺点：需要 GitHub 账号

---

## 打包产物

打包完成后，`dist` 目录下会生成：

```
dist/
├── 听写软件.exe      # 主程序（包含所有依赖）
└── 使用说明.txt      # 用户说明文档
```

将这两个文件分发给用户即可，用户无需安装任何依赖。