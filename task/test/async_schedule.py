if __name__ == "__main__":
    import sys
    import os

    sys.path.append("/home/rikki/WorkSpace/Dev/MaiMBot/")

import asyncio
import time

from task import Task, TaskStage, TaskType
from task.TaskManager import task_manager


@Task(on=TaskStage.ON_STARTUP, priority=1)
def on_startup():
    print("on_startup")
    while True:
        print("on_startup_loop")
        time.sleep(1)


print("aft", on_startup.AFTER_START)


@Task(on=on_startup.AFTER_START,priority=1)
async def on_startup_BEFORE_START_1():
    print("on_startup_BEFORE_START")
    await asyncio.sleep(5)
    print("on_startup_BEFORE_START_5")

@Task(on=on_startup.AFTER_START,priority=2)
async def on_startup_BEFORE_START_2():
    print("on_startup_BEFORE_START")
    await asyncio.sleep(5)
    print("on_startup_BEFORE_START_5")


if __name__ == "__main__":
    def keyboard(task):
        print("键盘中断")

    def final(task):
        print("收尾")

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
