from typing import Union, TYPE_CHECKING
from asyncio import Queue

from .TaskTypes import TaskStage,TaskHookType

if TYPE_CHECKING:
    from .TaskItem import TaskItem

class TaskRegister:
    def __init__(self):
        self.stage_chains: dict[TaskStage, list[TaskItem]] = {}
        self.hook_chains: dict[str, list[TaskItem]] = {}
        self.sorted_flags: dict[Union[TaskStage, str], bool] = {}

        self.chain_tx: dict[Union[TaskStage, str], Queue] = {}
        self.chain_rx: dict[Union[TaskStage, str], Queue] = {}
        self.chain_cache: dict[Union[TaskStage, str], Queue] = {}

    def get_stage_chains(self, stage: TaskStage, default: list) -> list["TaskItem"] | list:
        return self.stage_chains.get(stage, default)

    def get_hook_chains(self, name: str, default: list) -> list["TaskItem"] | list:
        return self.hook_chains.get(name, default)
    
    def init_msg_queue(self, stage: Union[TaskStage, str]):
        """初始化消息队列"""
        self.chain_tx[stage] = Queue()
        self.chain_rx[stage] = Queue()
        self.chain_cache[stage] = Queue()

    def register_stage_task(self, stage: TaskStage, task_item: "TaskItem"):
        if stage not in self.stage_chains:
            # 如果stage在stage链集中不存在，则以stage为键创建一个空链
            self.stage_chains[stage] = []

        # 将task_item添加到 f"{stage}" 链中
        self.stage_chains[stage].append(task_item)
        self.init_msg_queue(stage)
        

        # 设置sorted_flags，表示 f"{stage}" 链对应项未排序
        self.sorted_flags[stage] = False

    def register_hook_task(self, hook_key: TaskHookType, task_item: "TaskItem"):
        if hook_key not in self.hook_chains:
            # 如果hook_key在hook链集中不存在，则以hook_key为键创建一个空链
            self.hook_chains[hook_key] = []
            
        # 将task_item添加到 f"{hook_key}" 链中
        self.hook_chains[hook_key].append(task_item)
        self.init_msg_queue(hook_key)

        # 设置sorted_flags，表示 f"{hook_key}" 链对应项未排序
        self.sorted_flags[hook_key] = False

    def sort_chain(self, chain_key: Union[TaskStage, str]):
        # 根据sorted_flags判断是否存在需要排序的链
        if not self.sorted_flags.get(chain_key, True):
            # 获取链
            chain = self.stage_chains.get(chain_key) or self.hook_chains.get(chain_key)

            if chain:
                # 排序
                chain.sort(key=lambda x: x.priority)

                # 更新排序记录
                self.sorted_flags[chain_key] = True


task_register = TaskRegister()
