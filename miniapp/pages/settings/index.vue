<template>
  <view class="container">
    <view class="card">
      <view class="title">后台设置</view>
      <view class="setting-item">
        <view class="setting-info">
          <text class="setting-label">启用后台</text>
          <text class="setting-desc">开启后数据将同步到服务器</text>
        </view>
        <switch :checked="settings.useBackend" @change="updateSetting('useBackend', $event.detail.value)" color="#667eea" />
      </view>
      <view class="setting-item" v-if="settings.useBackend">
        <text class="setting-label">后台服务地址</text>
        <input
          class="setting-input"
          v-model="settings.backendUrl"
          @blur="saveSettings"
          placeholder="http://localhost:8000"
        />
      </view>
    </view>

    <view class="card">
      <view class="title">听写设置</view>
      <view class="setting-item">
        <text class="setting-label">语音类型</text>
        <picker :value="voiceIndex" :range="voiceOptions" @change="onVoiceChange">
          <view class="picker-value">
            {{ voiceOptions[voiceIndex] }}
            <text class="picker-arrow">›</text>
          </view>
        </picker>
      </view>
      <view class="setting-item">
        <text class="setting-label">默认间隔时间</text>
        <view class="setting-row">
          <input
            type="number"
            class="setting-input-small"
            v-model="settings.defaultInterval"
            @blur="saveSettings"
            min="1"
            max="30"
          />
          <text class="setting-unit">秒</text>
        </view>
      </view>
      <view class="setting-item">
        <text class="setting-label">默认重复次数</text>
        <view class="setting-row">
          <input
            type="number"
            class="setting-input-small"
            v-model="settings.defaultRepeat"
            @blur="saveSettings"
            min="1"
            max="10"
          />
          <text class="setting-unit">次</text>
        </view>
      </view>
      <view class="setting-item">
        <view class="setting-info">
          <text class="setting-label">自动保存</text>
          <text class="setting-desc">自动保存数据到本地</text>
        </view>
        <switch :checked="settings.autoSave" @change="updateSetting('autoSave', $event.detail.value)" color="#667eea" />
      </view>
    </view>

    <view class="card">
      <view class="title">数据管理</view>
      <view class="action-list">
        <view class="action-item" @tap="resetSettings">
          <text class="action-text">恢复默认设置</text>
          <text class="action-arrow">›</text>
        </view>
        <view class="action-item danger" @tap="clearData">
          <text class="action-text">清除所有数据</text>
          <text class="action-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="card">
      <view class="title">关于</view>
      <view class="about-info">
        <text class="about-name">听写软件</text>
        <text class="about-version">版本 1.0.0</text>
        <text class="about-desc">一款支持离线使用的听写练习小程序</text>
      </view>
    </view>

    <view class="card">
      <view class="title">开源声明</view>
      <view class="license-list">
        <view class="license-item">
          <text class="license-name">Tesseract.js</text>
          <text class="license-type">Apache License 2.0</text>
        </view>
      </view>
      <text class="license-note">本项目使用了 Tesseract.js 进行文字识别，遵循 Apache License 2.0 开源协议。</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      settings: {
        backendUrl: 'http://localhost:8000',
        voiceType: 'zh-CN-XiaoxiaoNeural',
        defaultInterval: 3,
        defaultRepeat: 2,
        autoSave: true,
        useBackend: false
      },
      voiceOptions: ['中文-晓晓', '中文-云希', '中文-云扬', '英文-Aria'],
      voiceValues: ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural', 'zh-CN-YunyangNeural', 'en-US-AriaNeural'],
      voiceIndex: 0
    }
  },
  onLoad() {
    this.loadSettings()
  },
  methods: {
    loadSettings() {
      const settings = uni.getStorageSync('dictation_settings')
      if (settings) {
        this.settings = JSON.parse(settings)
        this.voiceIndex = this.voiceValues.indexOf(this.settings.voiceType)
        if (this.voiceIndex < 0) this.voiceIndex = 0
      }
    },

    saveSettings() {
      uni.setStorageSync('dictation_settings', JSON.stringify(this.settings))
      uni.showToast({ title: '设置已保存', icon: 'success' })
    },

    updateSetting(key, value) {
      this.settings[key] = value
      this.saveSettings()
    },

    onVoiceChange(e) {
      this.voiceIndex = e.detail.value
      this.settings.voiceType = this.voiceValues[this.voiceIndex]
      this.saveSettings()
    },

    resetSettings() {
      uni.showModal({
        title: '确认操作',
        content: '确定要恢复默认设置吗？',
        success: (res) => {
          if (res.confirm) {
            this.settings = {
              backendUrl: 'http://localhost:8000',
              voiceType: 'zh-CN-XiaoxiaoNeural',
              defaultInterval: 3,
              defaultRepeat: 2,
              autoSave: true,
              useBackend: false
            }
            this.voiceIndex = 0
            this.saveSettings()
          }
        }
      })
    },

    clearData() {
      uni.showModal({
        title: '警告',
        content: '确定要清除所有数据吗？此操作不可恢复！',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('dictation_groups')
            uni.removeStorageSync('dictation_settings')
            uni.showToast({ title: '数据已清除', icon: 'success' })
            setTimeout(() => {
              this.loadSettings()
            }, 1500)
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.container {
  padding: 20rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
}

.setting-label {
  font-size: 28rpx;
  color: #333;
}

.setting-desc {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 4rpx;
}

.setting-row {
  display: flex;
  align-items: center;
}

.setting-input {
  width: 300rpx;
  padding: 12rpx 16rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  font-size: 26rpx;
  text-align: right;
}

.setting-input-small {
  width: 100rpx;
  padding: 12rpx 16rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  font-size: 26rpx;
  text-align: center;
}

.setting-unit {
  margin-left: 12rpx;
  font-size: 26rpx;
  color: #666;
}

.picker-value {
  display: flex;
  align-items: center;
  color: #667eea;
  font-size: 28rpx;
}

.picker-arrow {
  font-size: 40rpx;
  margin-left: 8rpx;
  color: #999;
}

.action-list {
  background: #fff;
  border-radius: 12rpx;
  overflow: hidden;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.action-item:last-child {
  border-bottom: none;
}

.action-item.danger .action-text {
  color: #f44336;
}

.action-text {
  font-size: 28rpx;
  color: #333;
}

.action-arrow {
  font-size: 36rpx;
  color: #ccc;
}

.about-info {
  text-align: center;
  padding: 20rpx 0;
}

.about-name {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.about-version {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.about-desc {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-top: 16rpx;
}

.license-list {
  margin-bottom: 16rpx;
}

.license-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.license-item:last-child {
  border-bottom: none;
}

.license-name {
  font-size: 26rpx;
  color: #333;
}

.license-type {
  font-size: 24rpx;
  color: #667eea;
}

.license-note {
  font-size: 24rpx;
  color: #999;
  line-height: 1.6;
}
</style>