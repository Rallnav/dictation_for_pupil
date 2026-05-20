import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from .group_service import GroupService
from .audio_service import AudioService
import uvicorn
import threading
import time


class GroupItem(BaseModel):
    """组别数据模型"""
    group_id: str
    name: str
    content: List[str]


class DictationConfig(BaseModel):
    """听写配置"""
    groups: List[str]
    interval: Optional[int] = 3
    repeat_count: Optional[int] = 2
    shuffle: Optional[bool] = True
    long_word_extension: Optional[bool] = False


class DictationResult(BaseModel):
    """听写结果"""
    success: bool
    message: str
    dictated_words: Optional[List[str]] = None


class ApiService:
    """REST API服务"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.app = FastAPI(title='听写软件 API', version='1.0')
        self.group_service = GroupService(config_path)
        self.audio_service = AudioService(config_path)
        self._setup_routes()
        self.server = None
        self.running = False
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get('/api/groups', response_model=Dict[str, Any])
        def get_groups():
            """获取所有组别"""
            return self.group_service.get_groups()
        
        @self.app.get('/api/groups/{group_id}', response_model=Dict[str, Any])
        def get_group(group_id: str):
            """获取单个组别"""
            try:
                return self.group_service.get_group(group_id)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.app.post('/api/groups', response_model=Dict[str, Any])
        def add_group(group: GroupItem):
            """添加新组别"""
            new_id = self.group_service.add_group(group.group_id, group.name, group.content)
            return {'group_id': new_id, 'name': group.name, 'content': group.content}
        
        @self.app.put('/api/groups/{group_id}', response_model=Dict[str, str])
        def update_group(group_id: str, name: Optional[str] = None, content: Optional[List[str]] = None):
            """更新组别"""
            try:
                self.group_service.update_group(group_id, name, content)
                return {'message': '更新成功'}
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.app.delete('/api/groups/{group_id}', response_model=Dict[str, str])
        def delete_group(group_id: str):
            """删除组别"""
            try:
                self.group_service.delete_group(group_id)
                return {'message': '删除成功'}
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.app.get('/api/config', response_model=Dict[str, Any])
        def get_config():
            """获取配置"""
            return {
                'interval': self.group_service.get_interval(),
                'repeat_count': self.group_service.get_repeat_count(),
                'long_word_extension': self.group_service.get_long_word_extension(),
                'selected_groups': self.group_service.get_selected_groups()
            }
        
        @self.app.post('/api/config', response_model=Dict[str, str])
        def update_config(interval: Optional[int] = None, repeat_count: Optional[int] = None,
                          long_word_extension: Optional[bool] = None):
            """更新配置"""
            if interval is not None:
                self.group_service.set_interval(interval)
            if repeat_count is not None:
                self.group_service.set_repeat_count(repeat_count)
            if long_word_extension is not None:
                self.group_service.set_long_word_extension(long_word_extension)
            return {'message': '配置更新成功'}
        
        @self.app.post('/api/dictate', response_model=DictationResult)
        def start_dictation(config: DictationConfig):
            """开始听写"""
            try:
                if not config.groups:
                    raise HTTPException(status_code=400, detail='请指定至少一个组别')
                
                # 获取所有要听写的内容
                all_content = []
                for group_id in config.groups:
                    try:
                        content = self.group_service.get_group_content(group_id)
                        all_content.extend(content)
                    except ValueError:
                        raise HTTPException(status_code=404, detail=f'组别 {group_id} 不存在')
                
                if not all_content:
                    return {'success': True, 'message': '没有词汇需要听写', 'dictated_words': []}
                
                # 执行听写
                interval = config.interval if config.interval else self.group_service.get_interval()
                repeat_count = config.repeat_count if config.repeat_count else self.group_service.get_repeat_count()
                shuffle = config.shuffle if config.shuffle is not None else True
                long_word_extension = config.long_word_extension if config.long_word_extension is not None else False
                
                # 在后台线程中执行听写
                def run_dictation():
                    self.audio_service.dictate(all_content, interval, repeat_count, shuffle, long_word_extension)
                
                thread = threading.Thread(target=run_dictation)
                thread.start()
                
                return {
                    'success': True,
                    'message': '听写已开始',
                    'dictated_words': all_content
                }
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get('/api/selected_groups', response_model=List[str])
        def get_selected_groups():
            """获取已选组别"""
            return self.group_service.get_selected_groups()
        
        @self.app.post('/api/selected_groups', response_model=Dict[str, str])
        def set_selected_groups(groups: List[str]):
            """设置已选组别"""
            self.group_service.set_selected_groups(groups)
            return {'message': '已选组别更新成功'}
        
        @self.app.get('/')
        def root():
            """健康检查"""
            return {'status': 'ok', 'service': 'dictation-api'}
    
    def start(self, host: str = '127.0.0.1', port: int = 8000):
        """启动API服务"""
        self.running = True
        self.server = uvicorn.Server(
            uvicorn.Config(
                self.app,
                host=host,
                port=port,
                log_level='info'
            )
        )
        
        async def run_server():
            await self.server.serve()
        
        self.thread = threading.Thread(target=asyncio.run, args=(run_server(),))
        self.thread.start()
        print(f'API服务已启动: http://{host}:{port}')
        print(f'Swagger文档: http://{host}:{port}/docs')
    
    def stop(self):
        """停止API服务"""
        if self.server:
            self.server.should_exit = True
            self.running = False
            print('API服务已停止')


if __name__ == '__main__':
    service = ApiService()
    service.start(host='0.0.0.0', port=8000)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
