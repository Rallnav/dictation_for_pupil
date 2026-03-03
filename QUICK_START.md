# 🚀 快速开始 - GitHub Actions 自动构建

## 📝 一键迁移脚本

**使用迁移脚本自动完成所有步骤：**

```bash
# 1. 给脚本添加执行权限
chmod +x migrate_to_github.sh

# 2. 运行迁移脚本
./migrate_to_github.sh

# 3. 按照提示输入您的 GitHub 用户名
# 4. 确认后脚本会自动完成迁移
```

---

## 🎯 手动迁移步骤

### 1️⃣ 在 GitHub 创建仓库

访问: https://github.com/new

- Repository name: `dictation_for_pupil`
- Visibility: **Public**（公开仓库可以使用免费的 GitHub Actions）
- **不要勾选** "Add a README file" 等选项

### 2️⃣ 添加 GitHub 远程仓库

```bash
# 添加 GitHub 远程仓库（替换为您的用户名）
git remote add github https://github.com/您的用户名/dictation_for_pupil.git

# 查看远程仓库
git remote -v
```

### 3️⃣ 推送代码

```bash
# 推送 master 分支
git push github master

# 推送其他分支
git push github develop
git push github feature

# 推送标签
git push github --tags
```

### 4️⃣ 查看 GitHub Actions

推送完成后，GitHub Actions 会自动开始构建：

1. 访问: https://github.com/您的用户名/dictation_for_pupil/actions
2. 查看构建进度
3. 等待构建完成（约 5-10 分钟）

### 5️⃣ 下载构建产物

构建完成后：

1. 点击完成的工作流
2. 在 "Artifacts" 部分下载：
   - `听写软件-Windows` - Windows exe 文件
   - `听写软件-Linux` - Linux 可执行文件

---

## 🔐 身份验证

### 方法 1: Personal Access Token（推荐）

```bash
# 1. 创建 token: https://github.com/settings/tokens
#    勾选 "repo" 权限

# 2. 使用 token 推送
git push https://您的token@github.com/您的用户名/dictation_for_pupil.git master
```

### 方法 2: SSH

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "您的邮箱"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 添加到 GitHub: https://github.com/settings/keys

# 4. 使用 SSH 地址
git remote set-url github git@github.com:您的用户名/dictation_for_pupil.git
git push github master
```

---

## 📊 构建流程

```
推送代码到 GitHub
    ↓
GitHub Actions 自动触发
    ↓
在 Windows 环境构建 exe
    ↓
在 Linux 环境构建可执行文件
    ↓
上传构建产物
    ↓
下载使用
```

---

## ✅ 检查清单

- [ ] 在 GitHub 创建仓库
- [ ] 添加 GitHub 远程仓库
- [ ] 推送代码
- [ ] 查看 Actions 页面
- [ ] 等待构建完成
- [ ] 下载构建产物
- [ ] 测试可执行文件

---

## 🎉 完成！

迁移完成后，每次推送代码到 GitHub，都会自动构建可执行文件！

**需要帮助？** 查看 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) 获取详细说明。