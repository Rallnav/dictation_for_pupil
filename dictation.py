import time
import subprocess
import shutil
import hashlib
import json
import random
import re
from pathlib import Path


class DictationEngine:
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent.resolve()
        self.cache_dir = self.config_dir / '.dictation_cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.voice = 'zh-CN-XiaoxiaoNeural'
        self._check_audio_setup()

    def _check_audio_setup(self):
        if not shutil.which('edge-tts'):
            print('警告: edge-tts 未安装，无法播放音频')
            print('请运行: pip install edge-tts')
            self.use_edge_tts = False
        else:
            self.use_edge_tts = True
            print(f'使用 edge-tts 语音: {self.voice}')

    def _get_audio_filename(self, text):
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', text)
        return f'{safe_name}.mp3'

    def _get_audio_path(self, text):
        filename = self._get_audio_filename(text)
        return self.cache_dir / filename

    def _generate_audio(self, text):
        audio_path = self._get_audio_path(text)
        
        if audio_path.exists():
            return audio_path
        
        print(f'  生成音频: {text}')
        cmd = f'edge-tts -t "{text}" -v {self.voice} --write-media "{audio_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f'  [错误] 音频生成失败: {result.stderr.strip()}')
            return None
        
        return audio_path

    def _load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata):
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _get_config_hash(self):
        if not self.config_path.exists():
            return ''
        with open(self.config_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _cleanup_unused_audio(self, all_content):
        if not self.cache_dir.exists():
            return
        
        content_set = set(self._get_audio_filename(text) for text in all_content)
        deleted_count = 0
        
        for audio_file in self.cache_dir.glob('*.mp3'):
            if audio_file.name not in content_set:
                try:
                    audio_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f'  [警告] 删除文件失败 {audio_file.name}: {e}')
        
        if deleted_count > 0:
            print(f'  清理了 {deleted_count} 个未使用的音频文件')

    def _preload_audio(self, content):
        if not self.use_edge_tts:
            return
        
        config_hash = self._get_config_hash()
        metadata = self._load_metadata()
        
        if metadata.get('config_hash') == config_hash:
            cached_count = sum(1 for text in content if self._get_audio_path(text).exists())
            if cached_count == len(content):
                print(f'音频缓存已就绪 ({len(content)} 个文件)')
                return
        
        print(f'预生成音频 ({len(content)} 个文件)...')
        for text in content:
            self._generate_audio(text)
        
        # 清理未使用的音频文件
        self._cleanup_unused_audio(content)
        
        metadata['config_hash'] = config_hash
        self._save_metadata(metadata)
        print('音频预生成完成')

    def preload_all_audio(self, group_manager):
        if not self.use_edge_tts:
            print('edge-tts 未安装，无法生成音频')
            return
        
        all_content = []
        groups = group_manager.get_groups()
        for group_id, group_info in groups.items():
            all_content.extend(group_info['content'])
        
        if not all_content:
            print('配置文件中没有词汇')
            return
        
        print(f'预生成所有音频 ({len(all_content)} 个文件)...')
        for i, text in enumerate(all_content, 1):
            print(f'  [{i}/{len(all_content)}] {text}')
            self._generate_audio(text)
        
        print('清理未使用的音频文件...')
        self._cleanup_unused_audio(all_content)
        
        config_hash = self._get_config_hash()
        metadata = self._load_metadata()
        metadata['config_hash'] = config_hash
        self._save_metadata(metadata)
        print('所有音频预生成完成')

    def speak(self, text):
        print(f"🔊 播放: {text}")
        
        if not self.use_edge_tts:
            print('  [跳过] edge-tts 未安装')
            return
        
        audio_path = self._get_audio_path(text)
        
        if not audio_path.exists():
            print(f'  [警告] 音频文件不存在，尝试生成')
            audio_path = self._generate_audio(text)
            if not audio_path:
                return
        
        try:
            from playsound3 import playsound
            playsound(str(audio_path))
        except ImportError:
            print('  [错误] playsound3 未安装，请运行: pip install playsound3')
        except Exception as e:
            print(f'  [错误] 音频播放异常: {e}')

    def dictate(self, content, interval=3, repeat_count=2, shuffle=True):
        self._preload_audio(content)
        
        if shuffle:
            content = content.copy()
            random.shuffle(content)
            print('已随机打乱听写顺序')
        
        for i, text in enumerate(content, 1):
            print(f"[{i}/{len(content)}] {text}")
            for j in range(repeat_count):
                self.speak(text)
                if j < repeat_count - 1:
                    time.sleep(interval)
            if i < len(content):
                time.sleep(interval)

    def dictate_mixed(self, content, interval=3, repeat_count=2, shuffle=True):
        all_text = [item[0] for item in content]
        self._preload_audio(all_text)
        
        if shuffle:
            content = content.copy()
            random.shuffle(content)
            print('已随机打乱听写顺序')
        
        for i, (text, group_id, group_name) in enumerate(content, 1):
            print(f"[{i}/{len(content)}] {text} [{group_name}]")
            for j in range(repeat_count):
                self.speak(text)
                if j < repeat_count - 1:
                    time.sleep(interval)
            if i < len(content):
                time.sleep(interval)
