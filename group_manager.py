import json
from pathlib import Path


class GroupManager:
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

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
        groups = self.get_groups()
        if group_id in groups:
            raise ValueError(f"组别 {group_id} 已存在")
        groups[group_id] = {'name': name, 'content': content}
        self.config['groups'] = groups
        self.save_config()

    def update_group(self, group_id, name=None, content=None):
        group = self.get_group(group_id)
        if name:
            group['name'] = name
        if content is not None:
            group['content'] = content
        self.save_config()

    def delete_group(self, group_id):
        groups = self.get_groups()
        if group_id not in groups:
            raise ValueError(f"组别 {group_id} 不存在")
        del groups[group_id]
        self.config['groups'] = groups
        self.save_config()

    def get_interval(self):
        return self.config.get('interval', 3)

    def get_repeat_count(self):
        return self.config.get('repeat_count', 2)

    def get_default_group(self):
        return self.config.get('default_group', None)

    def get_selected_groups(self):
        return self.config.get('selected_groups', [])

    def set_selected_groups(self, group_ids):
        for group_id in group_ids:
            if group_id not in self.get_groups():
                raise ValueError(f"组别 {group_id} 不存在")
        self.config['selected_groups'] = group_ids
        self.save_config()

    def set_interval(self, interval):
        self.config['interval'] = interval
        self.save_config()

    def set_repeat_count(self, count):
        self.config['repeat_count'] = count
        self.save_config()

    def set_default_group(self, group_id):
        if group_id not in self.get_groups():
            raise ValueError(f"组别 {group_id} 不存在")
        self.config['default_group'] = group_id
        self.save_config()
