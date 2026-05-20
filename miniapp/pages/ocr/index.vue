<template>
  <view class="container">
    <view class="card">
      <view class="title">📷 文字识别</view>
      <text class="description">拍摄课本上的单词，自动识别并添加到组别中</text>

      <view class="camera-wrapper" v-if="cameraShowing">
        <camera
          device-position="back"
          flash="auto"
          @error="onCameraError"
          style="width: 100%; height: 400rpx;"
        ></camera>
      </view>

      <view class="image-preview" v-if="imagePath && !cameraShowing">
        <image :src="imagePath" mode="aspectFit" class="preview-img"></image>
      </view>

      <view class="empty-state" v-if="!imagePath && !cameraShowing">
        <text class="empty-icon">📸</text>
        <text class="empty-text">点击下方按钮拍照或选择图片</text>
      </view>

      <view class="ocr-controls">
        <button class="btn btn-primary" @tap="startCamera" v-if="!cameraShowing">
          开启摄像头
        </button>
        <button class="btn btn-primary" @tap="takePhoto" v-if="cameraShowing">
          拍照识别
        </button>
        <button class="btn btn-secondary" @tap="chooseImage">
          从相册选择
        </button>
        <button class="btn btn-warning" @tap="stopCamera" v-if="cameraShowing">
          关闭摄像头
        </button>
      </view>
    </view>

    <view class="card" v-if="ocrResult">
      <view class="title">识别结果</view>
      <view class="ocr-result">
        <text class="result-text">{{ ocrResult }}</text>
      </view>
      <view class="ocr-actions">
        <button class="btn btn-primary" @tap="showGroupPickerModal">添加到组别</button>
        <button class="btn btn-secondary" @tap="clearOcr">清除</button>
      </view>
    </view>

    <view class="card loading-card" v-if="loading">
      <view class="loading-content">
        <view class="loading-spinner"></view>
        <text class="loading-text">正在识别...</text>
      </view>
    </view>

    <view class="modal" v-if="showGroupPicker">
      <view class="modal-mask" @tap="closeGroupPicker"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">选择组别</text>
          <text class="modal-close" @tap="closeGroupPicker">×</text>
        </view>
        <view class="modal-body">
          <view
            v-for="(group, id) in groups"
            :key="id"
            class="group-option"
            :class="{ selected: selectedGroupId === id }"
            @tap="selectGroup(id)"
          >
            <text>{{ group.name }}</text>
            <text class="group-count">{{ group.content.length }} 词</text>
          </view>
          <view class="group-option new-group" @tap="showNewGroupModal">
            <text>+ 创建新组别</text>
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn btn-secondary" @tap="closeGroupPicker">取消</button>
          <button class="btn btn-primary" @tap="confirmAddToGroup">确认添加</button>
        </view>
      </view>
    </view>

    <view class="modal" v-if="showNewGroupModal">
      <view class="modal-mask" @tap="closeNewGroupModal"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">新建组别</text>
          <text class="modal-close" @tap="closeNewGroupModal">×</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">组别ID</text>
            <input class="form-input" v-model="newGroupId" placeholder="请输入组别ID" />
          </view>
          <view class="form-item">
            <text class="form-label">组别名称</text>
            <input class="form-input" v-model="newGroupName" placeholder="请输入组别名称" />
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn btn-secondary" @tap="closeNewGroupModal">取消</button>
          <button class="btn btn-primary" @tap="confirmNewGroup">创建并添加</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      cameraShowing: false,
      imagePath: '',
      ocrResult: '',
      loading: false,
      groups: {},
      showGroupPicker: false,
      showNewGroupModal: false,
      selectedGroupId: '',
      newGroupId: '',
      newGroupName: ''
    }
  },
  onLoad() {
    this.loadGroups()
  },
  onShow() {
    this.loadGroups()
  },
  onUnload() {
    this.stopCamera()
  },
  methods: {
    loadGroups() {
      const groupsData = uni.getStorageSync('dictation_groups')
      if (groupsData) {
        this.groups = JSON.parse(groupsData)
      }
    },

    startCamera() {
      this.cameraShowing = true
    },

    stopCamera() {
      this.cameraShowing = false
    },

    takePhoto() {
      const ctx = uni.createCameraContext()
      ctx.takePhoto({
        quality: 'high',
        success: (res) => {
          this.imagePath = res.tempImagePath
          this.cameraShowing = false
          this.processImage(res.tempImagePath)
        },
        fail: () => {
          uni.showToast({ title: '拍照失败', icon: 'none' })
        }
      })
    },

    chooseImage() {
      uni.chooseImage({
        count: 1,
        sourceType: ['album'],
        success: (res) => {
          if (res.tempFilePaths.length > 0) {
            this.imagePath = res.tempFilePaths[0]
            this.processImage(res.tempFilePaths[0])
          }
        },
        fail: () => {
          uni.showToast({ title: '选择图片失败', icon: 'none' })
        }
      })
    },

    processImage(imagePath) {
      this.loading = true
      this.ocrResult = ''

      uni.showLoading({ title: '识别中...' })

      const settings = JSON.parse(uni.getStorageSync('dictation_settings') || '{}')

      if (settings.useBackend && settings.backendUrl) {
        this.callBackendOCR(imagePath, settings.backendUrl)
      } else {
        this.callLocalOCR(imagePath)
      }
    },

    callLocalOCR(imagePath) {
      const fs = uni.getFileSystemManager()
      fs.readFile({
        filePath: imagePath,
        encoding: 'base64',
        success: (res) => {
          const base64 = res.data
          const imgSrc = `data:image/jpeg;base64,${base64}`
          this.recognizeWithBrowser(imgSrc)
        },
        fail: (err) => {
          uni.hideLoading()
          this.loading = false
          uni.showToast({ title: '读取图片失败', icon: 'none' })
        }
      })
    },

    recognizeWithBrowser(imgSrc) {
      const that = this
      const TESSERACT_CDN = 'https://cdn.jsdelivr.net/npm/tesseract.js@5.1.0/dist/tesseract.min.js'

      if (!that.tesseractLoaded) {
        uni.showLoading({ title: '加载识别引擎...' })
        const script = document.createElement('script')
        script.src = TESSERACT_CDN
        script.onload = function() {
          that.tesseractLoaded = true
          uni.hideLoading()
          that.recognizeWithBrowser(imgSrc)
        }
        script.onerror = function() {
          uni.hideLoading()
          that.loading = false
          uni.showToast({ title: 'OCR引擎加载失败', icon: 'none' })
        }
        document.head.appendChild(script)
        return
      }

      if (typeof Tesseract === 'undefined') {
        uni.hideLoading()
        this.loading = false
        uni.showToast({ title: 'OCR引擎未就绪', icon: 'none' })
        return
      }

      uni.showLoading({ title: '正在识别...' })

      Tesseract.recognize(
        imgSrc,
        'eng+chi_sim',
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              uni.showLoading({ title: `识别中 ${Math.round(m.progress * 100)}%` })
            }
          }
        }
      ).then((result) => {
        uni.hideLoading()
        this.loading = false
        this.ocrResult = result.data.text.trim()

        if (!this.ocrResult) {
          uni.showToast({ title: '未识别到文字', icon: 'none' })
        }
      }).catch((err) => {
        uni.hideLoading()
        this.loading = false
        console.error('OCR Error:', err)
        uni.showToast({ title: '识别失败', icon: 'none' })
      })
    },

    callBackendOCR(imagePath, backendUrl) {
      uni.uploadFile({
        url: `${backendUrl}/api/ocr`,
        filePath: imagePath,
        name: 'image',
        success: (res) => {
          uni.hideLoading()
          this.loading = false
          if (res.statusCode === 200) {
            const data = JSON.parse(res.data)
            if (data.success) {
              this.ocrResult = data.text
            } else {
              uni.showToast({ title: data.message || '识别失败', icon: 'none' })
            }
          } else {
            uni.showToast({ title: '识别服务不可用', icon: 'none' })
          }
        },
        fail: () => {
          uni.hideLoading()
          this.loading = false
          this.callLocalOCR(imagePath)
        }
      })
    },

    onCameraError() {
      uni.showToast({ title: '摄像头出错', icon: 'none' })
      this.cameraShowing = false
    },

    showGroupPickerModal() {
      if (!this.ocrResult) return
      this.showGroupPicker = true
    },

    selectGroup(id) {
      this.selectedGroupId = id
    },

    closeGroupPicker() {
      this.showGroupPicker = false
    },

    confirmAddToGroup() {
      if (!this.selectedGroupId) {
        uni.showToast({ title: '请选择组别', icon: 'none' })
        return
      }

      const words = this.parseOcrResult(this.ocrResult)
      if (words.length === 0) {
        uni.showToast({ title: '没有可添加的单词', icon: 'none' })
        return
      }

      this.groups[this.selectedGroupId].content = this.groups[this.selectedGroupId].content.concat(words)
      uni.setStorageSync('dictation_groups', JSON.stringify(this.groups))
      this.closeGroupPicker()
      uni.showToast({ title: `已添加 ${words.length} 个单词`, icon: 'success' })
      this.clearOcr()
    },

    showNewGroupModal() {
      this.closeGroupPicker()
      this.showNewGroupModal = true
    },

    closeNewGroupModal() {
      this.showNewGroupModal = false
    },

    confirmNewGroup() {
      if (!this.newGroupId || !this.newGroupName) {
        uni.showToast({ title: '请填写完整信息', icon: 'none' })
        return
      }

      if (this.groups[this.newGroupId]) {
        uni.showToast({ title: '该ID已存在', icon: 'none' })
        return
      }

      const words = this.parseOcrResult(this.ocrResult)
      this.groups[this.newGroupId] = {
        name: this.newGroupName,
        content: words
      }
      uni.setStorageSync('dictation_groups', JSON.stringify(this.groups))
      this.closeNewGroupModal()
      uni.showToast({ title: `已创建组别并添加 ${words.length} 个单词`, icon: 'success' })
      this.clearOcr()
      this.newGroupId = ''
      this.newGroupName = ''
    },

    parseOcrResult(text) {
      return text.split(/[\n,，、\s]+/)
        .map(item => item.trim())
        .filter(item => item && item.length > 1)
    },

    clearOcr() {
      this.imagePath = ''
      this.ocrResult = ''
      this.selectedGroupId = ''
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

.description {
  display: block;
  text-align: center;
  color: #666;
  font-size: 26rpx;
  margin-bottom: 30rpx;
}

.camera-wrapper {
  width: 100%;
  border-radius: 12rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
}

.image-preview {
  width: 100%;
  border-radius: 12rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  background: #000;
}

.preview-img {
  width: 100%;
  height: 400rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx 0;
  background: #f8f9fa;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.ocr-controls {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.ocr-controls .btn {
  padding: 24rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
}

.ocr-result {
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.result-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
  font-family: monospace;
}

.ocr-actions {
  display: flex;
  gap: 20rpx;
}

.ocr-actions .btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
}

.loading-card {
  text-align: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 0;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 20rpx;
  font-size: 28rpx;
  color: #666;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  width: 90%;
  max-width: 600rpx;
  max-height: 80vh;
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
}

.modal-close {
  font-size: 48rpx;
  line-height: 1;
}

.modal-body {
  flex: 1;
  padding: 30rpx;
  max-height: 400rpx;
  overflow-y: auto;
}

.group-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
  border-radius: 8rpx;
}

.group-option.selected {
  background: #f0f0ff;
  border-color: #667eea;
}

.group-option.new-group {
  justify-content: center;
  color: #667eea;
  margin-top: 16rpx;
}

.group-count {
  font-size: 24rpx;
  color: #999;
}

.form-item {
  margin-bottom: 24rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 12rpx;
  font-size: 28rpx;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 8rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  gap: 20rpx;
  padding: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.modal-footer .btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
}
</style>