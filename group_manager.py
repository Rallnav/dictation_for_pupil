import json
import os
from pathlib import Path


class GroupManager:
    def __init__(self, config_path="config.json", groups_dir="groups"):
        self.config_path = Path(config_path)
        self.groups_dir = Path(groups_dir)
        self.groups_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
        self._group_file_map = {}
        self._load_groups()

    def _load_config(self):
        """加载主配置文件"""
        if not self.config_path.exists():
            # 创建默认配置
            default_config = {
                "selected_groups": [],
                "interval": 3,
                "repeat_count": 2
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_groups(self):
        """从目录加载所有群组配置文件"""
        self._group_file_map = {}
        groups = {}
        
        # 用于跟踪重复的组别 ID
        group_id_counter = {}
        
        # 遍历 groups 目录中的所有 JSON 文件
        for json_file in self.groups_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                    if 'groups' in file_content:
                        for group_id, group_info in file_content['groups'].items():
                            # 处理重复的组别 ID
                            original_group_id = group_id
                            while group_id in groups:
                                # 为重复的组别 ID 添加后缀
                                if original_group_id not in group_id_counter:
                                    group_id_counter[original_group_id] = 1
                                else:
                                    group_id_counter[original_group_id] += 1
                                group_id = f"{original_group_id}_{group_id_counter[original_group_id]}"
                            
                            # 保存组别信息，添加来源文件信息
                            group_info['source_file'] = json_file.name
                            groups[group_id] = group_info
                            self._group_file_map[group_id] = json_file
            except Exception as e:
                print(f"加载文件 {json_file} 失败: {e}")
        
        self.config['groups'] = groups

    def save_config(self):
        """保存主配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def save_groups(self):
        """保存所有群组到对应的文件"""
        # 按文件分组
        file_groups = {}
        for group_id, file_path in self._group_file_map.items():
            if file_path not in file_groups:
                file_groups[file_path] = {}
            if group_id in self.config['groups']:
                # 移除来源文件信息
                group_info = self.config['groups'][group_id].copy()
                if 'source_file' in group_info:
                    del group_info['source_file']
                file_groups[file_path][group_id] = group_info
        
        # 保存每个文件
        for file_path, groups_data in file_groups.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({"groups": groups_data}, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存文件 {file_path} 失败: {e}")

    def get_groups(self):
        return self.config.get('groups', {})

    def get_group(self, group_id):
        groups = self.get_groups()
        if group_id not in groups:
            raise ValueError(f"组别 {group_id} 不存在")
        return groups[group_id]

    def get_group_content(self, group_id):
        group = self.get_group(group_id)
        return group.get('content', [])

    def add_group(self, group_id, name, content):
        """添加新组别，默认保存到 default.json"""
        groups = self.get_groups()
        
        # 处理重复的组别 ID
        original_group_id = group_id
        counter = 1
        while group_id in groups:
            group_id = f"{original_group_id}_{counter}"
            counter += 1
        
        # 添加组别信息
        groups[group_id] = {'name': name, 'content': content, 'source_file': 'default.json'}
        self.config['groups'] = groups
        
        # 默认保存到 default.json
        default_file = self.groups_dir / "default.json"
        self._group_file_map[group_id] = default_file
        
        self.save_config()
        self.save_groups()
        
        return group_id

    def update_group(self, group_id, name=None, content=None):
        group = self.get_group(group_id)
        if name:
            group['name'] = name
        if content is not None:
            group['content'] = content
        
        self.save_config()
        self.save_groups()

    def delete_group(self, group_id):
        groups = self.get_groups()
        if group_id not in groups:
            raise ValueError(f"组别 {group_id} 不存在")
        del groups[group_id]
        self.config['groups'] = groups
        
        # 从 group_file_map 中移除
        if group_id in self._group_file_map:
            del self._group_file_map[group_id]
        
        # 从 selected_groups 中移除已删除的组别
        if 'selected_groups' in self.config:
            if group_id in self.config['selected_groups']:
                self.config['selected_groups'].remove(group_id)
        
        # 从 default_group 中移除已删除的组别
        if 'default_group' in self.config and self.config['default_group'] == group_id:
            self.config['default_group'] = None
        
        self.save_config()
        self.save_groups()

    def get_interval(self):
        return self.config.get('interval', 3)

    def get_repeat_count(self):
        return self.config.get('repeat_count', 2)

    def get_default_group(self):
        return self.config.get('default_group', None)

    def get_selected_groups(self):
        return self.config.get('selected_groups', [])

    def set_selected_groups(self, group_ids):
        # 允许选择重复的组别 ID
        # for group_id in group_ids:
        #     if group_id not in self.get_groups():
        #         raise ValueError(f"组别 {group_id} 不存在")
        self.config['selected_groups'] = group_ids
        self.save_config()

    def set_interval(self, interval):
        self.config['interval'] = interval
        self.save_config()

    def set_repeat_count(self, count):
        self.config['repeat_count'] = count
        self.save_config()

    def set_default_group(self, group_id):
        # 允许设置重复的组别 ID
        # if group_id not in self.get_groups():
        #     raise ValueError(f"组别 {group_id} 不存在")
        self.config['default_group'] = group_id
        self.save_config()