import time
import subprocess
import shutil
import hashlib
import json
import random
import re
import os
from pathlib import Path


class DictationEngine:
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent.resolve()
        # 使用非隐藏目录，方便用户查看
        self.cache_dir = self.config_dir / 'dictation_audio'
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.voice = 'zh-CN-XiaoxiaoNeural'
        self._check_audio_setup()

    def _check_audio_setup(self):
        """检查音频设置"""
        # 检查 edge-tts
        if not shutil.which('edge-tts'):
            print('警告: edge-tts 未安装，无法播放音频')
            print('请运行: pip install edge-tts')
            self.use_edge_tts = False
        else:
            self.use_edge_tts = True
            print(f'使用 edge-tts 语音: {self.voice}')
        
        # 检查音频播放库
        try:
            from playsound3 import playsound
            self.use_playsound = True
        except ImportError:
            print('警告: playsound3 未安装')
            print('请运行: pip install playsound3')
            self.use_playsound = False
            
            # 尝试使用 pygame 作为备选
            try:
                import pygame
                self.use_pygame = True
                pygame.mixer.init()
                print('使用 pygame 作为音频播放库')
            except ImportError:
                self.use_pygame = False
        else:
            self.use_pygame = False

    def _get_audio_filename(self, text):
        """获取安全的音频文件名"""
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', text)
        return f'{safe_name}.mp3'

    def _get_audio_path(self, text):
        """获取音频文件路径"""
        filename = self._get_audio_filename(text)
        return self.cache_dir / filename

    def _generate_audio(self, text):
        """生成音频文件"""
        audio_path = self._get_audio_path(text)
        
        if audio_path.exists():
            return audio_path
        
        print(f'  生成音频: {text}')
        print(f'  保存路径: {audio_path}')
        
        # 使用 edge-tts 生成音频
        cmd = ['edge-tts', '-t', text, '-v', self.voice, '--write-media', str(audio_path)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f'  [错误] 音频生成失败: {result.stderr.strip()}')
                return None
            
            # 验证文件是否生成
            if audio_path.exists() and audio_path.stat().st_size > 0:
                print(f'  ✓ 音频生成成功: {audio_path.name} ({audio_path.stat().st_size} bytes)')
                return audio_path
            else:
                print(f'  [错误] 音频文件未生成或为空')
                return None
                
        except subprocess.TimeoutExpired:
            print(f'  [错误] 音频生成超时')
            return None
        except Exception as e:
            print(f'  [错误] 音频生成异常: {e}')
            return None

    def _load_metadata(self):
        """加载元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _get_config_hash(self):
        """获取配置文件哈希"""
        if not self.config_path.exists():
            return ''
        with open(self.config_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _cleanup_unused_audio(self, all_content):
        """清理未使用的音频文件"""
        if not self.cache_dir.exists():
            return
        
        content_set = set(self._get_audio_filename(text) for text in all_content)
        deleted_count = 0
        
        for audio_file in self.cache_dir.glob('*.mp3'):
            if audio_file.name not in content_set:
                try:
                    audio_file.unlink()
                    deleted_count += 1
                    print(f'  删除未使用音频: {audio_file.name}')
                except Exception as e:
                    print(f'  [警告] 删除文件失败 {audio_file.name}: {e}')
        
        if deleted_count > 0:
            print(f'  清理了 {deleted_count} 个未使用的音频文件')

    def _preload_audio(self, content):
        """预加载音频"""
        if not self.use_edge_tts:
            print('edge-tts 未安装，跳过音频预生成')
            return
        
        config_hash = self._get_config_hash()
        metadata = self._load_metadata()
        
        if metadata.get('config_hash') == config_hash:
            cached_count = sum(1 for text in content if self._get_audio_path(text).exists())
            if cached_count == len(content):
                print(f'音频缓存已就绪 ({len(content)} 个文件)')
                print(f'音频文件位置: {self.cache_dir}')
                return
        
        print(f'预生成音频 ({len(content)} 个文件)...')
        print(f'音频文件将保存到: {self.cache_dir}')
        
        success_count = 0
        for text in content:
            if self._generate_audio(text):
                success_count += 1
        
        # 清理未使用的音频文件
        self._cleanup_unused_audio(content)
        
        metadata['config_hash'] = config_hash
        self._save_metadata(metadata)
        print(f'音频预生成完成 ({success_count}/{len(content)} 成功)')

    def preload_all_audio(self, group_manager):
        """预生成所有音频"""
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
        print(f'音频文件将保存到: {self.cache_dir}')
        
        success_count = 0
        for i, text in enumerate(all_content, 1):
            print(f'  [{i}/{len(all_content)}] {text}')
            if self._generate_audio(text):
                success_count += 1
        
        print('清理未使用的音频文件...')
        self._cleanup_unused_audio(all_content)
        
        config_hash = self._get_config_hash()
        metadata = self._load_metadata()
        metadata['config_hash'] = config_hash
        self._save_metadata(metadata)
        print(f'所有音频预生成完成 ({success_count}/{len(all_content)} 成功)')

    def speak(self, text):
        """播放音频"""
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
        
        # 尝试使用不同的音频播放库
        if self.use_playsound:
            try:
                from playsound3 import playsound
                playsound(str(audio_path))
                return
            except Exception as e:
                print(f'  [警告] playsound3 播放失败: {e}')
        
        if self.use_pygame:
            try:
                import pygame
                pygame.mixer.music.load(str(audio_path))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                return
            except Exception as e:
                print(f'  [警告] pygame 播放失败: {e}')
        
        # 如果所有方法都失败，尝试使用系统默认播放器
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(audio_path))
                time.sleep(2)  # 等待播放开始
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', str(audio_path)], check=False)
                time.sleep(2)
        except Exception as e:
            print(f'  [错误] 无法播放音频: {e}')
            print(f'  音频文件位置: {audio_path}')

    def dictate(self, content, interval=3, repeat_count=2, shuffle=True):
        """开始听写"""
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
        """混合听写（多组）"""
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
