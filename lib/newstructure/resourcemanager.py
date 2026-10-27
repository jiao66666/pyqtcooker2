
import threading


class ResourceManager:
    """
    统一管理任务和独立动作的业务资源占用。
    线程安全锁仍然保留在本类中。
    """

    def __init__(self, bus):
        # resource_id -> owner_id
        self.resource_owner = {}

        # owner_id -> set(resource_id)
        self.owner_resources = {}

        # owner_id -> "task" / "action"
        self.owner_types = {}

        self.bus = bus
        self.lock = threading.Lock()

        # 整个任务完成
        self.bus.subscribe(
            "TASK_DONE", self.on_task_done
        )

        # 独立电机动作完成
        self.bus.subscribe(
            "ACTION_DONE", self.on_action_done
        )

        # 电机单步完成仍然由状态机处理
        # 不在这里直接释放整个任务的资源

    def acquire_resources(
        self, owner_id, owner_type, resource_ids
    ):
        resource_ids = set(resource_ids)

        with self.lock:
            # 先检查所有资源，避免部分申请成功
            for resource_id in resource_ids:
                owner = self.resource_owner.get(resource_id)

                if owner is not None and owner != owner_id:
                    print(
                        f"[ResourceManager] resource busy: "
                        f"{resource_id}, owner={owner}"
                    )
                    return False

            # 检查通过后统一登记
            for resource_id in resource_ids:
                self.resource_owner[resource_id] = owner_id

            self.owner_resources.setdefault(
                owner_id, set()
            ).update(resource_ids)

            self.owner_types[owner_id] = owner_type

            print(
                f"[ResourceManager] {owner_type}={owner_id} "
                f"acquired {resource_ids}"
            )
            return True

    def release_resources(self, owner_id):
        with self.lock:
            resources = self.owner_resources.get(owner_id)

            if resources is None:
                print("error>>>>resource is NONE")
                return False

            for resource_id in resources:
                if self.resource_owner.get(resource_id) == owner_id:
                    del self.resource_owner[resource_id]

            del self.owner_resources[owner_id]
            self.owner_types.pop(owner_id, None)

            print(
                f"[ResourceManager] owner={owner_id} released"
            )
            return True

    def on_task_done(self, data):
        print("处理电机解锁(任务)<<<<<<<<<<<<<<<")
        task_id = data.get("task_id")
        if not task_id:
            print("error>>>>没有任务ID")
            return

        if self.owner_types.get(task_id) != "task":
            print(f"[ResourceManager] unknown task: {task_id}")
            return

        self.release_resources(task_id)

    def on_action_done(self, data):
        print("处理电机解锁（动作）《《《《《《《《《《《《《")
        action_id = data.get("task_id")
        if not action_id:
            print("error>>>>没有任务ID")
            return

        if self.owner_types.get(action_id) != "action":
            print(f"[ResourceManager] unknown action: {action_id}")
            return

        self.release_resources(action_id)
