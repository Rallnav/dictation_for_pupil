#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 double.json 中的组别 ID
"""

import json
from pathlib import Path


def check_double_json():
    """检查 double.json 中的组别 ID"""
    print("检查 double.json 中的组别 ID")
    print("=" * 50)
    
    # 加载 double.json
    double_file = Path('../groups/double.json')
    if not double_file.exists():
        print("double.json 不存在")
        return
    
    with open(double_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    if 'groups' not in content:
        print("double.json 中没有 groups 键")
        return
    
    groups = content['groups']
    print(f"double.json 中有 {len(groups)} 个组别")
    
    # 加载 default.json
    default_file = Path('../groups/default.json')
    if default_file.exists():
        with open(default_file, 'r', encoding='utf-8') as f:
            default_content = json.load(f)
        
        if 'groups' in default_content:
            default_groups = default_content['groups']
            print(f"default.json 中有 {len(default_groups)} 个组别")
            
            # 检查重复的组别 ID
            double_group_ids = set(groups.keys())
            default_group_ids = set(default_groups.keys())
            duplicate_ids = double_group_ids.intersection(default_group_ids)
            
            print(f"\n重复的组别 ID: {len(duplicate_ids)}")
            if duplicate_ids:
                print("前10个重复的组别 ID:")
                for i, group_id in enumerate(list(duplicate_ids)[:10]):
                    print(f"  {group_id}")
            
            # 检查 double.json 中独有的组别 ID
            unique_ids = double_group_ids - default_group_ids
            print(f"\ndouble.json 中独有的组别 ID: {len(unique_ids)}")
            if unique_ids:
                print("独有的组别 ID:")
                for group_id in unique_ids:
                    print(f"  {group_id}: {groups[group_id]['name']}")
    
    print("\n" + "=" * 50)
    print("检查完成")


if __name__ == '__main__':
    check_double_json()
