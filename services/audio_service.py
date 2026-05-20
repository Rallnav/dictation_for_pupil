import time
import subprocess
import hashlib
import json
import random
import re
import os
import asyncio
import logging
from pathlib import Path
from typing import List, Optional


class AudioService:
    """音频服务 - 提供音频生成和播放功能"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent.resolve()
        self.cache_dir = self.config_dir / 'dictation_audio'
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.voice = 'zh-CN-XiaoxiaoNeural'
        self._check_audio_setup()
    
    def _check_audio_setup(self) -> None:
        """检查音频设置"""
        print('开始检查音频设置...')
        
        # 检查 edge-tts
        try:
            import edge_tts
            self.use_edge_tts = True
            print(f'✓ edge-tts 已安装，使用语音: {self.voice}')
        except ImportError:
            print('警告: edge-tts 未安装，无法播放音频')
            print('请运行: pip install edge-tts')
            self.use_edge_tts = False
        
        # 检查音频播放库
        audio_libraries = []
        
        # sounddevice
        try:
            import sounddevice as sd
            import soundfile as sf
            sd.query_devices()
            self.use_sounddevice = True
            audio_libraries.append('sounddevice')
            print('✓ sounddevice 已安装并可用')
        except ImportError:
            self.use_sounddevice = False
            print('提示: 安装 sounddevice 和 soundfile')
            print('请运行: pip install sounddevice soundfile')
        except OSError as e:
            self.use_sounddevice = False
            print(f'提示: sounddevice 缺少 PortAudio: {e}')
        
        # simpleaudio
        try:
            import simpleaudio as sa
            self.use_simpleaudio = True
            audio_libraries.append('simpleaudio')
            print('✓ simpleaudio 已安装')
        except ImportError:
            self.use_simpleaudio = False
            print('提示: 安装 simpleaudio')
            print('请运行: pip install simpleaudio')
        
        # playsound3
        try:
            from playsound3 import playsound
            self.use_playsound = True
            audio_libraries.append('playsound3')
            print('✓ playsound3 已安装')
        except ImportError:
            self.use_playsound = False
            print('警告: playsound3 未安装')
            print('请运行: pip install playsound3')
            
            # pygame 备选
            try:
                import pygame
                self.use_pygame = True
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                audio_libraries.append('pygame')
                print('✓ pygame 已安装')
            except ImportError:
                self.use_pygame = False
                print('警告: pygame 未安装')
            except Exception as e:
                print(f'  [警告] pygame 初始化失败: {e}')
                self.use_pygame = False
        else:
            self.use_pygame = False
        
        if audio_libraries:
            print(f'可用的音频播放库: {audio_libraries}')
        else:
            print('警告: 未找到任何音频播放库')
        
        print('音频设置检查完成')
    
    def _get_audio_filename(self, text: str) -> str:
        """获取安全的音频文件名"""
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', text)
        return f'{safe_name}.mp3'
    
    def _get_audio_path(self, text: str) -> Path:
        """获取音频文件路径"""
        filename = self._get_audio_filename(text)
        return self.cache_dir / filename
    
    async def _generate_audio_async(self, text: str) -> Optional[Path]:
        """异步生成音频文件"""
        audio_path = self._get_audio_path(text)
        
        if audio_path.exists():
            return audio_path
        
        print(f'  生成音频: {text}')
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(
                text=text, 
                voice=self.voice,
                rate='+0%',
                volume='+0%'
            )
            await communicate.save(str(audio_path))
            
            if audio_path.exists() and audio_path.stat().st_size > 0:
                print(f'  ✓ 音频生成成功')
                return audio_path
            else:
                print(f'  [错误] 音频文件未生成')
                return None
                
        except Exception as e:
            print(f'  [错误] 音频生成异常: {e}')
            return None
    
    def _generate_audio(self, text: str) -> Optional[Path]:
        """生成音频文件（同步接口）"""
        if not self.use_edge_tts:
            print('  [跳过] edge-tts 未安装')
            return None
        
        return asyncio.run(self._generate_audio_async(text))
    
    def _preload_audio(self, content: List[str]) -> None:
        """预加载音频"""
        if not self.use_edge_tts:
            print('edge-tts 未安装，跳过音频预生成')
            return
        
        missing_audio = [text for text in content if not self._get_audio_path(text).exists()]
        
        if not missing_audio:
            print(f'音频缓存已就绪 ({len(content)} 个文件)')
            return
        
        print(f'预生成缺失的音频 ({len(missing_audio)} 个文件)...')
        
        success_count = 0
        for text in missing_audio:
            if self._generate_audio(text):
                success_count += 1
        
        print(f'音频预生成完成 ({success_count}/{len(missing_audio)} 成功)')
    
    def speak(self, text: str) -> None:
        """播放音频"""
        print(f"🔊 播放: {text}")
        
        if not self.use_edge_tts:
            print('  [跳过] edge-tts 未安装')
            return
        
        audio_path = self._get_audio_path(text)
        
        if not audio_path.exists():
            print('  [警告] 音频文件不存在，尝试生成')
            audio_path = self._generate_audio(text)
            if not audio_path:
                return
        
        # sounddevice
        if hasattr(self, 'use_sounddevice') and self.use_sounddevice:
            try:
                import sounddevice as sd
                import soundfile as sf
                data, fs = sf.read(str(audio_path), dtype='float32')
                print(f'  使用 sounddevice 播放')
                sd.play(data, fs)
                sd.wait()
                print('  ✓ 播放成功')
                return
            except OSError as e:
                print(f'  [警告] sounddevice 播放失败: {e}')
                self.use_sounddevice = False
            except Exception as e:
                print(f'  [警告] sounddevice 播放失败: {e}')
        
        # simpleaudio
        if hasattr(self, 'use_simpleaudio') and self.use_simpleaudio:
            try:
                import simpleaudio as sa
                print('  使用 simpleaudio 播放')
                wave_obj = sa.WaveObject.from_wave_file(str(audio_path))
                play_obj = wave_obj.play()
                play_obj.wait_done()
                print('  ✓ 播放成功')
                return
            except Exception as e:
                print(f'  [警告] simpleaudio 播放失败: {e}')
        
        # pygame
        if self.use_pygame:
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.music.load(str(audio_path))
                print('  使用 pygame 播放')
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                print('  ✓ 播放成功')
                return
            except Exception as e:
                print(f'  [警告] pygame 播放失败: {e}')
        
        # playsound3
        if self.use_playsound:
            try:
                from playsound3 import playsound
                print('  使用 playsound3 播放')
                playsound(str(audio_path))
                print('  ✓ 播放成功')
                return
            except Exception as e:
                print(f'  [警告] playsound3 播放失败: {e}')
        
        # 系统播放器
        try:
            if os.name == 'nt':
                print('  使用 Windows 系统播放器')
                os.startfile(str(audio_path))
                time.sleep(2)
                print('  ✓ 播放成功')
            elif os.name == 'posix':
                print('  使用系统默认播放器')
                subprocess.run(['xdg-open', str(audio_path)], check=False)
                time.sleep(2)
                print('  ✓ 播放成功')
        except Exception as e:
            print(f'  [错误] 无法播放音频: {e}')
    
    def dictate(self, content: List[str], interval: int = 3, repeat_count: int = 2, 
                shuffle: bool = True, long_word_extension: bool = False) -> List[str]:
        """开始听写"""
        self._preload_audio(content)
        
        dictated_words = []
        
        if shuffle:
            content = content.copy()
            random.shuffle(content)
            print('已随机打乱听写顺序')
        
        for i, text in enumerate(content, 1):
            print(f"[{i}/{len(content)}] {text}")
            dictated_words.append(text)
            
            for j in range(repeat_count):
                self.speak(text)
                if j < repeat_count - 1:
                    current_interval = interval
                    if long_word_extension and len(text) > 4:
                        current_interval += 1
                    time.sleep(current_interval)
            
            if i < len(content):
                current_interval = interval
                if long_word_extension and len(text) > 4:
                    current_interval += 1
                time.sleep(current_interval)
        
        return dictated_words
    
    def preload_all_audio(self, all_content: List[str]) -> None:
        """预生成所有音频"""
        if not self.use_edge_tts:
            print('edge-tts 未安装')
            return
        
        if not all_content:
            print('没有词汇需要预生成')
            return
        
        missing_audio = [text for text in all_content if not self._get_audio_path(text).exists()]
        
        if not missing_audio:
            print(f'所有音频已就绪 ({len(all_content)} 个文件)')
            return
        
        print(f'预生成缺失的音频 ({len(missing_audio)} 个文件)...')
        
        success_count = 0
        for i, text in enumerate(missing_audio, 1):
            print(f'  [{i}/{len(missing_audio)}] {text}')
            if self._generate_audio(text):
                success_count += 1
        
        print(f'音频预生成完成 ({success_count}/{len(missing_audio)} 成功)')
    
    def cleanup_unused_audio(self, all_content: List[str]) -> None:
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
                    print(f'  [警告] 删除失败: {e}')
        
        if deleted_count > 0:
            print(f'  清理了 {deleted_count} 个未使用的音频文件')
