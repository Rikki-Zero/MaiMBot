import asyncio
from typing import Callable, Optional
from functools import wraps

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

    _task: Optional[asyncio.Task] = None  # 任务实例

    _hooks: dict[TaskHookType, list["TaskItem"]] = {}  # 任务钩子

    def __init__(
        self, fn: Callable, task_type: TaskType, loop: bool = False, priority: int = 0, timeout: Optional[float] = None
    ):
        """
        初始化任务项
        :param fn: 任务函数，可以是同步或异步
        :param task_type: 任务类型
        :param loop: 是否循环执行任务
        :param priority: 任务优先级
        :param timeout: 任务超时时间
        """
        self.fn: asyncio.coroutines
        self.task_type = task_type
        self.loop = loop
        self.priority = priority
        self.timeout = timeout

        @wraps(fn)
        def fn_loop_thread(self, *args, **kwargs):
            """循环执行任务"""
            print("fn_loop_thread")
            while task_manager.get_is_running():
                fn(*args, **kwargs)

        @wraps(fn)
        async def fn_loop_coroutine(self, *args, **kwargs):
            """循环执行任务"""
            print("ssssssssssssssssssssss")
            while task_manager.get_is_running():
                await fn(*args, **kwargs)

        # 如果需要循环执行任务，则将任务函数包装为循环执行任务
        if self.loop:
            # 根据任务类型选择循环执行任务的函数
            if self.task_type == TaskType.COROUTINE:
                self.fn = fn_loop_coroutine
            elif self.task_type == TaskType.THREAD:
                self.fn = asyncio.to_thread(fn_loop_thread, *args, **kwargs)
        else:
            self.fn = fn

        fn_name = self.fn.__name__
        # 动态添加TaskHookType枚举项作为属性
        for hook_type in TaskHookType:
            # 更新实例的具体hook chain名称
            # 例如：on_startup.AFTER_START = "on_startup_after_start"
            setattr(self, hook_type.name, f"{fn_name}_{hook_type.value}")

    def run_hook(self, hook_type: TaskHookType, *args, **kwargs) -> None:
        """
        执行钩子

        param:
            hook_type: 钩子类型
            args: 参数
            kwargs: 关键字参数
        """
        task_manager.submit(hook_type, *args, **kwargs)

    async def get_coroutine(self):
        """获取任务"""
        if self.task_type == TaskType.COROUTINE:
            return self.fn
        elif self.task_type == TaskType.THREAD:
            return self.fn_loop_thread

    async def start(self, *args, **kwargs) -> None:
        """启动任务"""
        # 执行BEFORE_START钩子
        self.run_hook(self.BEFORE_START)

        # 启动主任务
        # 在 TaskManager 里面的 run 方法中已经处理了参数过滤
        if self.task_type == TaskType.COROUTINE:
            self._task = asyncio.create_task(self.fn(*args, **kwargs))
        elif self.task_type == TaskType.THREAD:
            self._task = asyncio.create_task()

        # 执行AFTER_START钩子
        self.run_hook(self.AFTER_START)

    def stop(self) -> None:
        """停止任务"""
        if self._task:
            # 执行BEFORE_STOP钩子
            self.run_hook(self.BEFORE_STOP)

            try:
                self._task.cancel()

                # 执行AFTER_STOP和ON_SUCCESS钩子
                self.run_hook(self.AFTER_STOP)

            except Exception as e:
                # 执行ON_ERROR钩子
                self.run_hook(self.ON_CANCEL_ERROR)
                raise e

            # 如果设置了超时且触发超时
            if self.timeout and self._task.is_alive():
                self.run_hook(self.ON_TIMEOUT)
