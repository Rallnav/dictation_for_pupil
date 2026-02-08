import time
import subprocess
import os


class DictationEngine:
    def __init__(self):
        # 设置 PulseAudio 服务器为 WSLg 的服务器
        os.environ['PULSE_SERVER'] = 'unix:/mnt/wslg/PulseServer'

    def speak(self, text):
        # 无论是否有音频设备，都提供视觉反馈
        print(f"🔊 播放: {text}")
        try:
            cmd = f'espeak-ng -v chinese-mb-cn1 "{text}"'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # 如果没有音频设备，静默忽略
            pass

    def dictate(self, content, interval=3, repeat_count=2):
        for i, text in enumerate(content, 1):
            print(f"[{i}/{len(content)}] {text}")
            for j in range(repeat_count):
                self.speak(text)
                if j < repeat_count - 1:
                    time.sleep(interval)
            if i < len(content):
                time.sleep(interval)
