# 🚀 从 Gitee 迁移到 GitHub 完整指南

## 📋 当前状态

- **当前远程仓库**: `https://gitee.com/ezilostal/dictation_for_pupil.git`
- **当前分支**: `master`
- **其他分支**: `develop`, `feature`

---

## 🎯 迁移目标

1. ✅ 在 GitHub 创建新仓库
2. ✅ 推送所有代码到 GitHub
3. ✅ 配置 GitHub Actions 自动构建
4. ✅ 生成 Windows 和 Linux 可执行文件

---

## 📝 详细步骤

### 步骤 1: 在 GitHub 创建新仓库

**方法 A: 手动创建（推荐）**

1. 访问 GitHub: https://github.com/new
2. 填写仓库信息:
   - **Repository name**: `dictation_for_pupil`
   - **Description**: 小学生听写软件
   - **Visibility**: Public（公开，可以使用免费的 GitHub Actions）
   - **⚠️ 不要勾选**: "Add a README file"、"Add .gitignore"、"Choose a license"
     （因为本地已有这些文件）
3. 点击 "Create repository"

**方法 B: 使用 GitHub CLI（如果已安装 gh）**

```bash
# 安装 GitHub CLI
sudo apt install gh

# 登录 GitHub
gh auth login

# 创建仓库
gh repo create dictation_for_pupil --public --description "小学生听写软件"
```

---

### 步骤 2: 添加 GitHub 远程仓库

**选择以下方案之一：**

**方案 A: 替换 origin（推荐，完全迁移到 GitHub）**

```bash
# 将 origin 指向 GitHub
git remote set-url origin https://github.com/您的用户名/dictation_for_pupil.git

# 保留 Gitee 作为备用
git remote add gitee https://gitee.com/ezilostal/dictation_for_pupil.git
```

**方案 B: 同时保留两个仓库（推荐，双重备份）**

```bash
# 添加 GitHub 作为新的远程仓库
git remote add github https://github.com/您的用户名/dictation_for_pupil.git

# 查看所有远程仓库
git remote -v
# 应该看到:
# origin  https://gitee.com/ezilostal/dictation_for_pupil.git (fetch)
# origin  https://gitee.com/ezilostal/dictation_for_pupil.git (push)
# github  https://github.com/您的用户名/dictation_for_pupil.git (fetch)
# github  https://github.com/您的用户名/dictation_for_pupil.git (push)
```

---

### 步骤 3: 推送代码到 GitHub

**推送所有分支和标签：**

```bash
# 方案 A: 如果替换了 origin
git push -u origin master
git push origin develop
git push origin feature
git push --tags

# 方案 B: 如果添加了 github 远程仓库
git push github master
git push github develop
git push github feature
git push github --tags
```

**如果需要身份验证：**

```bash
# 方法 1: 使用 Personal Access Token
# 1. 在 GitHub 创建 token: Settings -> Developer settings -> Personal access tokens
# 2. 使用 token 推送
git push https://您的token@github.com/您的用户名/dictation_for_pupil.git master

# 方法 2: 使用 SSH
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "您的邮箱"
# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub
# 3. 添加到 GitHub: Settings -> SSH and GPG keys -> New SSH key
# 4. 使用 SSH 地址
git remote set-url origin git@github.com:您的用户名/dictation_for_pupil.git
git push -u origin master
```

---

### 步骤 4: 验证 GitHub Actions

**推送完成后，GitHub Actions 会自动开始构建：**

1. 进入 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 可以看到正在运行的工作流 "Build Executables"
4. 等待构建完成（约 5-10 分钟）

**构建产物：**

- `听写软件-Windows` - Windows exe 文件
- `听写软件-Linux` - Linux 可执行文件

**下载构建产物：**

1. 点击完成的工作流
2. 在 "Artifacts" 部分点击下载
3. 解压后即可使用

---

### 步骤 5: 发布版本（可选）

**创建 Release：**

```bash
# 创建标签
git tag -a v1.0.0 -m "首次发布"

# 推送标签到 GitHub
git push origin v1.0.0
# 或
git push github v1.0.0

# GitHub Actions 会自动创建 Release 并上传文件
```

---

## 🔧 GitHub Actions 配置说明

**工作流文件位置**: `.github/workflows/build.yml`

**触发条件:**
- 推送到 `main` 或 `master` 分支
- Pull Request 到 `main` 或 `master` 分支
- 手动触发

**构建内容:**
- Windows 可执行文件（.exe）
- Linux 可执行文件
- 使用说明文档

**构建环境:**
- Windows: `windows-latest`
- Linux: `ubuntu-latest`
- Python: 3.11

---

## 📊 迁移检查清单

- [ ] 在 GitHub 创建新仓库
- [ ] 添加 GitHub 远程仓库
- [ ] 推送 master 分支
- [ ] 推送其他分支（develop, feature）
- [ ] 推送所有标签
- [ ] 验证 GitHub Actions 开始运行
- [ ] 等待构建完成
- [ ] 下载构建产物测试
- [ ] 更新本地 Git 配置（可选）
- [ ] 通知团队成员新的仓库地址

---

## 🔄 后续维护

**日常推送:**

```bash
# 方案 A: 完全迁移到 GitHub
git add .
git commit -m "更新说明"
git push origin master

# 方案 B: 同时推送到两个仓库
git add .
git commit -m "更新说明"
git push origin master  # 推送到 Gitee
git push github master  # 推送到 GitHub
```

**同步两个仓库:**

```bash
# 从 Gitee 拉取更新
git pull origin master

# 推送到 GitHub
git push github master
```

---

## ❓ 常见问题

### 1. 推送时提示权限错误

**解决方法:**
```bash
# 使用 Personal Access Token
git push https://您的token@github.com/您的用户名/dictation_for_pupil.git master

# 或使用 SSH
git remote set-url origin git@github.com:您的用户名/dictation_for_pupil.git
git push origin master
```

### 2. GitHub Actions 构建失败

**检查步骤:**
1. 查看 Actions 页面的错误日志
2. 确保 `requirements.txt` 文件存在
3. 确保所有依赖都正确列出
4. 检查 Python 版本兼容性

### 3. 如何同时维护两个仓库

**推荐工作流:**
```bash
# 1. 开发新功能
git checkout -b feature/new-feature
git add .
git commit -m "添加新功能"

# 2. 推送到两个仓库
git push origin feature/new-feature  # Gitee
git push github feature/new-feature  # GitHub

# 3. 合并到主分支
git checkout master
git merge feature/new-feature
git push origin master
git push github master
```

---

## 📞 需要帮助？

如果遇到问题，请提供以下信息：
- 错误信息截图
- 执行的命令
- Git 版本 (`git --version`)

---

## 🎉 迁移完成后的优势

✅ **自动构建**: 每次推送自动生成可执行文件  
✅ **多平台支持**: 同时生成 Windows 和 Linux 版本  
✅ **版本管理**: 自动创建 Release  
✅ **持续集成**: 代码质量自动检查  
✅ **社区支持**: 更好的开源社区生态  

---

**准备好开始迁移了吗？按照上述步骤执行即可！**