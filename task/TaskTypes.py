from enum import Enum


class TaskStage(Enum):
    """
    任务阶段枚举类，定义不同的任务处理阶段
    """

    ON_STARTUP = "on_startup"  # 程序启动阶段
    ON_CONNECT = "on_connect"  # 连接建立阶段
    ON_MESSAGE = "on_message"  # 消息接收阶段
    ON_NOTICE = "on_notice"  # 通知处理阶段


class TaskHookType(Enum):
    """
    任务钩子类型枚举类，定义不同的任务钩子类型
    """

    BEFORE_START = "before_start"  # 任务开始前
    AFTER_START = "after_start"  # 任务结束后
    BEFORE_STOP = "before_stop"  # 任务停止前
    AFTER_STOP = "after_stop"  # 任务停止后

    ON_SYNC_SUCCESS = "on_sync_success"  # 任务成功后
    ON_SYNC_ERROR = "on_sync_error"  # 任务失败后

    ON_CANCEL_ERROR = "on_cancel_error"  # 任务取消失败后

    ON_TIMEOUT = "on_timeout"  # 任务超时后


class TaskType(Enum):
    """任务类型枚举类，定义不同的任务执行方式
    SYNC: 同步任务，在调度子线程中需要执行完成才会继续执行链中后方的任务
    COROUTINE、PROCESS、THREAD: 在调度子线程中被读到时会立即创建相关上下文
    不发生阻塞，可以立即执行链中后方的任务
    """

    SYNC = "sync"  # 同步任务，要确保程序短小，不然容易导致被调度器子线程卡住
    COROUTINE = "coroutine"  # 协程任务
    PROCESS = "process"  # 进程任务
    THREAD = "thread"  # 线程任务
