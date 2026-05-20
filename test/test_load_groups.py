#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 GroupService 是否加载了所有文件
"""

import sys
sys.path.insert(0, '../')
from services import GroupService
from pathlib import Path


def test_load_groups():
    """测试加载所有群组文件"""
    print("测试加载所有群组文件")
    print("=" * 50)
    
    # 检查 groups 目录
    groups_dir = Path('../groups')
    print(f"Groups 目录绝对路径: {groups_dir.resolve()}")
    print(f"Groups 目录是否存在: {groups_dir.exists()}")
    
    # 列出 groups 目录中的所有文件
    print("\nGroups 目录中的文件:")
    for file in groups_dir.glob("*.json"):
        print(f"  - {file.name}")
        print(f"    大小: {file.stat().st_size} bytes")
    
    # 创建 GroupService 实例
    service = GroupService(groups_dir="../groups")
    
    # 测试加载组别
    groups = service.get_groups()
    print(f"\n✓ 加载了 {len(groups)} 个组别")
    
    # 查看文件映射
    print("\n文件映射:")
    file_groups = {}
    for group_id, file_path in service._group_file_map.items():
        file_name = file_path.name
        if file_name not in file_groups:
            file_groups[file_name] = []
        file_groups[file_name].append(group_id)
    
    for file_name, group_ids in file_groups.items():
        print(f"  {file_name}: {len(group_ids)} 个组别")
    
    # 检查是否加载了 double.json
    if 'double.json' in file_groups:
        print(f"\n✓ 成功加载了 double.json，包含 {len(file_groups['double.json'])} 个组别")
    else:
        print("\n✗ 没有加载 double.json")
        # 尝试手动加载 double.json
        double_file = groups_dir / 'double.json'
        if double_file.exists():
            print(f"\n尝试手动加载 double.json:")
            try:
                import json
                with open(double_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                print(f"  成功加载，类型: {type(content)}")
                if 'groups' in content:
                    print(f"  包含 groups 键，有 {len(content['groups'])} 个组别")
                else:
                    print(f"  不包含 groups 键")
            except Exception as e:
                print(f"  加载失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == '__main__':
    test_load_groups()
