import asyncio
from threading import Thread
from multiprocessing import Process
from typing import Callable, Optional, Union

from .TaskManager import task_manager
from .TaskTypes import TaskType, TaskHookType


class TaskItem:
    """
    任务项类，封装单个任务函数，提供任务执行的相关信息和方法
    主要功能：
    1. 封装任务函数及其类型、优先级等信息
    2. 提供任务启动、停止等操作方法
    3. 支持任务钩子的管理
    """

    BEFORE_START = "before_start"  # 任务开始前
    AFTER_START = "after_start"  # 任务结束后
    BEFORE_STOP = "before_stop"  # 任务停止前
    AFTER_STOP = "after_stop"  # 任务停止后

    ON_SYNC_SUCCESS = "on_sync_success"  # 任务成功后
    ON_SYNC_ERROR = "on_sync_error"  # 任务失败后

    ON_CANCEL_ERROR = "on_cancel_error"  # 任务取消失败后

    ON_TIMEOUT = "on_timeout"  # 任务超时后

    # 类属性
    fn: Optional[Callable] = None  # 任务函数，可以是同步或异步
    name: str  # 任务名称
    task_type: TaskType = None  # 任务类型
    timeout: Optional[float] = None  # 任务超时时间
    priority: int = 0  # 任务优先级
    _task: Optional[Union[asyncio.Task, Thread, Process]] = None  # 任务实例
    _hooks: dict[TaskHookType, list["TaskItem"]] = {}  # 任务钩子

    def __init__(self, fn: Callable, task_type: TaskType, priority: int = 0, timeout: Optional[float] = None):
        """
        初始化任务项
        :param fn: 任务函数，可以是同步或异步
        :param task_type: 任务类型
        :param priority: 任务优先级
        :param timeout: 任务超时时间
        """
        self.fn = fn
        self.task_type = task_type
        self.priority = priority
        self.timeout = timeout

        fn_name = self.fn.__name__
        # 动态添加TaskHookType枚举项作为属性
        for hook_type in TaskHookType:
            # 更新实例的具体hook chain名称
            # 例如：on_startup.AFTER_START = "on_startup_after_start"
            setattr(self, hook_type.name, f"{fn_name}_{hook_type.value}")

    def to_dict(self) -> dict:
        """将任务项转换为字典"""
        return {
            "name": self.name,
            "task_type": self.task_type.value,
            "priority": self.priority,
            "timeout": self.timeout,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskItem":
        """从字典创建任务项"""
        return cls(
            fn=None,  # 需要外部设置
            name=data["name"],
            task_type=TaskType(data["task_type"]),
            priority=data["priority"],
            timeout=data["timeout"],
        )
    
    def run_hook(self, hook_type: TaskHookType, *args, **kwargs) -> None:
        """执行钩子"""
        kwargs['task'] = self  # 将当前任务实例作为task参数传入
        task_manager.run(hook_type, *args, **kwargs)

    async def start(self, *args, **kwargs) -> None:
        """启动任务"""
        # 执行BEFORE_START钩子
        self.run_hook(self.BEFORE_START)
        
        # 启动主任务
        # 在 TaskManager 里面的 run 方法中已经处理了参数过滤
        if self.task_type == TaskType.COROUTINE:
            self._task = asyncio.create_task(self.fn(*args, **kwargs))
            await self._task
        elif self.task_type == TaskType.THREAD:
            self._task = Thread(target=self.fn, args=args, kwargs=kwargs)
            self._task.start()
        elif self.task_type == TaskType.PROCESS:
            self._task = Process(target=self.fn, args=args, kwargs=kwargs)
            self._task.start()
        elif self.task_type == TaskType.SYNC:
            try:
                self.fn(*args, **kwargs)
                self.run_hook(self.ON_SYNC_SUCCESS)
            except Exception as e:
                self.run_hook(self.ON_SYNC_ERROR)
                raise e

        # 执行AFTER_START钩子
        self.run_hook(self.AFTER_START)

    def stop(self) -> None:
        """停止任务"""
        if self._task:
            # 执行BEFORE_STOP钩子
            self.run_hook(self.BEFORE_STOP)
            
            try:
                if self.task_type == TaskType.COROUTINE:
                    self._task.cancel()
                elif self.task_type == TaskType.THREAD:
                    if self._task.is_alive():
                        self._task.join(timeout=self.timeout)
                elif self.task_type == TaskType.PROCESS:
                    if self._task.is_alive():
                        self._task.terminate()
                
                # 执行AFTER_STOP和ON_SUCCESS钩子
                self.run_hook(self.AFTER_STOP)
                
            except Exception as e:
                # 执行ON_ERROR钩子
                self.run_hook(self.ON_CANCEL_ERROR)
                raise e
            
            # 如果设置了超时且触发超时
            if self.timeout and self._task.is_alive():
                self.run_hook(self.ON_TIMEOUT)
