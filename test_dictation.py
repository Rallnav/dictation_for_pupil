#!/usr/bin/env python3
"""
DictationEngine 单元测试
"""

import unittest
from pathlib import Path
import tempfile
import json
from dictation import DictationEngine


class TestDictationEngine(unittest.TestCase):
    """DictationEngine 测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.json"
        
        # 写入测试配置
        config_data = {
            "groups": {
                "test": {
                    "name": "测试组",
                    "content": ["测试1", "测试2"]
                }
            },
            "interval": 3,
            "repeat_count": 2,
            "selected_groups": ["test"]
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 创建测试引擎
        self.engine = DictationEngine(str(self.config_path))
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.engine, DictationEngine)
        self.assertTrue(self.engine.cache_dir.exists())
    
    def test_get_audio_filename(self):
        """测试获取音频文件名"""
        test_text = "测试文本"
        filename = self.engine._get_audio_filename(test_text)
        self.assertEqual(filename, "测试文本.mp3")
        
        # 测试特殊字符
        test_text = "test/|?*<>&"
        filename = self.engine._get_audio_filename(test_text)
        self.assertTrue(filename.startswith("test"))
        self.assertTrue(filename.endswith(".mp3"))
    
    def test_get_audio_path(self):
        """测试获取音频文件路径"""
        test_text = "测试"
        audio_path = self.engine._get_audio_path(test_text)
        expected_path = self.engine.cache_dir / "测试.mp3"
        self.assertEqual(audio_path, expected_path)
    
    def test_cleanup_unused_audio(self):
        """测试清理未使用的音频文件"""
        # 创建测试音频文件
        (self.engine.cache_dir / "test1.mp3").write_text("test")
        (self.engine.cache_dir / "test2.mp3").write_text("test")
        
        # 清理未使用的音频
        self.engine._cleanup_unused_audio(["test1"])
        
        # 验证结果
        self.assertTrue((self.engine.cache_dir / "test1.mp3").exists())
        self.assertFalse((self.engine.cache_dir / "test2.mp3").exists())
    
    def test_get_config_hash(self):
        """测试获取配置文件哈希"""
        hash1 = self.engine._get_config_hash()
        # 修改配置文件
        with open(self.config_path, 'a') as f:
            f.write(" ")
        hash2 = self.engine._get_config_hash()
        self.assertNotEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()
