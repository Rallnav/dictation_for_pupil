<template>
  <view class="container">
    <view class="card">
      <view class="toolbar">
        <button class="btn btn-primary" @tap="showAddModal">添加组别</button>
        <button class="btn btn-secondary" @tap="importGroups">导入</button>
        <button class="btn btn-secondary" @tap="exportGroups">导出</button>
      </view>
    </view>

    <view class="card">
      <view class="title">组别列表</view>
      <view class="group-table">
        <view class="table-header">
          <text class="col-id">ID</text>
          <text class="col-name">名称</text>
          <text class="col-count">词汇数</text>
          <text class="col-action">操作</text>
        </view>
        <scroll-view scroll-y style="max-height: 600rpx;">
          <view
            v-for="(group, id) in groups"
            :key="id"
            class="table-row"
          >
            <text class="col-id">{{ id }}</text>
            <text class="col-name">{{ group.name }}</text>
            <text class="col-count">{{ group.content.length }}</text>
            <view class="col-action">
              <text class="action-btn edit" @tap="editGroup(id)">编辑</text>
              <text class="action-btn delete" @tap="deleteGroup(id)">删除</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 添加/编辑弹窗 -->
    <view class="modal" v-if="showModal">
      <view class="modal-mask" @tap="closeModal"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">{{ isEditing ? '编辑组别' : '添加组别' }}</text>
          <text class="modal-close" @tap="closeModal">×</text>
        </view>
        <view class="modal-body">
          <view class="form-item" v-if="!isEditing">
            <text class="form-label">组别ID</text>
            <input class="form-input" v-model="formData.id" placeholder="请输入组别ID" />
          </view>
          <view class="form-item">
            <text class="form-label">组别名称</text>
            <input class="form-input" v-model="formData.name" placeholder="请输入组别名称" />
          </view>
          <view class="form-item">
            <text class="form-label">词汇（每行一个）</text>
            <textarea class="form-textarea" v-model="formData.content" placeholder="apple\nbook\ncat"></textarea>
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn btn-secondary" @tap="closeModal">取消</button>
          <button class="btn btn-primary" @tap="saveGroup">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      groups: {},
      showModal: false,
      isEditing: false,
      editingId: '',
      formData: {
        id: '',
        name: '',
        content: ''
      }
    }
  },
  onLoad() {
    this.loadData()
  },
  onShow() {
    this.loadData()
  },
  onPullDownRefresh() {
    this.loadData()
    uni.stopPullDownRefresh()
  },
  methods: {
    loadData() {
      const groupsData = uni.getStorageSync('dictation_groups')
      if (groupsData) {
        this.groups = JSON.parse(groupsData)
      }
    },

    showAddModal() {
      this.isEditing = false
      this.formData = {
        id: '',
        name: '',
        content: ''
      }
      this.showModal = true
    },

    editGroup(id) {
      this.isEditing = true
      this.editingId = id
      const group = this.groups[id]
      this.formData = {
        id: id,
        name: group.name,
        content: group.content.join('\n')
      }
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
    },

    saveGroup() {
      if (!this.formData.name) {
        uni.showToast({ title: '请输入组别名称', icon: 'none' })
        return
      }

      if (!this.formData.content) {
        uni.showToast({ title: '请输入词汇', icon: 'none' })
        return
      }

      const content = this.formData.content
        .split('\n')
        .map(item => item.trim())
        .filter(item => item)

      if (content.length === 0) {
        uni.showToast({ title: '词汇不能为空', icon: 'none' })
        return
      }

      if (this.isEditing) {
        this.groups[this.editingId] = {
          name: this.formData.name,
          content: content
        }
      } else {
        if (!this.formData.id) {
          uni.showToast({ title: '请输入组别ID', icon: 'none' })
          return
        }
        if (this.groups[this.formData.id]) {
          uni.showToast({ title: '该ID已存在', icon: 'none' })
          return
        }
        this.groups[this.formData.id] = {
          name: this.formData.name,
          content: content
        }
      }

      uni.setStorageSync('dictation_groups', JSON.stringify(this.groups))
      this.closeModal()
      this.loadData()
      uni.showToast({
        title: this.isEditing ? '更新成功' : '添加成功',
        icon: 'success'
      })
    },

    deleteGroup(id) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除组别 "${this.groups[id].name}" 吗？`,
        success: (res) => {
          if (res.confirm) {
            delete this.groups[id]
            uni.setStorageSync('dictation_groups', JSON.stringify(this.groups))
            this.loadData()
            uni.showToast({ title: '删除成功', icon: 'success' })
          }
        }
      })
    },

    importGroups() {
      uni.chooseMessageFile({
        count: 1,
        type: 'file',
        success: (res) => {
          const file = res.tempFiles[0]
          if (!file.name.endsWith('.json')) {
            uni.showToast({ title: '请选择JSON文件', icon: 'none' })
            return
          }

          uni.getFileSystemManager().readFile({
            filePath: file.path,
            success: (readRes) => {
              try {
                const data = JSON.parse(readRes.data)
                if (data.groups) {
                  Object.assign(this.groups, data.groups)
                } else {
                  Object.assign(this.groups, data)
                }
                uni.setStorageSync('dictation_groups', JSON.stringify(this.groups))
                this.loadData()
                uni.showToast({ title: '导入成功', icon: 'success' })
              } catch (e) {
                uni.showToast({ title: '文件格式错误', icon: 'none' })
              }
            },
            fail: () => {
              uni.showToast({ title: '读取文件失败', icon: 'none' })
            }
          })
        }
      })
    },

    exportGroups() {
      const data = { groups: this.groups }
      const fileName = `dictation_groups_${Date.now()}.json`
      const filePath = `${wx.env.USER_DATA_PATH}/${fileName}`

      uni.getFileSystemManager().writeFile({
        filePath: filePath,
        data: JSON.stringify(data, null, 2),
        success: () => {
          uni.shareFileMessage({
            filePath: filePath,
            fileName: fileName,
            success: () => {
              uni.showToast({ title: '导出成功', icon: 'success' })
            },
            fail: () => {
              uni.showToast({ title: '导出失败', icon: 'none' })
            }
          })
        },
        fail: () => {
          uni.showToast({ title: '创建文件失败', icon: 'none' })
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

.toolbar {
  display: flex;
  gap: 20rpx;
}

.toolbar .btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
}

.group-table {
  background: #fff;
  border-radius: 12rpx;
  overflow: hidden;
}

.table-header {
  display: flex;
  padding: 24rpx 16rpx;
  background: #667eea;
  color: #fff;
  font-size: 26rpx;
  font-weight: 500;
}

.table-row {
  display: flex;
  padding: 24rpx 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
  font-size: 26rpx;
}

.table-row:last-child {
  border-bottom: none;
}

.col-id {
  width: 160rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-count {
  width: 100rpx;
  text-align: center;
}

.col-action {
  width: 160rpx;
  display: flex;
  gap: 16rpx;
}

.action-btn {
  padding: 8rpx 16rpx;
  border-radius: 6rpx;
  font-size: 24rpx;
}

.action-btn.edit {
  background: #2196F3;
  color: #fff;
}

.action-btn.delete {
  background: #f44336;
  color: #fff;
}

/* 模态框 */
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
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
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
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
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

.form-textarea {
  width: 100%;
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 8rpx;
  font-size: 28rpx;
  min-height: 200rpx;
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