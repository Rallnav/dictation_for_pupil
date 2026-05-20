"""
适配器层 - 保持向后兼容性

将新的服务层适配为旧的接口，以便现有代码可以继续使用。
"""

from services import GroupService, AudioService


class GroupManager:
    """GroupManager 适配器 - 保持与旧接口的兼容性"""
    
    def __init__(self, config_path="config.json", groups_dir="groups"):
        self.service = GroupService(config_path, groups_dir)
    
    def _load_config(self):
        """加载配置（兼容旧接口）"""
        return self.service._load_config()
    
    def _load_groups(self):
        """加载组别（兼容旧接口）"""
        self.service._load_groups()
    
    def save_config(self):
        """保存配置"""
        self.service.save_config()
    
    def save_groups(self):
        """保存组别"""
        self.service.save_groups()
    
    def get_groups(self):
        """获取所有组别"""
        return self.service.get_groups()
    
    def get_group(self, group_id):
        """获取单个组别"""
        return self.service.get_group(group_id)
    
    def get_group_content(self, group_id):
        """获取组别内容"""
        return self.service.get_group_content(group_id)
    
    def add_group(self, group_id, name, content):
        """添加新组别"""
        return self.service.add_group(group_id, name, content)
    
    def update_group(self, group_id, name=None, content=None):
        """更新组别"""
        return self.service.update_group(group_id, name, content)
    
    def delete_group(self, group_id):
        """删除组别"""
        return self.service.delete_group(group_id)
    
    def get_interval(self):
        """获取间隔"""
        return self.service.get_interval()
    
    def get_repeat_count(self):
        """获取重复次数"""
        return self.service.get_repeat_count()
    
    def get_default_group(self):
        """获取默认组别"""
        return self.service.get_default_group()
    
    def get_selected_groups(self):
        """获取已选组别"""
        return self.service.get_selected_groups()
    
    def set_selected_groups(self, group_ids):
        """设置已选组别"""
        return self.service.set_selected_groups(group_ids)
    
    def set_interval(self, interval):
        """设置间隔"""
        return self.service.set_interval(interval)
    
    def set_repeat_count(self, count):
        """设置重复次数"""
        return self.service.set_repeat_count(count)
    
    def set_default_group(self, group_id):
        """设置默认组别"""
        return self.service.set_default_group(group_id)
    
    def get_long_word_extension(self):
        """获取长词延长设置"""
        return self.service.get_long_word_extension()
    
    def set_long_word_extension(self, value):
        """设置长词延长"""
        return self.service.set_long_word_extension(value)
    
    @property
    def config(self):
        """兼容旧的 config 属性"""
        return self.service.config
    
    @property
    def _group_file_map(self):
        """兼容旧的 _group_file_map 属性"""
        return self.service._group_file_map


class DictationEngine:
    """DictationEngine 适配器 - 保持与旧接口的兼容性"""
    
    def __init__(self, config_path='config.json'):
        self.service = AudioService(config_path)
    
    def _check_audio_setup(self):
        """检查音频设置"""
        self.service._check_audio_setup()
    
    def _get_audio_filename(self, text):
        """获取音频文件名"""
        return self.service._get_audio_filename(text)
    
    def _get_audio_path(self, text):
        """获取音频文件路径"""
        return self.service._get_audio_path(text)
    
    def _generate_audio_async(self, text):
        """异步生成音频"""
        return self.service._generate_audio_async(text)
    
    def _generate_audio(self, text):
        """生成音频"""
        return self.service._generate_audio(text)
    
    def _load_metadata(self):
        """加载元数据"""
        return self.service._load_metadata()
    
    def _save_metadata(self, metadata):
        """保存元数据"""
        return self.service._save_metadata(metadata)
    
    def _get_config_hash(self):
        """获取配置哈希"""
        return self.service._get_config_hash()
    
    def _cleanup_unused_audio(self, all_content):
        """清理未使用的音频"""
        return self.service._cleanup_unused_audio(all_content)
    
    def _preload_audio(self, content):
        """预加载音频"""
        return self.service._preload_audio(content)
    
    def get_all_content(self, group_manager):
        """获取所有内容"""
        return self.service.get_all_content(group_manager.service)
    
    def cleanup_unused_audio(self, group_manager):
        """清理未使用的音频"""
        return self.service.cleanup_unused_audio(self.get_all_content(group_manager))
    
    def preload_all_audio(self, group_manager):
        """预生成所有音频"""
        return self.service.preload_all_audio(self.get_all_content(group_manager))
    
    def speak(self, text):
        """播放音频"""
        return self.service.speak(text)
    
    def dictate(self, content, interval=3, repeat_count=2, shuffle=True):
        """开始听写"""
        return self.service.dictate(content, interval, repeat_count, shuffle)
    
    def dictate_mixed(self, content, interval=3, repeat_count=2, shuffle=True):
        """混合听写"""
        all_text = [item[0] for item in content]
        return self.service.dictate(all_text, interval, repeat_count, shuffle)
    
    @property
    def use_edge_tts(self):
        """兼容旧的 use_edge_tts 属性"""
        return self.service.use_edge_tts
    
    @property
    def use_pygame(self):
        """兼容旧的 use_pygame 属性"""
        return self.service.use_pygame
    
    @property
    def use_playsound(self):
        """兼容旧的 use_playsound 属性"""
        return self.service.use_playsound
    
    @property
    def cache_dir(self):
        """兼容旧的 cache_dir 属性"""
        return self.service.cache_dir
