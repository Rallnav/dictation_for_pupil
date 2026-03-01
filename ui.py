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
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("开始听写", classes="card-title")
        
        # 选择组别
        yield Static("选择要听写的组别：")
        tree = Tree("组别列表")
        groups = self.manager.get_groups()
        for group_id, group_info in groups.items():
            node = tree.root.add(group_info['name'], data=group_id)
            node.expanded = True
        yield tree
        
        # 设置选项
        yield Static("设置：")
        yield Grid(
            Input(str(self.interval), id="interval", placeholder="间隔时间（秒）"),
            Input(str(self.repeat_count), id="repeat-count", placeholder="重复次数"),
            Checkbox("随机顺序", value=True, id="shuffle"),
            id="settings-grid"
        )
        
        # 操作按钮
        yield Horizontal(
            Button("开始", id="start"),
            Button("返回", id="back")
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "start":
            # 获取设置
            interval_input = self.query_one("#interval", Input)
            repeat_input = self.query_one("#repeat-count", Input)
            shuffle_checkbox = self.query_one("#shuffle", Checkbox)
            
            try:
                interval = int(interval_input.value)
                repeat_count = int(repeat_input.value)
                shuffle = shuffle_checkbox.value
                
                # 开始听写
                if len(self.selected_groups) == 1:
                    group_id = self.selected_groups[0]
                    group_info = self.manager.get_group(group_id)
                    content = group_info['content']
                    self.engine.dictate(content, interval, repeat_count, shuffle)
                else:
                    all_content = []
                    for group_id in self.selected_groups:
                        group_info = self.manager.get_group(group_id)
                        for text in group_info['content']:
                            all_content.append((text, group_id, group_info['name']))
                    self.engine.dictate_mixed(all_content, interval, repeat_count, shuffle)
                
                # 显示完成消息
                self.query_one("#status-bar", Static).update("听写完成！")
            except Exception as e:
                self.query_one("#status-bar", Static).update(f"错误：{e}")
        elif event.button.id == "back":
            self.main_app.pop_screen()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """处理树节点选择事件"""
        if event.node.data:
            group_id = event.node.data
            if group_id in self.selected_groups:
                self.selected_groups.remove(group_id)
            else:
                self.selected_groups.append(group_id)


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
        table.add_columns("ID", "名称", "词汇数量")
        
        yield table
        
        # 操作按钮
        yield Horizontal(
            Button("添加组别", id="add-group"),
            Button("编辑组别", id="edit-group"),
            Button("删除组别", id="delete-group"),
            Button("返回", id="back")
        )
    
    def on_mount(self) -> None:
        """界面挂载时填充数据"""
        table = self.query_one("#groups-table", DataTable)
        groups = self.manager.get_groups()
        for group_id, group_info in groups.items():
            table.add_row(group_id, group_info['name'], str(len(group_info['content'])))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "add-group":
            self.main_app.push_screen(AddGroupScreen(self.main_app))
        elif event.button.id == "edit-group":
            # 获取选中的组别
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                group_id = table.get_row_at(table.cursor_row)[0]
                self.main_app.push_screen(EditGroupScreen(self.main_app, group_id))
        elif event.button.id == "delete-group":
            # 获取选中的组别
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                group_id = table.get_row_at(table.cursor_row)[0]
                try:
                    self.manager.delete_group(group_id)
                    self.query_one("#status-bar", Static).update(f"已删除组别：{group_id}")
                    # 刷新界面
                    self.main_app.push_screen(GroupManagementScreen(self.main_app))
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
                content = [item.strip() for item in group_content.split(',')]
                self.manager.add_group(group_id, group_name, content)
                self.query_one("#status-bar", Static).update(f"已添加组别：{group_name}")
                self.main_app.pop_screen()
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
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "save":
            group_name = self.query_one("#group-name", Input).value
            group_content = self.query_one("#group-content", TextArea).text
            
            if not group_name or not group_content:
                self.query_one("#status-bar", Static).update("错误：名称和内容不能为空")
                return
            
            try:
                content = [item.strip() for item in group_content.split(',')]
                self.manager.update_group(self.group_id, name=group_name, content=content)
                self.query_one("#status-bar", Static).update(f"已更新组别：{group_name}")
                self.main_app.pop_screen()
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
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("系统设置", classes="card-title")
        
        # 默认设置
        yield Static("默认设置：")
        yield Static("默认间隔时间（秒）：")
        yield Input(str(self.config.get('interval', 3)), id="interval")
        
        yield Static("默认重复次数：")
        yield Input(str(self.config.get('repeat_count', 2)), id="repeat-count")
        
        # 默认选中的组别
        yield Static("默认选中的组别：")
        tree = Tree("组别列表")
        groups = self.manager.get_groups()
        selected_groups = set(self.config.get('selected_groups', []))
        
        for group_id, group_info in groups.items():
            node = tree.root.add(f"{group_info['name']} {'✓' if group_id in selected_groups else ''}", data=group_id)
            node.expanded = True
        
        yield tree
        
        # 操作按钮
        yield Horizontal(
            Button("保存", id="save"),
            Button("取消", id="cancel")
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "save":
            interval_input = self.query_one("#interval", Input)
            repeat_input = self.query_one("#repeat-count", Input)
            
            try:
                interval = int(interval_input.value)
                repeat_count = int(repeat_input.value)
                
                # 更新配置
                self.config['interval'] = interval
                self.config['repeat_count'] = repeat_count
                
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
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        yield Static("预生成音频", classes="card-title")
        yield Static("正在预生成所有音频...", classes="status-message")
        yield Static("")
        yield Static("这可能需要一些时间，请耐心等待...")
        yield Static("")
        yield Button("返回", id="back")
        yield Static("", id="status-bar")
    
    def on_mount(self) -> None:
        """界面挂载时执行"""
        # 预生成音频
        self.engine.preload_all_audio(self.manager)
        self.query_one("#status-bar", Static).update("音频预生成完成")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "back":
            self.main_app.pop_screen()


if __name__ == "__main__":
    app = DictationApp()
    app.run()