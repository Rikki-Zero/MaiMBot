from functools import wraps
from typing import Callable,Optional, Union
from inspect import signature
from asyncio import iscoroutinefunction

from .TaskRegister import task_register
from .TaskTypes import TaskStage,TaskType,TaskHookType
from .TaskItem import TaskItem

class Task:
    def __init__(self, 
                 on: Union[TaskStage, TaskHookType], 
                 type: Optional[TaskType] = None,
                 timeout: Optional[float] = 0.0,
                 priority: int = 0):
        self.on = on
        self.type = type
        self.timeout = timeout
        self.priority = priority

    def __call__(self, func: Callable) -> TaskItem:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 参数过滤逻辑
            sig = signature(func)
            filtered_kwargs = {
                k: v for k, v in kwargs.items() 
                if k in sig.parameters
            }
            return func(*args, **filtered_kwargs)

        # 自动识别任务类型
        if self.type is None:
            self.type = TaskType.COROUTINE if iscoroutinefunction(func) else TaskType.THREAD

        # 创建TaskItem
        task_item = TaskItem(
            fn=wrapper,
            task_type=self.type,
            priority=self.priority
        )

        # 注册任务
        if isinstance(self.on, TaskStage):
            task_register.register_stage_task(self.on, task_item)
        else:
            # 如果是Hook任务
            task_register.register_hook_task(self.on, task_item)

        return task_item