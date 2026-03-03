# dictation_for_pupil

#### 介绍
本项目是一个为小学生听写设计的软件，支持自定义词汇组、重复播放、间隔设置等功能。使用 edge-tts 提供高质量的中文语音朗读。

#### 功能特点
- 支持多个词汇组管理
- 可自定义播放间隔和重复次数
- 高质量中文语音（使用 edge-tts）
- 音频预生成，播放无延迟
- 配置文件管理，方便维护
- 多组听写时自动混合随机
- 美观的终端界面（基于 Textual）

#### 安装教程

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd dictation_for_pupil
   ```

2. **创建虚拟环境**（可选但推荐）
   ```bash
   python3 -m venv .venv_dictation
   source .venv_dictation/bin/activate
   ```

3. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置词汇组**
   编辑 `config.json` 文件，添加你的词汇组。

#### 使用说明

1. **启动终端界面**（推荐）
   ```bash
   # 启动美观的终端界面
   python ui.py
   ```

2. **命令行使用**（高级用户）
   ```bash
   # 使用配置文件中设置的组别
   python main.py
   ```

3. **指定组别**
   ```bash
   # 指定一个组别（单组随机）
   python main.py -g group1

   # 指定多个组别（多组混合随机）
   python main.py -g group1 group2 group3
   ```

4. **自定义间隔和次数**
   ```bash
   # 设置间隔为 5 秒，重复 3 次
   python main.py -i 5 -r 3
   ```

5. **列出所有组别**
   ```bash
   python main.py --list
   ```

6. **添加新组别**
   ```bash
   # 添加组别：ID 为 math，名称为数学，内容为"加法,减法,乘法,除法"
   python main.py --add-group math 数学 "加法,减法,乘法,除法"
   ```

7. **删除组别**
   ```bash
   python main.py --delete-group math
   ```

8. **设置默认听写组别**
   ```bash
   python main.py --set-groups group1 group2
   ```

9. **不随机打乱听写顺序**
   ```bash
   # 默认随机顺序，使用 --no-shuffle 保持原顺序
   python main.py -g group1 --no-shuffle
   ```

10. **预生成所有音频**
    ```bash
    # 一次性生成配置文件中所有词汇的音频
    python main.py --preload-all
    ```

#### 配置文件说明

`config.json` 文件结构：

```json
{
  "groups": {
    "group1": {
      "name": "第一组",
      "content": ["词汇1", "词汇2", "词汇3"]
    }
  },
  "selected_groups": ["group1"],
  "interval": 3,
  "repeat_count": 2
}
```

- `groups`: 词汇组字典
  - `name`: 组别名称
  - `content`: 词汇列表
- `selected_groups`: 默认听写的组别列表
- `interval`: 每个词汇重复播放之间的间隔（秒）
- `repeat_count`: 每个词汇重复播放的次数

#### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-c, --config` | 配置文件路径 | `-c my_config.json` |
| `-g, --group` | 指定听写组别 | `-g group1 group2` |
| `-i, --interval` | 听写间隔（秒） | `-i 5` |
| `-r, --repeat` | 听写次数 | `-r 3` |
| `--list` | 列出所有组别 | `--list` |
| `--add-group` | 添加新组别 | `--add-group ID NAME CONTENT` |
| `--delete-group` | 删除组别 | `--delete-group ID` |
| `--set-groups` | 设置默认听写组别 | `--set-groups ID1 ID2` |
| `--no-shuffle` | 不随机打乱听写顺序（默认随机） | `--no-shuffle` |
| `--preload-all` | 预生成所有音频 | `--preload-all` |

#### 音频缓存

- 音频文件缓存在配置文件所在目录的 `.dictation_cache/` 文件夹中
- 程序会自动检测配置文件变化，只在需要时重新生成音频
- 首次运行或配置文件变化时会预生成所有音频
- 使用 `--preload-all` 参数可以一次性生成所有配置文件中的音频
- 编辑或删除词汇后，音频文件会自动更新或清理

#### 打包成 exe

**打包说明**：

本项目支持打包成 Windows 可执行文件（exe），方便在没有 Python 环境的电脑上使用。

**快速打包（Windows，无需安装 Python）**：

1. **下载项目源码**
   ```bash
   git clone <repository-url>
   cd dictation_for_pupil
   ```

2. **运行自动打包脚本**
   ```cmd
   build_auto.bat
   ```
   
   脚本会自动：
   - 下载便携版 Python（约 10MB）
   - 安装所有依赖
   - 打包成 exe 文件
   - 清理临时文件

3. **打包产物**
   - `dist/听写软件.exe` - 主程序文件
   - `dist/使用说明.txt` - 用户使用说明

**手动打包（Windows）**：

详细步骤请参考：[BUILD_WINDOWS.md](BUILD_WINDOWS.md)

**使用 GitHub Actions 自动打包**：

1. 推送代码到 GitHub
2. 进入 Actions 页面查看构建进度
3. 构建完成后下载 exe 文件

**系统要求**：

- Windows 10 或更高版本
- 无需安装额外依赖

**注意事项**：

1. 打包后的 exe 文件包含所有依赖，用户无需安装任何额外软件
2. 打包后的 exe 文件会自动创建配置文件和音频缓存目录
3. 首次运行时会生成所有音频文件，可能需要一些时间

#### 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

#### 许可证

MIT License