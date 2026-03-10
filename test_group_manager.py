#!/usr/bin/env python3
"""
GroupManager 单元测试
"""

import unittest
from pathlib import Path
import tempfile
import json
from group_manager import GroupManager


class TestGroupManager(unittest.TestCase):
    """GroupManager 测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.json"
        
        # 写入测试配置
        config_data = {
            "groups": {
                "test1": {
                    "name": "测试组1",
                    "content": ["测试1", "测试2"]
                },
                "test2": {
                    "name": "测试组2",
                    "content": ["测试3", "测试4"]
                }
            },
            "interval": 3,
            "repeat_count": 2,
            "selected_groups": ["test1", "test2"],
            "default_group": "test1"
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 创建测试管理器
        self.manager = GroupManager(str(self.config_path))
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.manager, GroupManager)
        self.assertEqual(len(self.manager.get_groups()), 2)
    
    def test_get_groups(self):
        """测试获取所有组别"""
        groups = self.manager.get_groups()
        self.assertEqual(len(groups), 2)
        self.assertIn("test1", groups)
        self.assertIn("test2", groups)
    
    def test_get_group(self):
        """测试获取单个组别"""
        group = self.manager.get_group("test1")
        self.assertEqual(group["name"], "测试组1")
        self.assertEqual(group["content"], ["测试1", "测试2"])
    
    def test_add_group(self):
        """测试添加组别"""
        self.manager.add_group("test3", "测试组3", ["测试5", "测试6"])
        groups = self.manager.get_groups()
        self.assertEqual(len(groups), 3)
        self.assertIn("test3", groups)
    
    def test_update_group(self):
        """测试更新组别"""
        self.manager.update_group("test1", name="更新的测试组1", content=["更新1", "更新2"])
        group = self.manager.get_group("test1")
        self.assertEqual(group["name"], "更新的测试组1")
        self.assertEqual(group["content"], ["更新1", "更新2"])
    
    def test_delete_group(self):
        """测试删除组别"""
        self.manager.delete_group("test1")
        groups = self.manager.get_groups()
        self.assertEqual(len(groups), 1)
        self.assertNotIn("test1", groups)
    
    def test_delete_group_updates_selected_groups(self):
        """测试删除组别时更新 selected_groups"""
        self.manager.delete_group("test1")
        selected = self.manager.get_selected_groups()
        self.assertEqual(selected, ["test2"])
    
    def test_delete_group_resets_default_group(self):
        """测试删除组别时重置默认组别"""
        self.manager.delete_group("test1")
        default_group = self.manager.get_default_group()
        self.assertIsNone(default_group)
    
    def test_get_interval(self):
        """测试获取间隔时间"""
        self.assertEqual(self.manager.get_interval(), 3)
    
    def test_get_repeat_count(self):
        """测试获取重复次数"""
        self.assertEqual(self.manager.get_repeat_count(), 2)
    
    def test_get_selected_groups(self):
        """测试获取选中的组别"""
        selected = self.manager.get_selected_groups()
        self.assertEqual(selected, ["test1", "test2"])
    
    def test_set_selected_groups(self):
        """测试设置选中的组别"""
        self.manager.set_selected_groups(["test1"])
        selected = self.manager.get_selected_groups()
        self.assertEqual(selected, ["test1"])
    
    def test_set_default_group(self):
        """测试设置默认组别"""
        self.manager.set_default_group("test2")
        default_group = self.manager.get_default_group()
        self.assertEqual(default_group, "test2")


if __name__ == '__main__':
    unittest.main()
