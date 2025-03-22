import asyncio
from functools import wraps
from inspect import signature
from typing import Callable, Optional, Union

from .TaskRegister import task_register
from .TaskManager import task_manager
from .TaskTypes import TaskStage, TaskType, TaskHookType
from .TaskItem import TaskItem


# 这个部分是专门用来实现装饰器功能的
# 用来注册函数
class Task:
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

    ON_TIMEOUT = "on_timeout"  # 任务超时后

    # 类属性
    # 注册必须
    on: Union[TaskStage, TaskHookType] = None  # 任务钩子类型

    # task_item属性
    fn: Optional[Callable] = None  # 任务函数，可以是同步或异步
    name: str  # 任务名称
    type: TaskType = None  # 任务类型
    timeout: Optional[float] = None  # 任务超时时间
    priority: int = 0  # 任务优先级

    _task: Optional[asyncio.Task] = None  # 任务实例

    _hooks: dict[TaskHookType, list["TaskItem"]] = {}  # 任务钩子


    def __init__(
        self,
        on: Union[TaskStage, TaskHookType],
        fn: asyncio.Coroutine,
        type: Optional[TaskType] = None,
        loop: bool = False,
        priority: int = 0,
        timeout: Optional[float] = None,
    ):
        """
        初始化任务项

        param:
            on: 任务钩子类型
            fn: 任务函数，可以是同步或异步
            type: 任务类型
            loop: 是否循环执行任务
            priority: 任务优先级
            timeout: 任务超时时间
        """
        self.on = on
        self.fn: asyncio.Coroutine
        self.type = type
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
                self.fn = asyncio.to_thread(fn_loop_thread)
        else:
            self.fn = fn

        fn_name = self.fn.__name__
        # 动态添加TaskHookType枚举项作为属性
        for hook_type in TaskHookType:
            # 更新实例的具体hook chain名称
            # 例如：on_startup.AFTER_START = "on_startup_after_start"
            setattr(self, hook_type.name, f"{fn_name}_{hook_type.value}")

    def __call__(self, fn: Callable) -> TaskItem:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 参数过滤逻辑
            sig = signature(fn)
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

            return fn(*args, **filtered_kwargs)

        # 自动识别任务类型
        if self.type is None:
            self.type = TaskType.COROUTINE if asyncio.iscoroutinefunction(fn) else TaskType.THREAD

        # 创建TaskItem
        task_item = TaskItem(
            fn=wrapper, task_type=self.type, loop=self.loop, priority=self.priority, timeout=self.timeout
        )

        # 注册任务
        if isinstance(self.on, TaskStage):
            task_register.register_stage_task(self.on, task_item)
        else:
            # 如果是Hook任务
            task_register.register_hook_task(self.on, task_item)

        return task_item
