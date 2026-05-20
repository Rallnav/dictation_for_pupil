<template>
  <view class="container">
    <view class="card">
      <view class="title">选择听写组别</view>
      <view class="group-list">
        <view
          v-for="(group, id) in groups"
          :key="id"
          class="group-item"
          :class="{ selected: selectedGroups.includes(id) }"
          @tap="toggleGroup(id)"
        >
          <view class="checkbox">
            <image v-if="selectedGroups.includes(id)" src="/static/check.png" mode="aspectFit"></image>
          </view>
          <view class="group-info">
            <text class="group-name">{{ group.name }}</text>
            <text class="group-count">{{ group.content.length }} 个词汇</text>
          </view>
        </view>
      </view>
      <view class="selected-info">
        <text>已选择 {{ selectedGroups.length }} 个组别</text>
      </view>
    </view>

    <view class="card">
      <view class="title">听写设置</view>
      <view class="setting-row">
        <text class="setting-label">间隔时间</text>
        <input type="number" v-model="interval" class="setting-input" min="1" max="30" />
        <text class="setting-unit">秒</text>
      </view>
      <view class="setting-row">
        <text class="setting-label">重复次数</text>
        <input type="number" v-model="repeatCount" class="setting-input" min="1" max="10" />
        <text class="setting-unit">次</text>
      </view>
      <view class="setting-row">
        <text class="setting-label">随机打乱顺序</text>
        <switch :checked="shuffle" @change="shuffle = $event.detail.value" color="#667eea" />
      </view>
      <view class="setting-row">
        <text class="setting-label">长词延长</text>
        <switch :checked="longWordExtension" @change="longWordExtension = $event.detail.value" color="#667eea" />
      </view>
    </view>

    <view class="card">
      <view class="title">听写进度</view>
      <view class="progress-bar">
        <view class="progress-inner" :style="{ width: progressPercent + '%' }"></view>
      </view>
      <view class="progress-text">{{ progressText }}</view>
    </view>

    <view class="card dictated-words" v-if="dictatedWords.length > 0">
      <view class="title">已听写单词</view>
      <view class="words-container">
        <text v-for="(word, index) in dictatedWords" :key="index" class="word-tag">{{ word }}</text>
      </view>
    </view>

    <view class="action-buttons">
      <button
        class="btn btn-primary"
        @tap="startDictation"
        :disabled="dictating || selectedGroups.length === 0"
      >
        {{ dictating ? '听写中...' : '开始听写' }}
      </button>
      <button
        v-if="dictating"
        class="btn btn-warning"
        @tap="togglePause"
      >
        {{ paused ? '继续' : '暂停' }}
      </button>
      <button
        v-if="dictating"
        class="btn btn-danger"
        @tap="stopDictation"
      >
        停止
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      groups: {},
      selectedGroups: [],
      interval: 3,
      repeatCount: 2,
      shuffle: true,
      longWordExtension: true,
      dictating: false,
      paused: false,
      progressPercent: 0,
      progressText: '等待开始...',
      dictatedWords: [],
      currentWordIndex: 0,
      allWords: []
    }
  },
  onLoad() {
    this.loadData()
  },
  onShow() {
    this.loadData()
  },
  methods: {
    loadData() {
      const groupsData = uni.getStorageSync('dictation_groups')
      if (groupsData) {
        this.groups = JSON.parse(groupsData)
      }
      const settings = uni.getStorageSync('dictation_settings')
      if (settings) {
        const parsed = JSON.parse(settings)
        this.interval = parsed.defaultInterval || 3
        this.repeatCount = parsed.defaultRepeat || 2
      }
    },

    toggleGroup(id) {
      const index = this.selectedGroups.indexOf(id)
      if (index > -1) {
        this.selectedGroups.splice(index, 1)
      } else {
        this.selectedGroups.push(id)
      }
    },

    startDictation() {
      if (this.selectedGroups.length === 0) {
        uni.showToast({ title: '请至少选择一个组别', icon: 'none' })
        return
      }

      let allContent = []
      this.selectedGroups.forEach(id => {
        if (this.groups[id]) {
          allContent = allContent.concat(this.groups[id].content)
        }
      })

      if (allContent.length === 0) {
        uni.showToast({ title: '没有可听写的词汇', icon: 'none' })
        return
      }

      if (this.shuffle) {
        allContent = this.shuffleArray([...allContent])
      }

      this.allWords = allContent
      this.dictating = true
      this.paused = false
      this.progressPercent = 0
      this.progressText = '准备开始...'
      this.dictatedWords = []
      this.currentWordIndex = 0

      this.runDictation()
    },

    async runDictation() {
      const total = this.allWords.length
      let completed = 0

      for (let i = 0; i < total && this.dictating; i++) {
        while (this.paused && this.dictating) {
          await this.sleep(100)
        }

        if (!this.dictating) break

        const word = this.allWords[i]
        this.currentWordIndex = i
        this.progressText = `正在听写: ${word} (${i + 1}/${total})`

        if (!this.dictatedWords.includes(word)) {
          this.dictatedWords.push(word)
        }

        for (let j = 0; j < this.repeatCount && !this.paused && this.dictating; j++) {
          await this.speak(word)
          completed++
          this.progressPercent = Math.round((completed / (total * this.repeatCount)) * 100)
        }

        if (i < total - 1 && !this.paused && this.dictating) {
          await this.sleep(this.getInterval(word) * 1000)
        }
      }

      if (this.dictating) {
        this.dictating = false
        this.progressText = '听写完成！'
        this.progressPercent = 100
        uni.showToast({ title: '听写完成！', icon: 'success' })
      }
    },

    speak(text) {
      return new Promise((resolve) => {
        const innerAudioContext = uni.createInnerAudioContext()
        innerAudioContext.autoplay = true

        const settings = JSON.parse(uni.getStorageSync('dictation_settings') || '{}')
        const voiceType = settings.voiceType || 'zh-CN-XiaoxiaoNeural'
        let per = 0
        if (voiceType.includes('Yunxi')) per = 1
        else if (voiceType.includes('Yunyang')) per = 3

        const url = `https://tts.baidu.com/text2audio?tex=${encodeURIComponent(text)}&cuid=baike&lan=ZH&ctp=1&pdt=301&vol=9&rate=32&eq=0&per=${per}`

        innerAudioContext.src = url
        innerAudioContext.onPlay(() => {})
        innerAudioContext.onEnded(() => {
          innerAudioContext.destroy()
          resolve()
        })
        innerAudioContext.onError(() => {
          innerAudioContext.destroy()
          resolve()
        })

        setTimeout(() => {
          if (innerAudioContext) {
            innerAudioContext.destroy()
          }
          resolve()
        }, 5000)
      })
    },

    getInterval(word) {
      if (this.longWordExtension && word.length > 4) {
        return this.interval + 1
      }
      return this.interval
    },

    togglePause() {
      this.paused = !this.paused
      if (this.paused) {
        this.progressText = '已暂停...'
        uni.showToast({ title: '已暂停', icon: 'none' })
      }
    },

    stopDictation() {
      this.dictating = false
      this.paused = false
      this.progressText = '已停止'
      uni.showToast({ title: '已停止', icon: 'none' })
    },

    shuffleArray(array) {
      const arr = [...array]
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[arr[i], arr[j]] = [arr[j], arr[i]]
      }
      return arr
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
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

.group-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.group-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  border: 2rpx solid #e0e0e0;
}

.group-item.selected {
  border-color: #667eea;
  background: #f0f0ff;
}

.checkbox {
  width: 40rpx;
  height: 40rpx;
  margin-right: 20rpx;
}

.checkbox image {
  width: 100%;
  height: 100%;
}

.group-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.group-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.group-count {
  font-size: 24rpx;
  color: #666;
  margin-top: 4rpx;
}

.selected-info {
  margin-top: 20rpx;
  text-align: right;
  color: #667eea;
  font-size: 28rpx;
}

.setting-row {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.setting-row:last-child {
  border-bottom: none;
}

.setting-label {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.setting-input {
  width: 120rpx;
  padding: 10rpx 16rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  text-align: center;
  font-size: 28rpx;
}

.setting-unit {
  margin-left: 16rpx;
  font-size: 28rpx;
  color: #666;
}

.progress-bar {
  height: 16rpx;
  background: #e0e0e0;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.progress-inner {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8rpx;
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  color: #333;
  font-size: 28rpx;
}

.dictated-words {
  background: #fff;
}

.words-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.word-tag {
  padding: 8rpx 24rpx;
  background: #667eea;
  color: #fff;
  border-radius: 30rpx;
  font-size: 24rpx;
}

.action-buttons {
  display: flex;
  gap: 20rpx;
  padding: 20rpx 0;
}

.action-buttons .btn {
  flex: 1;
  padding: 24rpx;
  border-radius: 12rpx;
  font-size: 30rpx;
}
</style>