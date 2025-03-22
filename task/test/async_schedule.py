if __name__ == "__main__":
    import sys
    import os

    sys.path.append("/home/rikki/WorkSpace/Dev/MaiMBot/")

import asyncio
import time

from task import Task, TaskStage
from task.TaskManager import task_manager


@Task(on=TaskStage.ON_STARTUP,loop=True, priority=1)
def on_startup():
    print("on_startup_loop")
    time.sleep(10)

@Task(on=on_startup.BEFORE_START)
def before_startup():
    print("on_startup")


@Task(on=on_startup.AFTER_START,priority=1)
async def on_startup_BEFORE_START_1():
    print("on_startup_BEFORE_START1")
    await asyncio.sleep(5)
    print("on_startup_BEFORE_START1_5")

@Task(on=on_startup.AFTER_START,priority=2)
async def on_startup_BEFORE_START_2():
    print("on_startup_BEFORE_START2")
    await asyncio.sleep(5)
    print("on_startup_BEFORE_START2_5")


if __name__ == "__main__":
    event = asyncio.Event()

    def keyboard(task):
        event.set()
        print("键盘中断")

    def final(task):
        print("收尾")

    task_manager.submit(TaskStage.ON_STARTUP, event=event)
    task_manager.run(KeyboardInterrupt_fn=keyboard, finally_fn=final)

# import asyncio
# import time

# def blocking_task():
#     print("Blocking task started")
#     time.sleep(2)
#     print("Blocking task finished")

# async def coro():
#     print("Coroutine started")
#     await asyncio.to_thread(blocking_task)  # 在后台线程中运行阻塞任务
#     print("Coroutine finished")

# asyncio.run(coro())
