from enum import Enum


class TaskStage(Enum):
    """
    任务阶段枚举类，定义不同的任务处理阶段

    Types:
        ON_STARTUP: 程序启动阶段
        ON_CONNECT: 连接建立阶段
        ON_MESSAGE: 消息接收阶段
        ON_NOTICE: 通知处理阶段
    """

    ON_STARTUP = "on_startup"  # 程序启动阶段
    ON_CONNECT = "on_connect"  # 连接建立阶段
    ON_MESSAGE = "on_message"  # 消息接收阶段
    ON_NOTICE = "on_notice"  # 通知处理阶段


class TaskHookType(Enum):
    """
    任务钩子类型枚举类，定义不同的任务钩子类型

    Types:
        BEFORE_START: 任务开始前
        AFTER_START: 任务结束后
        BEFORE_STOP: 任务停止前
        AFTER_STOP: 任务停止后
        ON_SYNC_SUCCESS: 任务成功后
        ON_SYNC_ERROR: 任务失败后
        ON_CANCEL_ERROR: 任务取消失败后
        ON_TIMEOUT: 任务超时后
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

    Types:
        COROUTINE: 协程任务
        THREAD: 线程任务
    """

    COROUTINE = "coroutine"  # 协程任务
    THREAD = "THREAD"  # 线程任务


class ScheduleType(Enum):
    """
    调度类型枚举类，定义不同的调度类型

    Types:
        EVENT_DRIVEN: 根据事件循环调度
        PACKET_DRIVEN: 根据数据包到达触发调度
    """

    EVENT_DRIVEN = "event_driven"  # 事件驱动调度
    PACKET_DRIVEN = "packet_driven"  # 数据包驱动调度
