# 听写软件 - 微信小程序版本

基于 UniApp 框架开发的微信小程序版本，支持听写练习、组别管理和文字识别功能。

## 功能特性

### 🎧 听写练习
- 多个组别选择
- 可调间隔时间和重复次数
- 随机打乱顺序
- 长词自动延长
- 暂停/继续/停止控制

### 📁 组别管理
- 创建、编辑、删除组别
- 导入/导出 JSON 数据
- 本地数据持久化

### 📷 文字识别 (OCR)
- 摄像头拍照识别
- 相册选择图片
- 识别结果添加到组别
- 支持创建新组别

### ⚙️ 系统设置
- 后台模式开关
- 语音类型选择
- 默认听写参数
- 数据管理

## 技术栈

- **框架**：UniApp + Vue 3
- **平台**：微信小程序
- **数据存储**：本地存储 (localStorage)
- **语音合成**：百度 TTS API

## 项目结构

```
miniapp/
├── pages/
│   ├── dictation/      # 听写页面
│   │   └── index.vue
│   ├── groups/         # 组别管理
│   │   └── index.vue
│   ├── settings/       # 系统设置
│   │   └── index.vue
│   └── ocr/            # 文字识别
│       └── index.vue
├── static/
│   └── tabbar/         # TabBar 图标
├── App.vue             # 主应用
├── main.js             # 入口文件
├── manifest.json       # 应用配置
├── package.json        # 依赖配置
└── pages.json          # 页面配置
```

## 开发环境

### 前置要求
- Node.js >= 16
- npm 或 yarn
- 微信开发者工具

### 安装依赖

```bash
cd miniapp
npm install
```

### 运行开发

```bash
# 微信小程序
npm run dev:mp-weixin

# 使用 HBuilderX
# 导入项目后，选择运行到小程序模拟器
```

### 构建发布

```bash
# 构建微信小程序
npm run build:mp-weixin

# 导出到 dist/build/mp-weixin 目录
# 使用微信开发者工具导入进行发布
```

## 配置说明

### 1. 获取 AppID

1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 注册小程序账号
3. 获取 AppID 并填入 `manifest.json`

### 2. 后台服务配置

在"系统设置"中启用后台模式，配置服务器地址：

- 默认地址：`http://localhost:8000`
- 需要与后端服务 `python3 main.py --start-api` 配合使用

### 3. OCR 功能

OCR 功能需要后台服务支持，请确保：
1. 启用后台模式
2. 正确配置服务器地址
3. 后端服务已启动并实现了 `/api/ocr` 接口

## 与其他端共享服务

本小程序与 H5 前端、后端服务共用同一套业务逻辑：

- **H5 前端**：`web/` 目录
- **小程序**：`miniapp/` 目录
- **后端服务**：`services/` 目录

数据通过 REST API 同步，确保多端数据一致性。

## 开源协议

本项目使用 MIT License

第三方依赖：
- **Tesseract.js** - Apache License 2.0 - 用于文字识别功能

详细许可证信息请参见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)