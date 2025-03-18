if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    print(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import time

from task import Task,TaskStage,TaskType
from task.TaskManager import task_manager

@Task(on=TaskStage.ON_STARTUP,type=TaskType.PROCESS,priority=1)
def on_startup():
    print("on_startup")
    while True:
        print("on_startup_loop")
        time.sleep(1)

print("aft",on_startup.AFTER_START)

@Task(on=on_startup.AFTER_START,type=TaskType.COROUTINE)
async def on_startup_BEFORE_START():
    print("on_startup_BEFORE_START")
    await asyncio.sleep(5)
    print("on_startup_BEFORE_START_5")

print("task_manager run")
task_manager.run(TaskStage.ON_STARTUP)

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