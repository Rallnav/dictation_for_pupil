import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class GroupService:
    """组别管理服务"""
    
    def __init__(self, config_path: str = "config.json", groups_dir: str = "groups"):
        self.config_path = Path(config_path)
        self.groups_dir = Path(groups_dir)
        self.groups_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
        self._group_file_map: Dict[str, Path] = {}
        self._load_groups()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载主配置文件"""
        if not self.config_path.exists():
            default_config = {
                "selected_groups": [],
                "interval": 3,
                "repeat_count": 2,
                "long_word_extension": True
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_groups(self) -> None:
        """从目录加载所有群组配置文件"""
        self._group_file_map = {}
        groups = {}
        group_id_counter: Dict[str, int] = {}
        
        for json_file in self.groups_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                    if 'groups' in file_content:
                        for group_id, group_info in file_content['groups'].items():
                            original_group_id = group_id
                            while group_id in groups:
                                if original_group_id not in group_id_counter:
                                    group_id_counter[original_group_id] = 1
                                else:
                                    group_id_counter[original_group_id] += 1
                                group_id = f"{original_group_id}_{group_id_counter[original_group_id]}"
                            
                            group_info['source_file'] = json_file.name
                            groups[group_id] = group_info
                            self._group_file_map[group_id] = json_file
            except Exception as e:
                print(f"加载文件 {json_file} 失败: {e}")
        
        self.config['groups'] = groups
    
    def save_config(self) -> None:
        """保存主配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def save_groups(self) -> None:
        """保存所有群组到对应的文件"""
        file_groups: Dict[Path, Dict[str, Any]] = {}
        for group_id, file_path in self._group_file_map.items():
            if file_path not in file_groups:
                file_groups[file_path] = {}
            if group_id in self.config['groups']:
                group_info = self.config['groups'][group_id].copy()
                if 'source_file' in group_info:
                    del group_info['source_file']
                file_groups[file_path][group_id] = group_info
        
        for file_path, groups_data in file_groups.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({"groups": groups_data}, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存文件 {file_path} 失败: {e}")
    
    def get_groups(self) -> Dict[str, Dict[str, Any]]:
        """获取所有组别"""
        return self.config.get('groups', {})
    
    def get_group(self, group_id: str) -> Dict[str, Any]:
        """获取单个组别"""
        groups = self.get_groups()
        if group_id not in groups:
            raise ValueError(f"组别 {group_id} 不存在")
        return groups[group_id]
    
    def get_group_content(self, group_id: str) -> List[str]:
        """获取组别内容"""
        group = self.get_group(group_id)
        return group.get('content', [])
    
    def add_group(self, group_id: str, name: str, content: List[str]) -> str:
        """添加新组别"""
        groups = self.get_groups()
        
        original_group_id = group_id
        counter = 1
        while group_id in groups:
            group_id = f"{original_group_id}_{counter}"
            counter += 1
        
        groups[group_id] = {'name': name, 'content': content, 'source_file': 'default.json'}
        self.config['groups'] = groups
        
        default_file = self.groups_dir / "default.json"
        self._group_file_map[group_id] = default_file
        
        self.save_config()
        self.save_groups()
        
        return group_id
    
    def update_group(self, group_id: str, name: Optional[str] = None, content: Optional[List[str]] = None) -> None:
        """更新组别"""
        group = self.get_group(group_id)
        if name:
            group['name'] = name
        if content is not None:
            group['content'] = content
        
        self.save_config()
        self.save_groups()
    
    def delete_group(self, group_id: str) -> None:
        """删除组别"""
        groups = self.get_groups()
        if group_id not in groups:
            raise ValueError(f"组别 {group_id} 不存在")
        del groups[group_id]
        self.config['groups'] = groups
        
        if group_id in self._group_file_map:
            del self._group_file_map[group_id]
        
        if 'selected_groups' in self.config and group_id in self.config['selected_groups']:
            self.config['selected_groups'].remove(group_id)
        
        if 'default_group' in self.config and self.config['default_group'] == group_id:
            self.config['default_group'] = None
        
        self.save_config()
        self.save_groups()
    
    def get_interval(self) -> int:
        """获取听写间隔"""
        return self.config.get('interval', 3)
    
    def get_repeat_count(self) -> int:
        """获取重复次数"""
        return self.config.get('repeat_count', 2)
    
    def get_default_group(self) -> Optional[str]:
        """获取默认组别"""
        return self.config.get('default_group', None)
    
    def get_selected_groups(self) -> List[str]:
        """获取已选组别"""
        return self.config.get('selected_groups', [])
    
    def set_selected_groups(self, group_ids: List[str]) -> None:
        """设置已选组别"""
        self.config['selected_groups'] = group_ids
        self.save_config()
    
    def set_interval(self, interval: int) -> None:
        """设置听写间隔"""
        self.config['interval'] = interval
        self.save_config()
    
    def set_repeat_count(self, count: int) -> None:
        """设置重复次数"""
        self.config['repeat_count'] = count
        self.save_config()
    
    def set_default_group(self, group_id: str) -> None:
        """设置默认组别"""
        self.config['default_group'] = group_id
        self.save_config()
    
    def get_long_word_extension(self) -> bool:
        """获取长词延长设置"""
        return self.config.get('long_word_extension', True)
    
    def set_long_word_extension(self, value: bool) -> None:
        """设置长词延长"""
        self.config['long_word_extension'] = value
        self.save_config()
