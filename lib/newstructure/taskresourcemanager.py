import threading
class TaskResourceManager:
    """
    任务级资源所有权管理器

    作用：
    1. 防止多个任务同时占用同一资源
    2. 防止单动作插入到动作组中
    3. 资源生命周期 = task 生命周期
    """

    def __init__(self):
        # resource_id -> task_id
        self.resource_owner = {}

        # task_id -> set(resource_id)
        self.task_resources = {}

        self.lock = threading.Lock()

    # =====================================
    # 申请资源
    # =====================================
    def acquire_task_resources(self, task_id, resource_ids):

        with self.lock:

            # 检查资源是否已被占用
            for resource_id in resource_ids:

                owner = self.resource_owner.get(resource_id)

                if owner is not None and owner != task_id:
                    print(
                        f"[ResourceManager] "
                        f"resource busy: {resource_id}, owner={owner},cur_task_id is {task_id}"
                    )
                    return False

            # 正式占有资源
            for resource_id in resource_ids:
                self.resource_owner[resource_id] = task_id

            self.task_resources[task_id] = set(resource_ids)

            print(
                f"[ResourceManager] "
                f"task={task_id} acquired resources={resource_ids}"
            )

            return True

    # =====================================
    # 释放任务资源
    # =====================================
    def release_task_resources(self, task_id):

        with self.lock:

            resources = self.task_resources.get(task_id)

            if not resources:
                return

            for resource_id in resources:

                owner = self.resource_owner.get(resource_id)

                # 防止误释放
                if owner == task_id:
                    del self.resource_owner[resource_id]

            del self.task_resources[task_id]

            print(
                f"[ResourceManager] "
                f"task={task_id} released"
            )

    # =====================================
    # 查询资源是否被占用
    # =====================================
    def is_resource_busy(self, resource_id):

        with self.lock:
            return resource_id in self.resource_owner

    # =====================================
    # 查询资源所有者
    # =====================================
    def get_resource_owner(self, resource_id):

        with self.lock:
            return self.resource_owner.get(resource_id)

    # =====================================
    # 查询 task 是否存在
    # =====================================
    def has_task(self, task_id):

        with self.lock:
            return task_id in self.task_resources