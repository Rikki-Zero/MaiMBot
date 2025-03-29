from functools import wraps
from typing import Callable, Optional, Union
from inspect import signature
from asyncio import iscoroutinefunction

from .TaskRegister import task_register
from .TaskTypes import TaskStage, TaskType, TaskHookType
from .TaskItem import TaskItem


class Task:
    on: Union[TaskStage, TaskHookType]
    task_type: TaskType
    loop: bool
    timeout: Optional[float]
    priority: int

    def __init__(
        self,
        on: Union[TaskStage, TaskHookType],
        task_type: TaskType = None,
        priority: int = 0,
        timeout: Optional[float] = None,
    ):
        """
        任务装饰器

        param:
            on: 任务执行位置
            task_type: 任务类型
            priority: 任务优先级
            timeout: 任务超时时间
        """
        self.on = on
        self.task_type = task_type
        self.timeout = timeout
        self.priority = priority

    def __call__(self, func: Callable) -> TaskItem:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 参数过滤逻辑
            sig = signature(func)
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

            return func(*args, **filtered_kwargs)

        # 自动识别任务类型
        if self.task_type is None:
            self.task_type = TaskType.COROUTINE if iscoroutinefunction(func) else TaskType.THREAD

        # 创建TaskItem
        task_item = TaskItem(fn=wrapper, task_type=self.task_type, priority=self.priority, timeout=self.timeout)

        # 注册任务
        if isinstance(self.on, TaskStage):
            task_register.register_stage_task(self.on, task_item)
        else:
            # 如果是Hook任务
            task_register.register_hook_task(self.on, task_item)

        return task_item
