import asyncio
from loguru import logger
from asyncio import AbstractEventLoop
from typing import Union, Callable
from inspect import signature

from .TaskTypes import TaskStage
from .TaskRegister import task_register
from .TaskUtils import fn_filter

class TaskManager:
    main_loop: AbstractEventLoop = None
    task_queue: asyncio.Queue = asyncio.Queue()
    schedule_period: float = 0.1

    is_running: asyncio.Event = asyncio.Event()

    def __init__(self):
        self.set_is_running(True)

    def set_schedule_period(self, period: float = 0.1):
        """设置调度周期"""
        self.schedule_period = period

    async def tasks_shutdown(self):
        """关闭所有协程任务"""
        try:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Task Schedule 关闭异常: {e}")

    async def schedule(self):
        """调度任务"""
        while True:
            # 从队列中获取任务
            task_data = await self.task_queue.get()

            # 从队列中获取到哨兵值，则停止调度
            if task_data is None:
                break

            on, args, kwargs = task_data

            chain_key = on

            task_register.sort_chain(chain_key)

            if isinstance(on, TaskStage):
                chain = task_register.get_stage_chains(on, [])
            else:
                chain = task_register.get_hook_chains(on, [])

            # 执行任务链
            for task_item in chain:
                sig = signature(task_item.fn)
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
                await task_item.start(*args, **filtered_kwargs)

            # 标记任务完成
            self.task_queue.task_done()

    def run(self, KeyboardInterrupt_fn: Callable = None, finally_fn: Callable = None):
        try:
            # 创建事件循环
            self.main_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.main_loop)

            # 执行调度任务
            self.main_loop.run_until_complete(self.schedule())
        except KeyboardInterrupt:
            # 执行键盘中断任务
            if KeyboardInterrupt_fn is not None:
                self.set_is_running(False)
                fn_filter(KeyboardInterrupt_fn, self.main_loop)
        finally:
            # 关闭所有协程任务
            self.main_loop.run_until_complete(self.tasks_shutdown())
            self.main_loop.close()

            # 执行结束任务
            if finally_fn is not None:
                fn_filter(finally_fn, self.main_loop)

    def submit(self, on: Union[TaskStage, str], *args, **kwargs):
        """将任务放入队列"""
        self.task_queue.put_nowait((on, args, kwargs))

    def set_is_running(self, is_running: bool = False):
        """设置是否正在运行"""
        if is_running:
            self.is_running.set()
        else:
            self.is_running.clear()

    def get_is_running(self) -> bool:
        """获取是否正在运行"""
        return self.is_running.is_set()


task_manager = TaskManager()
