import threading
from lib.newstructure.runtime import runtime
#任务型 还是 指令型 全部通过此命令器分发，防冲突
class CommandDispatcher:

    def __init__(self, resource_manager,bus):
        self.rm = resource_manager

        # 防止重复提交（可选增强）
        self.active_tasks = set()

        self.lock = threading.Lock()

        self.bus = bus

        self.bus.subscribe("MOTOR_DONE", self.on_motor_done)


    def submit(self, task_id, resources, run_fn):
        """
        统一执行入口
        """

        with self.lock:

            # 1. 防重复任务（同 task_id）
            if task_id in self.active_tasks:
                print(f"[Dispatcher] duplicate task rejected: {task_id}")
                return False

            # 2. 申请资源（核心）
            ok = self.rm.acquire_task_resources(task_id, resources)

            if not ok:
                print(f"[Dispatcher] resource busy: {task_id}")
                return False

            # 3. 标记任务开始
            self.active_tasks.add(task_id)

        # ===== 执行区（不在锁内） =====
        try:
            run_fn()
            return True

        except Exception as e:
            print(f"[Dispatcher] error: {task_id} -> {e}")

            # 异常释放
            self._cleanup(task_id)
            raise

    def complete(self, task_id):
        """
        正常完成调用
        """
        self._cleanup(task_id)

    def _cleanup(self, task_id):

        with self.lock:

            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)

            self.rm.release_task_resources(task_id)


    def on_motor_done(self, data):
        print("电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@---disptcher")
        motor_id = data["motor_id"]    
        ctx = runtime.get(motor_id)
        if not ctx:
            print("no runtime context")
            return      
        task_id = ctx["task_id"]
        print(f"release resource>>>>>>>>>>>>>>>>>>>>,taskid:{task_id}")
        
        self._cleanup(task_id)            