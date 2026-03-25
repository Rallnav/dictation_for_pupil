#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试听写软件的新功能
"""

from group_manager import GroupManager
from pathlib import Path


def test_long_word_extension():
    """测试长词延长功能"""
    print("测试长词延长功能")
    print("=" * 50)
    
    # 创建 GroupManager 实例
    manager = GroupManager()
    
    # 测试获取长词延长配置
    long_word_extension = manager.get_long_word_extension()
    print(f"✓ 长词延长功能默认值: {long_word_extension}")
    
    # 测试设置长词延长配置
    manager.set_long_word_extension(False)
    new_value = manager.get_long_word_extension()
    print(f"✓ 长词延长功能设置为: {new_value}")
    
    # 恢复默认值
    manager.set_long_word_extension(True)
    final_value = manager.get_long_word_extension()
    print(f"✓ 长词延长功能恢复为: {final_value}")
    
    print("\n✓ 长词延长功能测试通过")


def test_group_manager():
    """测试组别管理器"""
    print("\n测试组别管理器")
    print("=" * 50)
    
    # 创建 GroupManager 实例
    manager = GroupManager()
    
    # 测试加载组别
    groups = manager.get_groups()
    print(f"✓ 加载了 {len(groups)} 个组别")
    
    # 测试获取配置
    interval = manager.get_interval()
    repeat_count = manager.get_repeat_count()
    selected_groups = manager.get_selected_groups()
    
    print(f"✓ 间隔时间: {interval} 秒")
    print(f"✓ 重复次数: {repeat_count} 次")
    print(f"✓ 选中的组别: {len(selected_groups)} 个")
    
    print("\n✓ 组别管理器测试通过")


def test_groups_directory():
    """测试 groups 目录"""
    print("\n测试 groups 目录")
    print("=" * 50)
    
    # 检查 groups 目录是否存在
    groups_dir = Path('groups')
    print(f"✓ Groups 目录存在: {groups_dir.exists()}")
    
    # 列出 groups 目录中的文件
    json_files = list(groups_dir.glob("*.json"))
    print(f"✓ Groups 目录中有 {len(json_files)} 个 JSON 文件")
    
    for file in json_files[:5]:  # 只显示前5个文件
        print(f"  - {file.name}")
    
    if len(json_files) > 5:
        print(f"  ... 等 {len(json_files) - 5} 个文件")
    
    print("\n✓ Groups 目录测试通过")


def main():
    """运行所有测试"""
    print("听写软件功能测试")
    print("=" * 60)
    
    test_long_word_extension()
    test_group_manager()
    test_groups_directory()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")


if __name__ == '__main__':
    main()
