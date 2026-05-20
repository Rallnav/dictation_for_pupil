import time
import subprocess
import shutil
import hashlib
import json
import random
import re
import os
import asyncio
import logging
from pathlib import Path

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dictation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 重定向 print 到日志
print = logger.info


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
        print('开始检查音频设置...')
        
        # 检查 edge-tts Python 库
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
        
        # 尝试使用 sounddevice（最佳效果）
        try:
            import sounddevice as sd
            import soundfile as sf
            # 测试 sounddevice 是否能正常工作（检查 PortAudio）
            sd.query_devices()
            self.use_sounddevice = True
            audio_libraries.append('sounddevice')
            print('✓ sounddevice 已安装并可用，将优先使用')
        except ImportError:
            self.use_sounddevice = False
            print('提示: 安装 sounddevice 和 soundfile 可以获得更好的音频播放效果')
            print('请运行: pip install sounddevice soundfile')
        except OSError as e:
            self.use_sounddevice = False
            print(f'提示: sounddevice 已安装但缺少 PortAudio 库: {e}')
            print('请安装 PortAudio 库，例如: sudo apt install portaudio19-dev (Ubuntu/Debian)')
        
        # 尝试使用 simpleaudio
        try:
            import simpleaudio as sa
            self.use_simpleaudio = True
            audio_libraries.append('simpleaudio')
            print('✓ simpleaudio 已安装，将作为备选使用')
        except ImportError:
            self.use_simpleaudio = False
            print('提示: 安装 simpleaudio 可以获得更好的跨平台音频播放效果')
            print('请运行: pip install simpleaudio')
        
        # 尝试使用 playsound3
        try:
            from playsound3 import playsound
            self.use_playsound = True
            audio_libraries.append('playsound3')
            print('✓ playsound3 已安装')
        except ImportError:
            print('警告: playsound3 未安装')
            print('请运行: pip install playsound3')
            self.use_playsound = False
            
            # 尝试使用 pygame 作为备选
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
            print(f'优先使用顺序: sounddevice → playsound3 → pygame → 系统播放器')
        else:
            print('警告: 未找到任何音频播放库，将使用系统默认播放器')
        
        print('音频设置检查完成')

    def _get_audio_filename(self, text):
        """获取安全的音频文件名"""
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', text)
        return f'{safe_name}.mp3'

    def _get_audio_path(self, text):
        """获取音频文件路径"""
        filename = self._get_audio_filename(text)
        return self.cache_dir / filename

    async def _generate_audio_async(self, text):
        """异步生成音频文件"""
        audio_path = self._get_audio_path(text)
        
        if audio_path.exists():
            return audio_path
        
        print(f'  生成音频: {text}')
        print(f'  保存路径: {audio_path}')
        
        try:
            import edge_tts
            # 使用更高质量的音频参数
            communicate = edge_tts.Communicate(
                text=text, 
                voice=self.voice,
                rate='+0%',  # 语速正常
                volume='+0%'  # 音量正常
            )
            await communicate.save(str(audio_path))
            
            # 验证文件是否生成
            if audio_path.exists() and audio_path.stat().st_size > 0:
                print(f'  ✓ 音频生成成功: {audio_path.name} ({audio_path.stat().st_size} bytes)')
                return audio_path
            else:
                print(f'  [错误] 音频文件未生成或为空')
                return None
                
        except Exception as e:
            print(f'  [错误] 音频生成异常: {e}')
            return None

    def _generate_audio(self, text):
        """生成音频文件（同步接口）"""
        if not self.use_edge_tts:
            print('  [跳过] edge-tts 未安装')
            return None
        
        # 运行异步函数
        return asyncio.run(self._generate_audio_async(text))

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
        """清理未使用的音频文件
        
        Args:
            all_content: 所有组别的内容列表（全表）
        """
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
        
        # 只生成缺失的音频
        missing_audio = [text for text in content if not self._get_audio_path(text).exists()]
        
        if not missing_audio:
            print(f'音频缓存已就绪 ({len(content)} 个文件)')
            print(f'音频文件位置: {self.cache_dir}')
            return
        
        print(f'预生成缺失的音频 ({len(missing_audio)} 个文件)...')
        print(f'音频文件将保存到: {self.cache_dir}')
        
        success_count = 0
        for text in missing_audio:
            if self._generate_audio(text):
                success_count += 1
        
        print(f'音频预生成完成 ({success_count}/{len(missing_audio)} 成功)')

    def get_all_content(self, group_manager):
        """获取所有组别的内容（全表）
        
        Args:
            group_manager: 组别管理器实例
            
        Returns:
            list: 所有组别的内容列表
        """
        all_content = []
        groups = group_manager.get_groups()
        for group_id, group_info in groups.items():
            all_content.extend(group_info['content'])
        return all_content
    
    def cleanup_unused_audio(self, group_manager):
        """清理多余的音频文件
        
        使用全表来清理未使用的音频文件
        
        Args:
            group_manager: 组别管理器实例
        """
        if not self.use_edge_tts:
            print('edge-tts 未安装，无法清理音频')
            return
        
        all_content = self.get_all_content(group_manager)
        
        if not all_content:
            print('配置文件中没有词汇')
            return
        
        print('清理未使用的音频文件...')
        self._cleanup_unused_audio(all_content)
        print('音频清理完成')
    
    def preload_all_audio(self, group_manager):
        """预生成所有音频"""
        if not self.use_edge_tts:
            print('edge-tts 未安装，无法生成音频')
            return
        
        all_content = self.get_all_content(group_manager)
        
        if not all_content:
            print('配置文件中没有词汇')
            return
        
        # 只生成缺失的音频
        missing_audio = [text for text in all_content if not self._get_audio_path(text).exists()]
        
        if not missing_audio:
            print(f'所有音频已就绪 ({len(all_content)} 个文件)')
            print(f'音频文件位置: {self.cache_dir}')
            return
        
        print(f'预生成缺失的音频 ({len(missing_audio)} 个文件)...')
        print(f'音频文件将保存到: {self.cache_dir}')
        
        success_count = 0
        for i, text in enumerate(missing_audio, 1):
            print(f'  [{i}/{len(missing_audio)}] {text}')
            if self._generate_audio(text):
                success_count += 1
        
        print(f'所有音频预生成完成 ({success_count}/{len(missing_audio)} 成功)')

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
        
        # 尝试使用 sounddevice（最佳效果）
        if hasattr(self, 'use_sounddevice') and self.use_sounddevice:
            try:
                import sounddevice as sd
                import soundfile as sf
                data, fs = sf.read(str(audio_path), dtype='float32')
                print(f'  使用 sounddevice 播放音频，采样率: {fs}Hz')
                sd.play(data, fs)
                sd.wait()
                print('  ✓ 使用 sounddevice 播放成功')
                return
            except OSError as e:
                print(f'  [警告] sounddevice 播放失败 (PortAudio 问题): {e}')
                print('  尝试使用其他音频播放方式')
                # 标记 sounddevice 为不可用，避免下次再尝试
                self.use_sounddevice = False
            except Exception as e:
                print(f'  [警告] sounddevice 播放失败: {e}')
        
        # 尝试使用 simpleaudio
        if hasattr(self, 'use_simpleaudio') and self.use_simpleaudio:
            try:
                import simpleaudio as sa
                import wave
                
                print('  使用 simpleaudio 播放音频')
                wave_obj = sa.WaveObject.from_wave_file(str(audio_path))
                play_obj = wave_obj.play()
                play_obj.wait_done()
                print('  ✓ 使用 simpleaudio 播放成功')
                return
            except Exception as e:
                print(f'  [警告] simpleaudio 播放失败: {e}')
        
        # 尝试使用 pygame
        if self.use_pygame:
            try:
                import pygame
                # 确保 mixer 已初始化
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                    print('  初始化 pygame 音频系统')
                pygame.mixer.music.load(str(audio_path))
                print('  使用 pygame 播放音频')
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                print('  ✓ 使用 pygame 播放成功')
                return
            except Exception as e:
                print(f'  [警告] pygame 播放失败: {e}')
        
        # 尝试使用 playsound3
        if self.use_playsound:
            try:
                from playsound3 import playsound
                print('  使用 playsound3 播放音频')
                playsound(str(audio_path))
                print('  ✓ 使用 playsound3 播放成功')
                return
            except Exception as e:
                print(f'  [警告] playsound3 播放失败: {e}')
        
        # 如果所有方法都失败，尝试使用系统默认播放器
        try:
            if os.name == 'nt':  # Windows
                print('  使用 Windows 系统播放器播放音频')
                os.startfile(str(audio_path))
                time.sleep(2)  # 等待播放开始
                print('  ✓ 使用系统播放器播放成功')
            elif os.name == 'posix':  # Linux/Mac
                print('  使用系统默认播放器播放音频')
                subprocess.run(['xdg-open', str(audio_path)], check=False)
                time.sleep(2)
                print('  ✓ 使用系统播放器播放成功')
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
