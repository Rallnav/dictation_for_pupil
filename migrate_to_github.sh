#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Git 仓库迁移助手${NC}"
echo -e "${BLUE}  Gitee -> GitHub${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    echo -e "${RED}错误: 当前目录不是 Git 仓库${NC}"
    exit 1
fi

# 显示当前配置
echo -e "${YELLOW}当前 Git 配置:${NC}"
git remote -v
echo ""

# 显示当前分支
echo -e "${YELLOW}当前分支:${NC}"
git branch
echo ""

# 获取 GitHub 用户名
echo -e "${YELLOW}请输入您的 GitHub 用户名:${NC}"
read -p "GitHub 用户名: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}错误: 用户名不能为空${NC}"
    exit 1
fi

# 设置仓库 URL
GITHUB_REPO="https://github.com/${GITHUB_USERNAME}/dictation_for_pupil.git"

echo ""
echo -e "${YELLOW}即将执行以下操作:${NC}"
echo -e "1. 添加 GitHub 远程仓库: ${GREEN}${GITHUB_REPO}${NC}"
echo -e "2. 推送 master 分支到 GitHub"
echo -e "3. 推送所有标签到 GitHub"
echo ""

# 确认
echo -e "${YELLOW}是否继续? (y/n)${NC}"
read -p "请输入: " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${RED}操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  开始迁移...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 移除旧的 github 远程仓库（如果存在）
if git remote | grep -q "github"; then
    echo -e "${YELLOW}移除旧的 GitHub 远程仓库...${NC}"
    git remote remove github
fi

# 添加 GitHub 远程仓库
echo -e "${YELLOW}[1/3] 添加 GitHub 远程仓库...${NC}"
git remote add github "$GITHUB_REPO"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ GitHub 远程仓库添加成功${NC}"
    echo -e "  URL: ${GITHUB_REPO}"
else
    echo -e "${RED}✗ GitHub 远程仓库添加失败${NC}"
    exit 1
fi

# 推送 master 分支
echo ""
echo -e "${YELLOW}[2/3] 推送 master 分支到 GitHub...${NC}"
git push github master

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ master 分支推送成功${NC}"
else
    echo -e "${RED}✗ master 分支推送失败${NC}"
    echo -e "${YELLOW}可能的原因:${NC}"
    echo -e "  1. GitHub 仓库还未创建，请先在 GitHub 上创建仓库"
    echo -e "  2. 仓库名称不正确，应该是: ${GITHUB_USERNAME}/dictation_for_pupil"
    echo -e "  3. 权限不足，请检查 GitHub 用户名和密码/token"
    echo ""
    echo -e "${YELLOW}请访问以下链接创建仓库:${NC}"
    echo -e "  ${BLUE}https://github.com/new${NC}"
    echo -e "  仓库名称: dictation_for_pupil"
    echo -e "  Visibility: Public"
    echo -e "  ${RED}不要勾选任何初始化选项${NC}"
    exit 1
fi

# 推送标签
echo ""
echo -e "${YELLOW}[3/3] 推送所有标签到 GitHub...${NC}"
TAGS=$(git tag)
if [ -z "$TAGS" ]; then
    echo -e "${YELLOW}! 没有标签，跳过${NC}"
else
    git push github --tags
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 所有标签推送成功${NC}"
    else
        echo -e "${RED}✗ 标签推送失败${NC}"
    fi
fi

# 显示结果
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  迁移完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}✓ 代码已成功推送到 GitHub${NC}"
echo ""
echo -e "${YELLOW}GitHub 仓库地址:${NC}"
echo -e "  ${BLUE}https://github.com/${GITHUB_USERNAME}/dictation_for_pupil${NC}"
echo ""
echo -e "${YELLOW}GitHub Actions 构建页面:${NC}"
echo -e "  ${BLUE}https://github.com/${GITHUB_USERNAME}/dictation_for_pupil/actions${NC}"
echo ""

echo -e "${YELLOW}后续操作:${NC}"
echo -e "1. 访问 GitHub Actions 页面查看构建进度"
echo -e "2. 等待构建完成（约 5-10 分钟）"
echo -e "3. 下载构建产物（Windows exe 和 Linux 可执行文件）"
echo ""

echo -e "${YELLOW}日常推送命令:${NC}"
echo -e "  推送到 Gitee: ${GREEN}git push origin master${NC}"
echo -e "  推送到 GitHub: ${GREEN}git push github master${NC}"
echo -e "  同时推送: ${GREEN}git push origin master && git push github master${NC}"
echo ""

echo -e "${GREEN}迁移完成！祝您使用愉快！${NC}"