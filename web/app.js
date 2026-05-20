/**
 * 听写软件前端版 - 核心应用逻辑
 * 
 * 功能特性：
 * 1. 纯前端实现，无需后端也可运行
 * 2. 支持配置开启后台通信模式
 * 3. 使用 localStorage 存储数据
 * 4. 集成 Tesseract.js 实现前端 OCR
 * 5. 使用 Web Speech API 实现语音合成
 */

class DictationApp {
    constructor() {
        this.init();
    }

    init() {
        // 加载配置
        this.loadSettings();
        
        // 初始化数据
        this.initData();
        
        // 绑定事件
        this.bindEvents();
        
        // 初始化语音合成
        this.initSpeech();
        
        // 初始化 OCR
        this.initOCR();
        
        // 渲染界面
        this.renderGroupList();
        this.renderGroupsTable();
    }

    // 加载设置
    loadSettings() {
        const settings = localStorage.getItem('dictation_settings');
        if (settings) {
            this.settings = JSON.parse(settings);
        } else {
            this.settings = {
                backendUrl: 'http://localhost:8000',
                voiceType: 'zh-CN-XiaoxiaoNeural',
                defaultInterval: 3,
                defaultRepeat: 2,
                autoSave: true,
                useBackend: false
            };
        }
        
        // 更新 UI
        document.getElementById('backendUrl').value = this.settings.backendUrl;
        document.getElementById('voiceType').value = this.settings.voiceType;
        document.getElementById('defaultInterval').value = this.settings.defaultInterval;
        document.getElementById('defaultRepeat').value = this.settings.defaultRepeat;
        document.getElementById('autoSave').checked = this.settings.autoSave;
        document.getElementById('useBackend').checked = this.settings.useBackend;
        document.getElementById('interval').value = this.settings.defaultInterval;
        document.getElementById('repeatCount').value = this.settings.defaultRepeat;
    }

    // 保存设置
    saveSettings() {
        this.settings = {
            backendUrl: document.getElementById('backendUrl').value,
            voiceType: document.getElementById('voiceType').value,
            defaultInterval: parseInt(document.getElementById('defaultInterval').value),
            defaultRepeat: parseInt(document.getElementById('defaultRepeat').value),
            autoSave: document.getElementById('autoSave').checked,
            useBackend: document.getElementById('useBackend').checked
        };
        localStorage.setItem('dictation_settings', JSON.stringify(this.settings));
        this.showNotification('设置已保存', 'success');
    }

    // 初始化数据
    initData() {
        const data = localStorage.getItem('dictation_groups');
        if (data) {
            this.groups = JSON.parse(data);
        } else {
            // 默认数据
            this.groups = {
                'group1': {
                    name: '基础单词',
                    content: ['apple', 'book', 'cat', 'dog', 'egg']
                },
                'group2': {
                    name: '数字单词',
                    content: ['one', 'two', 'three', 'four', 'five']
                },
                'group3': {
                    name: '颜色单词',
                    content: ['red', 'blue', 'green', 'yellow', 'black']
                }
            };
            this.saveData();
        }
    }

    // 保存数据
    saveData() {
        if (this.settings.autoSave) {
            localStorage.setItem('dictation_groups', JSON.stringify(this.groups));
        }
    }

    // 绑定事件
    bindEvents() {
        // 导航切换
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // 设置开关
        document.getElementById('useBackend').addEventListener('change', (e) => {
            this.settings.useBackend = e.target.checked;
            this.saveSettings();
            this.showNotification(
                e.target.checked ? '已启用后台模式' : '已切换到本地模式',
                'success'
            );
        });

        // 听写控制
        document.getElementById('startDictation').addEventListener('click', () => {
            this.startDictation();
        });
        document.getElementById('pauseDictation').addEventListener('click', () => {
            this.togglePause();
        });
        document.getElementById('stopDictation').addEventListener('click', () => {
            this.stopDictation();
        });

        // 组别管理
        document.getElementById('addGroup').addEventListener('click', () => {
            this.openGroupModal();
        });
        document.getElementById('importGroups').addEventListener('click', () => {
            this.importGroups();
        });
        document.getElementById('exportGroups').addEventListener('click', () => {
            this.exportGroups();
        });

        // 组别表单
        document.getElementById('groupForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveGroup();
        });
        document.getElementById('cancelModal').addEventListener('click', () => {
            this.closeGroupModal();
        });
        document.querySelector('.close').addEventListener('click', () => {
            this.closeGroupModal();
        });

        // 设置页面
        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });
        document.getElementById('resetSettings').addEventListener('click', () => {
            this.resetSettings();
        });
        document.getElementById('clearData').addEventListener('click', () => {
            this.clearData();
        });

        // OCR 功能
        document.getElementById('startCamera').addEventListener('click', () => {
            this.startCamera();
        });
        document.getElementById('captureImage').addEventListener('click', () => {
            this.captureImage();
        });
        document.getElementById('uploadImage').addEventListener('click', () => {
            document.getElementById('imageUpload').click();
        });
        document.getElementById('imageUpload').addEventListener('change', (e) => {
            this.uploadImage(e);
        });
        document.getElementById('addToGroup').addEventListener('click', () => {
            this.addOcrResultToGroup();
        });
        document.getElementById('clearOcr').addEventListener('click', () => {
            this.clearOcr();
        });

        // 模态框点击外部关闭
        document.getElementById('groupModal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('groupModal')) {
                this.closeGroupModal();
            }
        });
    }

    // 切换标签页
    switchTab(tabId) {
        // 更新导航按钮状态
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // 切换内容显示
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');
    }

    // 渲染组别列表（听写页面）
    renderGroupList() {
        const container = document.getElementById('groupList');
        container.innerHTML = '';

        Object.entries(this.groups).forEach(([id, group]) => {
            const item = document.createElement('div');
            item.className = 'group-item';
            item.innerHTML = `
                <input type="checkbox" data-id="${id}">
                <div class="group-info">
                    <h4>${group.name}</h4>
                    <p>${group.content.length} 个词汇</p>
                </div>
            `;

            const checkbox = item.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', () => {
                this.updateSelectedCount();
            });

            container.appendChild(item);
        });

        this.updateSelectedCount();
    }

    // 更新已选数量
    updateSelectedCount() {
        const count = document.querySelectorAll('#groupList input[type="checkbox"]:checked').length;
        document.getElementById('selectedCount').textContent = count;
    }

    // 获取选中的组别
    getSelectedGroups() {
        const selected = [];
        document.querySelectorAll('#groupList input[type="checkbox"]:checked').forEach(checkbox => {
            selected.push(checkbox.dataset.id);
        });
        return selected;
    }

    // 渲染组别表格（管理页面）
    renderGroupsTable() {
        const tbody = document.getElementById('groupsTableBody');
        tbody.innerHTML = '';

        Object.entries(this.groups).forEach(([id, group]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${id}</td>
                <td>${group.name}</td>
                <td>${group.content.length}</td>
                <td>
                    <div class="table-actions">
                        <button class="table-btn edit" data-id="${id}">编辑</button>
                        <button class="table-btn delete" data-id="${id}">删除</button>
                    </div>
                </td>
            `;

            // 编辑按钮
            row.querySelector('.edit').addEventListener('click', () => {
                this.editGroup(id);
            });

            // 删除按钮
            row.querySelector('.delete').addEventListener('click', () => {
                this.deleteGroup(id);
            });

            tbody.appendChild(row);
        });
    }

    // 打开组别模态框
    openGroupModal() {
        document.getElementById('modalTitle').textContent = '添加组别';
        document.getElementById('groupId').value = '';
        document.getElementById('groupFormId').value = '';
        document.getElementById('groupFormName').value = '';
        document.getElementById('groupFormContent').value = '';
        document.getElementById('groupFormId').disabled = false;
        document.getElementById('groupModal').style.display = 'block';
    }

    // 编辑组别
    editGroup(id) {
        const group = this.groups[id];
        document.getElementById('modalTitle').textContent = '编辑组别';
        document.getElementById('groupId').value = id;
        document.getElementById('groupFormId').value = id;
        document.getElementById('groupFormName').value = group.name;
        document.getElementById('groupFormContent').value = group.content.join('\n');
        document.getElementById('groupFormId').disabled = true;
        document.getElementById('groupModal').style.display = 'block';
    }

    // 关闭模态框
    closeGroupModal() {
        document.getElementById('groupModal').style.display = 'none';
    }

    // 保存组别
    saveGroup() {
        const id = document.getElementById('groupId').value || document.getElementById('groupFormId').value;
        const name = document.getElementById('groupFormName').value;
        const content = document.getElementById('groupFormContent').value
            .split('\n')
            .map(item => item.trim())
            .filter(item => item);

        if (!id || !name || content.length === 0) {
            this.showNotification('请填写完整信息', 'error');
            return;
        }

        // 检查是否是新组别
        const isNew = !this.groups[id];

        // 如果是后台模式，调用 API
        if (this.settings.useBackend) {
            this.saveGroupToBackend(id, name, content, isNew);
            return;
        }

        // 本地模式
        this.groups[id] = { name, content };
        this.saveData();
        this.closeGroupModal();
        this.renderGroupList();
        this.renderGroupsTable();
        
        this.showNotification(
            isNew ? '组别添加成功' : '组别更新成功',
            'success'
        );
    }

    // 删除组别
    deleteGroup(id) {
        if (!confirm(`确定要删除组别 "${this.groups[id].name}" 吗？`)) {
            return;
        }

        // 如果是后台模式，调用 API
        if (this.settings.useBackend) {
            this.deleteGroupFromBackend(id);
            return;
        }

        // 本地模式
        delete this.groups[id];
        this.saveData();
        this.renderGroupList();
        this.renderGroupsTable();
        this.showNotification('组别删除成功', 'success');
    }

    // 导入组别
    importGroups() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    if (data.groups) {
                        Object.assign(this.groups, data.groups);
                    } else {
                        Object.assign(this.groups, data);
                    }
                    this.saveData();
                    this.renderGroupList();
                    this.renderGroupsTable();
                    this.showNotification('导入成功', 'success');
                } catch (error) {
                    this.showNotification('导入失败，文件格式错误', 'error');
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }

    // 导出组别
    exportGroups() {
        const data = { groups: this.groups };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dictation_groups.json';
        a.click();
        URL.revokeObjectURL(url);
        this.showNotification('导出成功', 'success');
    }

    // 重置设置
    resetSettings() {
        if (!confirm('确定要恢复默认设置吗？')) return;
        
        this.settings = {
            backendUrl: 'http://localhost:8000',
            voiceType: 'zh-CN-XiaoxiaoNeural',
            defaultInterval: 3,
            defaultRepeat: 2,
            autoSave: true,
            useBackend: false
        };
        localStorage.setItem('dictation_settings', JSON.stringify(this.settings));
        this.loadSettings();
        this.showNotification('设置已恢复默认', 'success');
    }

    // 清除数据
    clearData() {
        if (!confirm('确定要清除所有数据吗？此操作不可恢复！')) return;
        
        localStorage.removeItem('dictation_groups');
        localStorage.removeItem('dictation_settings');
        this.initData();
        this.loadSettings();
        this.renderGroupList();
        this.renderGroupsTable();
        this.showNotification('数据已清除', 'success');
    }

    // 显示通知
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // ==================== 听写功能 ====================

    initSpeech() {
        this.synth = window.speechSynthesis;
        this.dictating = false;
        this.paused = false;
        this.stopRequested = false;
        this.dictatedWords = [];
    }

    startDictation() {
        const selectedGroups = this.getSelectedGroups();
        if (selectedGroups.length === 0) {
            this.showNotification('请至少选择一个组别', 'error');
            return;
        }

        // 收集所有词汇
        let allContent = [];
        selectedGroups.forEach(id => {
            if (this.groups[id]) {
                allContent = allContent.concat(this.groups[id].content);
            }
        });

        if (allContent.length === 0) {
            this.showNotification('没有可听写的词汇', 'error');
            return;
        }

        // 获取设置
        const interval = parseInt(document.getElementById('interval').value);
        const repeatCount = parseInt(document.getElementById('repeatCount').value);
        const shuffle = document.getElementById('shuffle').checked;
        const longWordExtension = document.getElementById('longWordExtension').checked;

        // 打乱顺序
        if (shuffle) {
            allContent = this.shuffleArray([...allContent]);
        }

        // 更新 UI
        document.getElementById('startDictation').disabled = true;
        document.getElementById('pauseDictation').disabled = false;
        document.getElementById('stopDictation').disabled = false;
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('progressBar').className = '';
        document.getElementById('wordsList').innerHTML = '';
        this.dictatedWords = [];

        // 开始听写
        this.dictating = true;
        this.paused = false;
        this.stopRequested = false;
        this.currentIndex = 0;
        
        this.runDictation(allContent, interval, repeatCount, longWordExtension);
    }

    async runDictation(content, interval, repeatCount, longWordExtension) {
        const total = content.length * repeatCount;
        let completed = 0;

        for (let i = 0; i < content.length && !this.stopRequested; i++) {
            const word = content[i];
            
            // 检查暂停
            while (this.paused && !this.stopRequested) {
                await this.sleep(100);
            }
            
            if (this.stopRequested) break;

            // 更新进度
            this.currentIndex = i;
            document.getElementById('progressText').textContent = 
                `正在听写: ${word} (${i + 1}/${content.length})`;

            // 记录单词
            if (!this.dictatedWords.includes(word)) {
                this.dictatedWords.push(word);
                this.updateDictatedWords();
            }

            for (let j = 0; j < repeatCount && !this.stopRequested; j++) {
                // 检查暂停
                while (this.paused && !this.stopRequested) {
                    await this.sleep(100);
                }
                
                if (this.stopRequested) break;

                // 播放单词
                await this.speak(word);
                completed++;
                document.getElementById('progressBar').style.width = 
                    `${(completed / total) * 100}%`;

                // 间隔等待
                if (j < repeatCount - 1) {
                    await this.sleep(this.getInterval(word, interval, longWordExtension) * 1000);
                }
            }

            // 单词间间隔
            if (i < content.length - 1 && !this.stopRequested) {
                await this.sleep(this.getInterval(word, interval, longWordExtension) * 1000);
            }
        }

        // 完成
        this.dictating = false;
        document.getElementById('progressText').textContent = '听写完成！';
        document.getElementById('progressBar').className = 'complete';
        document.getElementById('startDictation').disabled = false;
        document.getElementById('pauseDictation').disabled = true;
        document.getElementById('stopDictation').disabled = true;
        document.getElementById('pauseDictation').textContent = '暂停';
        
        if (!this.stopRequested) {
            this.showNotification('听写完成！', 'success');
        }
    }

    getInterval(word, baseInterval, longWordExtension) {
        if (longWordExtension && word.length > 4) {
            return baseInterval + 1;
        }
        return baseInterval;
    }

    async speak(text) {
        return new Promise((resolve) => {
            // 取消之前的语音
            this.synth.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            
            // 设置语音
            const voices = this.synth.getVoices();
            const voice = voices.find(v => 
                v.name.includes(this.settings.voiceType.split('-')[2]?.replace('Neural', '')) ||
                v.lang.startsWith(this.settings.voiceType.split('-')[0])
            );
            
            if (voice) {
                utterance.voice = voice;
            }
            
            utterance.lang = this.settings.voiceType.split('-').slice(0, 2).join('-');
            utterance.rate = 0.8; // 稍慢一点更清晰
            utterance.onend = resolve;
            utterance.onerror = resolve;

            this.synth.speak(utterance);
        });
    }

    togglePause() {
        this.paused = !this.paused;
        
        if (this.paused) {
            this.synth.cancel(); // 停止当前播放
            document.getElementById('pauseDictation').textContent = '继续';
            document.getElementById('progressText').textContent = '已暂停...';
            this.showNotification('听写已暂停', 'warning');
        } else {
            document.getElementById('pauseDictation').textContent = '暂停';
            this.showNotification('继续听写', 'success');
        }
    }

    stopDictation() {
        this.stopRequested = true;
        this.paused = false;
        this.synth.cancel();
        document.getElementById('progressText').textContent = '已停止';
        document.getElementById('startDictation').disabled = false;
        document.getElementById('pauseDictation').disabled = true;
        document.getElementById('stopDictation').disabled = true;
        document.getElementById('pauseDictation').textContent = '暂停';
        this.showNotification('听写已停止', 'warning');
    }

    updateDictatedWords() {
        const container = document.getElementById('wordsList');
        const tag = document.createElement('span');
        tag.className = 'word-tag';
        tag.textContent = this.dictatedWords[this.dictatedWords.length - 1];
        container.appendChild(tag);
    }

    shuffleArray(array) {
        const arr = [...array];
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ==================== OCR 功能 ====================

    initOCR() {
        this.ocrWorker = null;
        this.cameraStream = null;
        this.ocrResult = '';
    }

    async startCamera() {
        try {
            this.cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.getElementById('video');
            video.srcObject = this.cameraStream;
            
            document.getElementById('startCamera').disabled = true;
            document.getElementById('captureImage').disabled = false;
            this.showNotification('摄像头已开启', 'success');
        } catch (error) {
            this.showNotification('无法访问摄像头', 'error');
        }
    }

    captureImage() {
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        this.processImage(canvas);
    }

    uploadImage(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.getElementById('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                this.processImage(canvas);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    async processImage(canvas) {
        this.showNotification('正在识别...', 'success');
        document.getElementById('addToGroup').disabled = true;

        // 初始化 Tesseract
        if (!this.ocrWorker) {
            this.ocrWorker = Tesseract.createWorker({
                logger: (m) => console.log(m)
            });
            await this.ocrWorker.load();
            await this.ocrWorker.loadLanguage('eng+chi_sim');
            await this.ocrWorker.initialize('eng+chi_sim');
        }

        try {
            const result = await this.ocrWorker.recognize(canvas);
            this.ocrResult = result.data.text.trim();
            document.getElementById('ocrText').textContent = this.ocrResult;
            
            if (this.ocrResult) {
                document.getElementById('addToGroup').disabled = false;
                this.showNotification('识别完成', 'success');
            } else {
                this.showNotification('未识别到文字', 'warning');
            }
        } catch (error) {
            this.showNotification('识别失败', 'error');
            console.error(error);
        }
    }

    addOcrResultToGroup() {
        if (!this.ocrResult) return;

        // 解析识别结果，提取单词（每行一个）
        const words = this.ocrResult.split('\n')
            .map(line => line.trim())
            .filter(line => line && line.length > 1);

        if (words.length === 0) {
            this.showNotification('没有可添加的单词', 'warning');
            return;
        }

        // 创建新组别
        const timestamp = Date.now().toString();
        const newGroupId = `ocr_${timestamp}`;
        
        this.groups[newGroupId] = {
            name: `OCR识别_${new Date().toLocaleString()}`,
            content: words
        };
        
        this.saveData();
        this.renderGroupList();
        this.renderGroupsTable();
        
        this.showNotification(`已添加 ${words.length} 个单词到新组别`, 'success');
        this.clearOcr();
    }

    clearOcr() {
        document.getElementById('ocrText').textContent = '';
        document.getElementById('addToGroup').disabled = true;
        this.ocrResult = '';
    }

    // ==================== 后台通信 ====================

    async saveGroupToBackend(id, name, content, isNew) {
        try {
            const url = `${this.settings.backendUrl}/api/groups`;
            const method = isNew ? 'POST' : 'PUT';
            const putUrl = isNew ? url : `${url}/${id}`;

            const response = await fetch(putUrl, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    group_id: id,
                    name: name,
                    content: content
                })
            });

            if (response.ok) {
                this.groups[id] = { name, content };
                this.saveData();
                this.closeGroupModal();
                this.renderGroupList();
                this.renderGroupsTable();
                this.showNotification(
                    isNew ? '组别添加成功' : '组别更新成功',
                    'success'
                );
            } else {
                throw new Error('请求失败');
            }
        } catch (error) {
            this.showNotification('连接后台失败，已保存到本地', 'warning');
            this.groups[id] = { name, content };
            this.saveData();
            this.closeGroupModal();
            this.renderGroupList();
            this.renderGroupsTable();
        }
    }

    async deleteGroupFromBackend(id) {
        try {
            const response = await fetch(
                `${this.settings.backendUrl}/api/groups/${id}`,
                { method: 'DELETE' }
            );

            if (response.ok) {
                delete this.groups[id];
                this.saveData();
                this.renderGroupList();
                this.renderGroupsTable();
                this.showNotification('组别删除成功', 'success');
            } else {
                throw new Error('请求失败');
            }
        } catch (error) {
            this.showNotification('连接后台失败，已删除本地数据', 'warning');
            delete this.groups[id];
            this.saveData();
            this.renderGroupList();
            this.renderGroupsTable();
        }
    }

    async syncWithBackend() {
        if (!this.settings.useBackend) return;

        try {
            // 获取后台数据
            const response = await fetch(`${this.settings.backendUrl}/api/groups`);
            if (response.ok) {
                const data = await response.json();
                this.groups = data;
                this.saveData();
                this.renderGroupList();
                this.renderGroupsTable();
                this.showNotification('已从后台同步数据', 'success');
            }
        } catch (error) {
            this.showNotification('同步失败', 'error');
        }
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DictationApp();
});