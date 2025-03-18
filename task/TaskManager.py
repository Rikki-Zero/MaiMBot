import asyncio
from typing import Union
from inspect import signature
from threading import Thread

from .TaskTypes import TaskStage
from .TaskRegister import task_register


class TaskManager:

    def run(self, on: Union[TaskStage, str], *args, **kwargs):
        chain_key = on
        #TODO: 这里需要判断on是TaskStage还是TaskHookType
        if isinstance(on, TaskStage):
            chain = task_register.get_stage_chains(on, [])
        else:
            chain = task_register.get_hook_chains(on, [])

        task_register.sort_chain(chain_key)

        # 每个链内部开启一个事件循环
        async def execute_chain():
            for task_item in chain:
                # 参数过滤
                sig = signature(task_item.fn)
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
                await task_item.start(*args, **filtered_kwargs)
        
        # 在新线程中执行链
        def wrap_execute_chain():
            asyncio.run(execute_chain())

        Thread(target=wrap_execute_chain).start()


task_manager = TaskManager()

