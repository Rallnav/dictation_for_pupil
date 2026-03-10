#!/usr/bin/env python3
"""
听写软件终端界面
使用 Textual 库创建美观的终端界面
"""

import json
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Grid, Container
from textual.screen import Screen
from textual.widgets import (
    Label, Button, Checkbox, Input, Static, Select,
    DataTable, Tree, TextArea, Markdown
)
from textual.widgets.tree import TreeNode
from textual.reactive import var
from textual import events

from dictation import DictationEngine
from group_manager import GroupManager
import threading


class DictationApp(App):
    """听写软件终端界面应用"""
    
    CSS = """
    /* 全局样式 */
    App {
        background: #0a1929;
        color: #e6f1ff;
    }
    
    /* 标题栏 */
    Header {
        background: #112d4e;
        color: #a8d8ea;
        height: 3;
    }
    
    /* 状态栏 */
    Footer {
        background: #112d4e;
        color: #a8d8ea;
        height: 3;
    }
    
    /* 按钮样式 */
    Button {
        background: #1a365d;
        color: #e6f1ff;
        border: solid #3182ce;
        height: 3;
    }
    
    Button:hover {
        background: #2c5282;
    }
    
    Button.pressed {
        background: #3182ce;
    }
    
    /* 输入框 */
    Input {
        background: #112d4e;
        color: #e6f1ff;
        border: solid #3182ce;
        height: 3;
        width: 30;
    }
    
    /* 复选框 */
    Checkbox {
        height: 3;
    }
    
    /* 表格 */
    DataTable {
        background: #112d4e;
        color: #e6f1ff;
        border: solid #3182ce;
        height: 10;
    }
    
    DataTable> .datatable--header {
        background: #1a365d;
    }
    
    /* 树状图 */
    Tree {
        background: #112d4e;
        color: #e6f1ff;
        border: solid #3182ce;
    }
    
    /* 文本区域 */
    TextArea {
        background: #112d4e;
        color: #e6f1ff;
        border: solid #3182ce;
    }
    
    /* 卡片样式 */
    .card {
        background: #112d4e;
        border: solid #3182ce;
        padding: 1;
        margin: 1;
    }
    
    .card-title {
        background: #1a365d;
        color: #a8d8ea;
        padding: 0 1;
    }
    
    /* Grid布局 */
    Grid {
        grid-size-columns: 5;
        grid-size-rows: 1;
    }
    
    /* 侧边栏 */
    .sidebar {
        width: 30;
        background: #112d4e;
        border-right: solid #3182ce;
    }
    
    /* 主内容区 */
    .main-content {
        width: 1fr;
    }
    
    /* 状态消息 */
    .status-message {
        color: #68d391;
    }
    
    .error-message {
        color: #fc8181;
    }
    """
    
    def __init__(self, config_path='config.json', **kwargs):
        super().__init__(**kwargs)
        self.config_path = Path(config_path)
        self.manager = GroupManager(config_path)
        self.engine = DictationEngine(config_path)
        self.status_message = ""
    
    def on_mount(self) -> None:
        """应用启动时调用"""
        self.push_screen(MainScreen(self))


class MainScreen(Screen):
    """主界面"""
    
    status_message = var("")
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
        self.engine = app.engine
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        # 侧边栏导航
        yield Horizontal(
            Container(
                Static("导航菜单", classes="card-title"),
                Button("开始听写", id="start-dictation"),
                Button("组别管理", id="group-management"),
                Button("系统设置", id="system-settings"),
                Button("预生成音频", id="preload-audio"),
                Button("退出", id="exit"),
                classes="sidebar"
            ),
            Container(
                Static("听写软件", classes="card-title"),
                Static("欢迎使用小学生听写软件！", classes="status-message"),
                Static(""),
                Static("功能特点："),
                Static("• 支持多个词汇组管理"),
                Static("• 高质量中文语音朗读"),
                Static("• 音频预生成，播放无延迟"),
                Static("• 多组混合随机听写"),
                Static(""),
                Static("请从左侧菜单选择功能", classes="status-message"),
                classes="main-content"
            )
        )
        
        # 状态栏
        yield Static("就绪", id="status-bar")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "start-dictation":
            self.main_app.push_screen(DictationScreen(self.main_app))
        elif event.button.id == "group-management":
            self.main_app.push_screen(GroupManagementScreen(self.main_app))
        elif event.button.id == "system-settings":
            self.main_app.push_screen(SettingsScreen(self.main_app))
        elif event.button.id == "preload-audio":
            self.main_app.push_screen(PreloadAudioScreen(self.main_app))
        elif event.button.id == "exit":
            self.main_app.exit()


class DictationScreen(Screen):
    """开始听写界面"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
        self.engine = app.engine
        self.selected_groups = list(self.manager.get_selected_groups())
        self.interval = self.manager.get_interval()
        self.repeat_count = self.manager.get_repeat_count()
        self.shuffle = True
        self.dictating = False
        self.stop_requested = False
        self.dictation_thread = None
    
    def compose(self) -> ComposeResult:
        """构建界面 - 简化布局"""
        yield Static("开始听写", classes="card-title")
        
        # 选择组别 - 简化表格
        yield Static("点击选择组别:")
        table = DataTable(id="group-table")
        table.add_columns("✓", "组别", "词汇")
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        groups = self.manager.get_groups()
        for group_id, group_info in groups.items():
            status = "✓" if group_id in self.selected_groups else ""
            name = group_info['name']
            preview = ", ".join(group_info['content'][:3])
            table.add_row(status, name, preview, key=group_id)
        yield table
        
        # 已选中的组别显示
        yield Static(f"已选: {self._get_selected_text()}", id="selected-groups")
        
        # 快捷操作按钮
        yield Horizontal(
            Button("全选", id="select-all"),
            Button("清空", id="select-none"),
            id="selection-buttons"
        )
        
        # 设置选项 - 使用Grid布局
        yield Grid(
            Static("间隔:"),
            Input(str(self.interval), id="interval", placeholder="秒"),
            Static("重复:"),
            Input(str(self.repeat_count), id="repeat-count", placeholder="次"),
            Checkbox("随机", value=True, id="shuffle"),
            id="settings-grid"
        )
        
        # 操作按钮
        yield Horizontal(
            Button("开始", id="start", variant="primary"),
            Button("返回", id="back"),
            id="action-buttons"
        )
        
        # 听写进度
        yield Static("等待开始...", id="progress-text")
    
    def _get_selected_text(self) -> str:
        """获取已选中的组别文本"""
        if not self.selected_groups:
            return "无"
        groups = self.manager.get_groups()
        names = [groups[gid]['name'] for gid in self.selected_groups if gid in groups]
        return ", ".join(names)
    
    def _update_table_selection(self):
        """更新表格中的选中状态显示"""
        table = self.query_one("#group-table", DataTable)
        # 获取第一列的 key（columns 是一个字典，获取第一个列的 key）
        status_column_key = list(table.columns.keys())[0]
        
        for row_key in table.rows:
            group_id = row_key.value
            status = "✓" if group_id in self.selected_groups else ""
            # 更新状态列
            table.update_cell(row_key, status_column_key, status)
        
        # 更新已选中的组别显示
        self.query_one("#selected-groups", Static).update(self._get_selected_text())
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "select-all":
            # 全选
            groups = self.manager.get_groups()
            self.selected_groups = list(groups.keys())
            self._update_table_selection()
            self.notify("已选择所有组别", severity="information")
        elif event.button.id == "select-none":
            # 全不选
            self.selected_groups = []
            self._update_table_selection()
            self.notify("已取消所有选择", severity="information")
        elif event.button.id == "start":
            if self.dictating:
                self.notify("听写正在进行中...", severity="warning")
                return
            
            try:
                interval = self.interval
                repeat_count = self.repeat_count
                shuffle = self.shuffle
                
                self.dictating = True
                self.query_one("#progress-text", Static).update("准备开始听写...")
                
                # 开始听写（在后台线程中执行，避免阻塞UI）
                self.dictation_thread = threading.Thread(
                    target=self._run_dictation_thread,
                    args=(interval, repeat_count, shuffle)
                )
                self.dictation_thread.daemon = True
                self.dictation_thread.start()
                
            except Exception as e:
                self.dictating = False
                self.query_one("#progress-text", Static).update(f"错误：{e}")
                self.notify(f"错误：{e}", severity="error")
        elif event.button.id == "back":
            # 如果有正在进行的听写，立即停止
            if self.dictating:
                self.stop_requested = True
                self.dictating = False
                # 强制终止音频播放进程
                try:
                    import subprocess
                    subprocess.run(['pkill', '-f', 'ffplay'], capture_output=True)
                except:
                    pass
                self.notify("已终止听写", severity="warning")
            self.main_app.pop_screen()
    
    def _run_dictation_thread(self, interval, repeat_count, shuffle):
        """在后台线程中运行听写"""
        try:
            self._run_dictation(interval, repeat_count, shuffle)
            self.app.call_from_thread(self._on_dictation_complete)
        except Exception as e:
            self.app.call_from_thread(self._on_dictation_error, str(e))
    
    def _on_dictation_complete(self):
        """听写完成回调"""
        self.dictating = False
        self.query_one("#progress-text", Static).update("听写完成！")
        self.notify("听写完成！", severity="information")
    
    def _on_dictation_error(self, error_msg):
        """听写错误回调"""
        self.dictating = False
        self.query_one("#progress-text", Static).update(f"错误：{error_msg}")
        self.notify(f"错误：{error_msg}", severity="error")
    
    def _run_dictation(self, interval, repeat_count, shuffle):
        """在后台线程中运行听写"""
        import time
        
        # 重置停止标志
        self.stop_requested = False
        
        if len(self.selected_groups) == 1:
            group_id = self.selected_groups[0]
            group_info = self.manager.get_group(group_id)
            content = group_info['content']
            
            # 预加载音频
            self._update_progress("预加载音频...")
            self.engine._preload_audio(content)
            
            if self.stop_requested:
                return
            
            if shuffle:
                content = content.copy()
                import random
                random.shuffle(content)
                self._update_progress("已随机打乱听写顺序")
            
            for i, text in enumerate(content, 1):
                if self.stop_requested:
                    break
                self._update_progress(f"[{i}/{len(content)}] {text}")
                for j in range(repeat_count):
                    if self.stop_requested:
                        break
                    self.engine.speak(text)
                    if j < repeat_count - 1:
                        time.sleep(interval)
                if i < len(content) and not self.stop_requested:
                    time.sleep(interval)
        else:
            all_content = []
            for group_id in self.selected_groups:
                group_info = self.manager.get_group(group_id)
                for text in group_info['content']:
                    all_content.append((text, group_id, group_info['name']))
            
            # 预加载音频
            self._update_progress("预加载音频...")
            all_text = [item[0] for item in all_content]
            self.engine._preload_audio(all_text)
            
            if self.stop_requested:
                return
            
            if shuffle:
                import random
                all_content = all_content.copy()
                random.shuffle(all_content)
                self._update_progress("已随机打乱听写顺序")
            
            for i, (text, group_id, group_name) in enumerate(all_content, 1):
                if self.stop_requested:
                    break
                self._update_progress(f"[{i}/{len(all_content)}] {text} [{group_name}]")
                for j in range(repeat_count):
                    if self.stop_requested:
                        break
                    self.engine.speak(text)
                    if j < repeat_count - 1:
                        time.sleep(interval)
                if i < len(all_content) and not self.stop_requested:
                    time.sleep(interval)
    
    def _update_progress(self, message):
        """更新进度显示（线程安全）"""
        self.app.call_from_thread(self._set_progress_text, message)
    
    def _set_progress_text(self, message):
        """设置进度文本"""
        try:
            progress_text = self.query_one("#progress-text", Static)
            progress_text.update(message)
        except:
            pass
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """处理表格行选择事件"""
        group_id = event.row_key.value
        
        if group_id in self.selected_groups:
            self.selected_groups.remove(group_id)
        else:
            self.selected_groups.append(group_id)
        
        # 更新表格显示
        self._update_table_selection()
    



class GroupManagementScreen(Screen):
    """组别管理界面"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("组别管理", classes="card-title")
        
        # 组别列表
        yield Static("现有组别：")
        table = DataTable(id="groups-table")
        table.add_columns("ID", "名称", "词汇数量", "词汇预览")
        table.zebra_stripes = True
        
        yield table
        
        # 操作按钮
        yield Horizontal(
            Button("添加组别", id="add-group"),
            Button("编辑组别", id="edit-group"),
            Button("删除组别", id="delete-group"),
            Button("返回", id="back")
        )
        
        yield Static("", id="status-bar")
    
    def on_mount(self) -> None:
        """界面挂载时填充数据"""
        table = self.query_one("#groups-table", DataTable)
        groups = self.manager.get_groups()
        for group_id, group_info in groups.items():
            preview = ", ".join(group_info['content'][:5])
            if len(group_info['content']) > 5:
                preview += "..."
            table.add_row(group_id, group_info['name'], str(len(group_info['content'])), preview)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "add-group":
            self.main_app.push_screen(AddGroupScreen(self.main_app))
        elif event.button.id == "edit-group":
            # 获取选中的组别
            table = self.query_one("#groups-table", DataTable)
            if table.cursor_row is not None:
                group_id = table.get_row_at(table.cursor_row)[0]
                self.main_app.push_screen(EditGroupScreen(self.main_app, group_id))
        elif event.button.id == "delete-group":
            # 获取选中的组别
            table = self.query_one("#groups-table", DataTable)
            if table.cursor_row is not None:
                group_id = table.get_row_at(table.cursor_row)[0]
                try:
                    self.manager.delete_group(group_id)
                    self.query_one("#status-bar", Static).update(f"已删除组别：{group_id}")
                    # 刷新当前界面的表格
                    table.clear()
                    groups = self.manager.get_groups()
                    for group_id, group_info in groups.items():
                        preview = ", ".join(group_info['content'][:5])
                        if len(group_info['content']) > 5:
                            preview += "..."
                        table.add_row(group_id, group_info['name'], str(len(group_info['content'])), preview)
                except Exception as e:
                    self.query_one("#status-bar", Static).update(f"错误：{e}")
        elif event.button.id == "back":
            self.main_app.pop_screen()


class AddGroupScreen(Screen):
    """添加组别界面"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("添加组别", classes="card-title")
        
        yield Static("组别ID：")
        yield Input(id="group-id")
        
        yield Static("组别名称：")
        yield Input(id="group-name")
        
        yield Static("词汇（用逗号分隔）：")
        yield TextArea(id="group-content")
        
        yield Horizontal(
            Button("保存", id="save"),
            Button("取消", id="cancel")
        )
        
        yield Static("", id="status-bar")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "save":
            group_id = self.query_one("#group-id", Input).value
            group_name = self.query_one("#group-name", Input).value
            group_content = self.query_one("#group-content", TextArea).text
            
            if not group_id or not group_name or not group_content:
                self.query_one("#status-bar", Static).update("错误：所有字段都不能为空")
                return
            
            try:
                content = [item.strip() for item in group_content.replace('，', ',').split(',')]
                self.manager.add_group(group_id, group_name, content)
                self.query_one("#status-bar", Static).update(f"已添加组别：{group_name}")
                # 刷新组别管理界面
                self.main_app.pop_screen()
                self.main_app.push_screen(GroupManagementScreen(self.main_app))
            except Exception as e:
                self.query_one("#status-bar", Static).update(f"错误：{e}")
        elif event.button.id == "cancel":
            self.main_app.pop_screen()


class EditGroupScreen(Screen):
    """编辑组别界面"""
    
    def __init__(self, app, group_id, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
        self.group_id = group_id
        self.group_info = self.manager.get_group(group_id)
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("编辑组别", classes="card-title")
        
        yield Static("组别ID：")
        yield Input(self.group_id, id="group-id", disabled=True)
        
        yield Static("组别名称：")
        yield Input(self.group_info['name'], id="group-name")
        
        yield Static("词汇（用逗号分隔）：")
        content_text = ','.join(self.group_info['content'])
        yield TextArea(content_text, id="group-content")
        
        yield Horizontal(
            Button("保存", id="save"),
            Button("取消", id="cancel")
        )
        
        yield Static("", id="status-bar")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "save":
            group_name = self.query_one("#group-name", Input).value
            group_content = self.query_one("#group-content", TextArea).text
            
            if not group_name or not group_content:
                self.query_one("#status-bar", Static).update("错误：名称和内容不能为空")
                return
            
            try:
                content = [item.strip() for item in group_content.replace('，', ',').split(',')]
                self.manager.update_group(self.group_id, name=group_name, content=content)
                self.query_one("#status-bar", Static).update(f"已更新组别：{group_name}")
                # 刷新组别管理界面
                self.main_app.pop_screen()
                self.main_app.push_screen(GroupManagementScreen(self.main_app))
            except Exception as e:
                self.query_one("#status-bar", Static).update(f"错误：{e}")
        elif event.button.id == "cancel":
            self.main_app.pop_screen()


class SettingsScreen(Screen):
    """系统设置界面"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
        self.config = self.manager.config
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.manager = app.manager
        self.config = self.manager.config
        self.selected_groups = list(self.config.get('selected_groups', []))
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("系统设置", classes="card-title")
        
        # 默认设置
        yield Static("默认设置：")
        yield Static("默认间隔时间（秒）：")
        yield Input(str(self.config.get('interval', 3)), id="interval")
        
        yield Static("默认重复次数：")
        yield Input(str(self.config.get('repeat_count', 2)), id="repeat-count")
        
        # 默认选中的组别 - 使用表格形式
        yield Static("点击选择默认组别：")
        table = DataTable(id="settings-group-table")
        table.add_columns("✓", "组别", "数量", "词汇预览")
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        groups = self.manager.get_groups()
        for group_id, group_info in groups.items():
            status = "✓" if group_id in self.selected_groups else ""
            name = group_info['name']
            count = str(len(group_info['content']))
            preview = ", ".join(group_info['content'][:3])
            if len(group_info['content']) > 3:
                preview += "..."
            table.add_row(status, name, count, preview, key=group_id)
        yield table
        
        # 已选中的组别显示
        yield Static(f"已选: {self._get_selected_text()}", id="settings-selected-groups")
        
        # 快捷操作按钮
        yield Horizontal(
            Button("全选", id="select-all"),
            Button("清空", id="select-none"),
            id="settings-selection-buttons"
        )
        
        # 操作按钮
        yield Horizontal(
            Button("保存", id="save"),
            Button("取消", id="cancel")
        )
        
        yield Static("", id="status-bar")
    
    def _get_selected_text(self) -> str:
        """获取已选中的组别文本"""
        if not self.selected_groups:
            return "无"
        groups = self.manager.get_groups()
        names = [groups[gid]['name'] for gid in self.selected_groups if gid in groups]
        return ", ".join(names)
    
    def _update_table_selection(self):
        """更新表格中的选中状态显示"""
        table = self.query_one("#settings-group-table", DataTable)
        status_column_key = list(table.columns.keys())[0]
        
        for row_key in table.rows:
            group_id = row_key.value
            status = "✓" if group_id in self.selected_groups else ""
            table.update_cell(row_key, status_column_key, status)
        
        # 更新已选中的组别显示
        self.query_one("#settings-selected-groups", Static).update(self._get_selected_text())
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """处理表格行选择事件"""
        table = self.query_one("#settings-group-table", DataTable)
        group_id = event.row_key.value
        
        if group_id in self.selected_groups:
            self.selected_groups.remove(group_id)
        else:
            self.selected_groups.append(group_id)
        
        self._update_table_selection()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "select-all":
            groups = self.manager.get_groups()
            self.selected_groups = list(groups.keys())
            self._update_table_selection()
        elif event.button.id == "select-none":
            self.selected_groups = []
            self._update_table_selection()
        elif event.button.id == "save":
            interval_input = self.query_one("#interval", Input)
            repeat_input = self.query_one("#repeat-count", Input)
            
            try:
                interval = int(interval_input.value)
                repeat_count = int(repeat_input.value)
                
                # 更新配置
                self.config['interval'] = interval
                self.config['repeat_count'] = repeat_count
                self.config['selected_groups'] = self.selected_groups
                
                # 保存配置
                self.manager.save_config()
                
                self.query_one("#status-bar", Static).update("设置已保存")
                self.main_app.pop_screen()
            except Exception as e:
                self.query_one("#status-bar", Static).update(f"错误：{e}")
        elif event.button.id == "cancel":
            self.main_app.pop_screen()


class PreloadAudioScreen(Screen):
    """预生成音频界面"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = app
        self.engine = app.engine
        self.manager = app.manager
        self.preloading = False
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("预生成音频", classes="card-title")
        yield Static("正在预生成所有音频...", classes="status-message")
        yield Static("", id="progress-text")
        yield Static("这可能需要一些时间，请耐心等待...")
        yield Static("")
        yield Button("返回", id="back")
        yield Static("", id="status-bar")
    
    def on_mount(self) -> None:
        """界面挂载时执行"""
        self.preloading = True
        self._start_preload()
    
    def _start_preload(self):
        """在后台线程中预生成音频"""
        import threading
        thread = threading.Thread(target=self._preload_audio_thread)
        thread.daemon = True
        thread.start()
    
    def _preload_audio_thread(self):
        """后台线程执行音频预生成"""
        try:
            groups = self.manager.get_groups()
            all_content = []
            for group_id, group_info in groups.items():
                all_content.extend(group_info['content'])
            
            if not all_content:
                self._update_status("配置文件中没有词汇")
                self.preloading = False
                return
            
            total = len(all_content)
            self._update_status(f"开始生成 {total} 个音频...")
            
            for i, text in enumerate(all_content, 1):
                if not self.preloading:
                    break
                
                self._update_progress(f"[{i}/{total}] {text}")
                self.engine._generate_audio(text)
            
            if self.preloading:
                self.engine._cleanup_unused_audio(all_content)
                self._update_status("音频预生成完成")
            
            self.preloading = False
        except Exception as e:
            import traceback
            error_msg = f"错误：{e}\n{traceback.format_exc()}"
            self._update_status(error_msg)
            self.preloading = False
    
    def _update_progress(self, message):
        """更新进度显示（线程安全）"""
        self.main_app.call_from_thread(self._set_progress_text, message)
    
    def _set_progress_text(self, message):
        """设置进度文本"""
        try:
            progress_text = self.query_one("#progress-text", Static)
            progress_text.update(message)
        except:
            pass
    
    def _update_status(self, message):
        """更新状态显示（线程安全）"""
        self.main_app.call_from_thread(self._set_status_text, message)
    
    def _set_status_text(self, message):
        """设置状态文本"""
        try:
            status_bar = self.query_one("#status-bar", Static)
            status_bar.update(message)
        except:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "back":
            self.preloading = False
            self.main_app.pop_screen()


if __name__ == "__main__":
    app = DictationApp()
    app.run()