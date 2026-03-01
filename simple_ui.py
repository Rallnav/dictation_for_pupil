#!/usr/bin/env python3
"""
简单的终端界面，使用 Rich 库
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.tree import Tree

from dictation import DictationEngine
from group_manager import GroupManager


class SimpleDictationUI:
    """简单的终端界面"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.manager = GroupManager(config_path)
        self.engine = DictationEngine(config_path)
        self.console = Console()
    
    def run(self):
        """运行界面"""
        while True:
            self.show_main_menu()
    
    def show_main_menu(self):
        """显示主菜单"""
        self.console.clear()
        
        # 标题
        self.console.print(
            Panel(
                "[bold cyan]小学生听写软件[/bold cyan]\n\n" +
                "[green]1. 开始听写[/green]\n" +
                "[green]2. 组别管理[/green]\n" +
                "[green]3. 系统设置[/green]\n" +
                "[green]4. 预生成音频[/green]\n" +
                "[green]5. 退出[/green]",
                title="[bold blue]主菜单[/bold blue]",
                border_style="blue"
            )
        )
        
        choice = Prompt.ask("请选择操作", choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            self.start_dictation()
        elif choice == "2":
            self.manage_groups()
        elif choice == "3":
            self.system_settings()
        elif choice == "4":
            self.preload_audio()
        elif choice == "5":
            self.console.print("[blue]再见！[/blue]")
            exit()
    
    def start_dictation(self):
        """开始听写"""
        self.console.clear()
        
        # 选择组别
        self.console.print(Panel("[bold cyan]选择要听写的组别[/bold cyan]", border_style="blue"))
        
        groups = self.manager.get_groups()
        selected_groups = []
        
        for group_id, group_info in groups.items():
            self.console.print(f"[green]{group_info['name']} ({len(group_info['content'])}个词汇)[/green]")
            self.console.print(f"[yellow]词汇: {', '.join(group_info['content'])}[/yellow]")
            if Confirm.ask(f"[blue]是否选择这个组别？[/blue]"):
                selected_groups.append(group_id)
            self.console.print()
        
        if not selected_groups:
            self.console.print("[red]请至少选择一个组别！[/red]")
            input("按回车键返回...")
            return
        
        # 设置参数
        interval = IntPrompt.ask("间隔时间（秒）", default=self.manager.get_interval())
        repeat_count = IntPrompt.ask("重复次数", default=self.manager.get_repeat_count())
        shuffle = Confirm.ask("随机顺序", default=True)
        
        # 开始听写
        self.console.clear()
        self.console.print("[bold green]开始听写...[/bold green]")
        
        if len(selected_groups) == 1:
            group_id = selected_groups[0]
            group_info = self.manager.get_group(group_id)
            content = group_info['content']
            self.engine.dictate(content, interval, repeat_count, shuffle)
        else:
            all_content = []
            for group_id in selected_groups:
                group_info = self.manager.get_group(group_id)
                for text in group_info['content']:
                    all_content.append((text, group_id, group_info['name']))
            self.engine.dictate_mixed(all_content, interval, repeat_count, shuffle)
        
        self.console.print("[bold green]听写完成！[/bold green]")
        input("按回车键返回...")
    
    def manage_groups(self):
        """组别管理"""
        while True:
            self.console.clear()
            
            # 显示组别列表
            self.console.print(Panel("[bold cyan]组别管理[/bold cyan]", border_style="blue"))
            
            groups = self.manager.get_groups()
            if groups:
                table = Table(title="现有组别", style="blue")
                table.add_column("ID", style="cyan")
                table.add_column("名称", style="green")
                table.add_column("词汇数量", style="yellow")
                
                for group_id, group_info in groups.items():
                    table.add_row(group_id, group_info['name'], str(len(group_info['content'])))
                
                self.console.print(table)
                
                # 显示每个组的具体词汇
                self.console.print("\n[bold blue]组别详情：[/bold blue]")
                for group_id, group_info in groups.items():
                    self.console.print(f"\n[green]{group_info['name']}[/green]")
                    self.console.print(f"[yellow]词汇: {', '.join(group_info['content'])}[/yellow]")
            else:
                self.console.print("[yellow]暂无组别，请添加组别[/yellow]")
            
            # 操作菜单
            self.console.print(
                "[green]1. 添加组别[/green]\n" +
                "[green]2. 编辑组别[/green]\n" +
                "[green]3. 删除组别[/green]\n" +
                "[green]4. 返回主菜单[/green]"
            )
            
            choice = Prompt.ask("请选择操作", choices=["1", "2", "3", "4"], default="4")
            
            if choice == "1":
                self.add_group()
            elif choice == "2":
                self.edit_group()
            elif choice == "3":
                self.delete_group()
            elif choice == "4":
                break
    
    def add_group(self):
        """添加组别"""
        self.console.clear()
        self.console.print(Panel("[bold cyan]添加组别[/bold cyan]", border_style="blue"))
        
        group_id = Prompt.ask("组别ID")
        group_name = Prompt.ask("组别名称")
        content_str = Prompt.ask("词汇（用逗号分隔）")
        
        content = [item.strip() for item in content_str.split(',')]
        
        try:
            self.manager.add_group(group_id, group_name, content)
            self.console.print("[green]组别添加成功！[/green]")
        except Exception as e:
            self.console.print(f"[red]错误：{e}[/red]")
        
        input("按回车键返回...")
    
    def edit_group(self):
        """编辑组别"""
        self.console.clear()
        self.console.print(Panel("[bold cyan]编辑组别[/bold cyan]", border_style="blue"))
        
        groups = self.manager.get_groups()
        if not groups:
            self.console.print("[yellow]暂无组别[/yellow]")
            input("按回车键返回...")
            return
        
        group_id = Prompt.ask("请输入要编辑的组别ID", choices=list(groups.keys()))
        group_info = groups[group_id]
        
        new_name = Prompt.ask("组别名称", default=group_info['name'])
        new_content_str = Prompt.ask("词汇（用逗号分隔）", default=",".join(group_info['content']))
        
        new_content = [item.strip() for item in new_content_str.split(',')]
        
        try:
            self.manager.update_group(group_id, name=new_name, content=new_content)
            self.console.print("[green]组别更新成功！[/green]")
        except Exception as e:
            self.console.print(f"[red]错误：{e}[/red]")
        
        input("按回车键返回...")
    
    def delete_group(self):
        """删除组别"""
        self.console.clear()
        self.console.print(Panel("[bold cyan]删除组别[/bold cyan]", border_style="blue"))
        
        groups = self.manager.get_groups()
        if not groups:
            self.console.print("[yellow]暂无组别[/yellow]")
            input("按回车键返回...")
            return
        
        group_id = Prompt.ask("请输入要删除的组别ID", choices=list(groups.keys()))
        
        if Confirm.ask("确定要删除这个组别吗？"):
            try:
                self.manager.delete_group(group_id)
                self.console.print("[green]组别删除成功！[/green]")
            except Exception as e:
                self.console.print(f"[red]错误：{e}[/red]")
        
        input("按回车键返回...")
    
    def system_settings(self):
        """系统设置"""
        self.console.clear()
        
        self.console.print(Panel("[bold cyan]系统设置[/bold cyan]", border_style="blue"))
        
        config = self.manager.config
        
        # 设置默认间隔
        interval = IntPrompt.ask("默认间隔时间（秒）", default=config.get('interval', 3))
        
        # 设置默认重复次数
        repeat_count = IntPrompt.ask("默认重复次数", default=config.get('repeat_count', 2))
        
        # 更新配置
        config['interval'] = interval
        config['repeat_count'] = repeat_count
        
        # 保存配置
        self.manager.save_config()
        
        self.console.print("[green]设置保存成功！[/green]")
        input("按回车键返回...")
    
    def preload_audio(self):
        """预生成音频"""
        self.console.clear()
        
        self.console.print(Panel("[bold cyan]预生成音频[/bold cyan]", border_style="blue"))
        self.console.print("正在预生成所有音频，请耐心等待...")
        
        try:
            self.engine.preload_all_audio(self.manager)
            self.console.print("[green]音频预生成完成！[/green]")
        except Exception as e:
            self.console.print(f"[red]错误：{e}[/red]")
        
        input("按回车键返回...")


if __name__ == "__main__":
    ui = SimpleDictationUI()
    ui.run()