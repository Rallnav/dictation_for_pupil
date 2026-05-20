<script>
export default {
  onLaunch() {
    console.log('App Launch')
    this.initData()
  },
  onShow() {
    console.log('App Show')
  },
  onHide() {
    console.log('App Hide')
  },
  methods: {
    initData() {
      const groups = uni.getStorageSync('dictation_groups')
      if (!groups) {
        const defaultData = {
          'basic': { name: '基础单词', content: ['apple', 'book', 'cat', 'dog', 'egg'] },
          'numbers': { name: '数字单词', content: ['one', 'two', 'three', 'four', 'five'] },
          'colors': { name: '颜色单词', content: ['red', 'blue', 'green', 'yellow', 'black'] }
        }
        uni.setStorageSync('dictation_groups', JSON.stringify(defaultData))
      }

      const settings = uni.getStorageSync('dictation_settings')
      if (!settings) {
        const defaultSettings = {
          backendUrl: 'http://localhost:8000',
          voiceType: 'zh-CN-XiaoxiaoNeural',
          defaultInterval: 3,
          defaultRepeat: 2,
          autoSave: true,
          useBackend: false
        }
        uni.setStorageSync('dictation_settings', JSON.stringify(defaultSettings))
      }
    }
  }
}
</script>

<style>
@import './static/iconfont.css';

page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.container {
  padding: 20rpx;
}

.card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
}

.btn {
  padding: 20rpx 40rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  text-align: center;
  border: none;
  outline: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.btn-secondary {
  background: #e0e0e0;
  color: #333333;
}

.btn-warning {
  background: #ff9800;
  color: #ffffff;
}

.btn-danger {
  background: #f44336;
  color: #ffffff;
}

.btn-disabled {
  opacity: 0.5;
}

.switch-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.switch-label:last-child {
  border-bottom: none;
}

.title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
  margin-bottom: 20rpx;
}
</style>