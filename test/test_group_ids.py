#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重复的组别 ID 处理
"""

import sys
sys.path.insert(0, '../')
from services import GroupService


def test_group_ids():
    """测试重复的组别 ID 处理"""
    print("测试重复的组别 ID 处理")
    print("=" * 50)
    
    # 创建 GroupService 实例
    service = GroupService(groups_dir="../groups")
    
    # 测试加载组别
    groups = service.get_groups()
    print(f"✓ 加载了 {len(groups)} 个组别")
    
    # 统计重复的原始组别 ID
    original_group_ids = {}
    for group_id in groups.keys():
        # 提取原始组别 ID（去掉后缀）
        if '_' in group_id:
            original_id = group_id.split('_')[0]
        else:
            original_id = group_id
        
        if original_id not in original_group_ids:
            original_group_ids[original_id] = []
        original_group_ids[original_id].append(group_id)
    
    print(f"\n原始组别 ID 数量: {len(original_group_ids)}")
    
    # 显示有重复的组别 ID
    print("\n有重复的组别 ID:")
    duplicate_count = 0
    for original_id, group_ids in original_group_ids.items():
        if len(group_ids) > 1:
            duplicate_count += 1
            print(f"  {original_id}: {len(group_ids)} 个实例")
            for group_id in group_ids:
                source_file = groups[group_id].get('source_file', 'unknown')
                print(f"    - {group_id} (来自: {source_file})")
    
    print(f"\n共有 {duplicate_count} 个重复的原始组别 ID")
    
    # 测试添加新组别
    print("\n测试添加新组别:")
    new_group_id = service.add_group('group1', '新测试组别', ['测试1', '测试2'])
    print(f"✓ 成功添加组别，新的组别 ID: {new_group_id}")
    
    # 重新加载并检查
    new_service = GroupService(groups_dir="../groups")
    new_groups = new_service.get_groups()
    print(f"✓ 重新加载后共有 {len(new_groups)} 个组别")
    
    # 清理测试组别
    if new_group_id in new_groups:
        new_service.delete_group(new_group_id)
        print(f"✓ 成功删除测试组别: {new_group_id}")
    
    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == '__main__':
    test_group_ids()
