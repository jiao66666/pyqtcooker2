import threading
import time


class TrackManager:
    def __init__(self):
        # 当前轨道是否被占用
        self.lock = threading.Lock()

        # 是否被占用
        self.occupied = False

        # 当前占用者
        # {
        #     "pot_id": 1,
        #     "time": xxx
        # }
        self.owner = None


    def try_acquire(self, pot_id, action=""):
        """
        尝试占用轨道

        返回:
            True  : 获取成功
            False : 获取失败

        规则:
            1. 空闲 -> 任意pot可以占用
            2. 已被自己pot占用 -> 允许继续使用
            3. 被其他pot占用 -> 拒绝
        """

        print(f"POT{pot_id} 尝试占用轨道")

        with self.lock:

            # 已经有人占用
            if self.occupied:

                # 自己已经拥有轨道
                if self.owner and self.owner["pot_id"] == pot_id:
                    print(
                        f"POT{pot_id} 已经拥有轨道，继续使用"
                    )
                    return True


                # 其他锅占用
                print(
                    f"POT{pot_id}占用失败，"
                    f"当前占用者 POT{self.owner['pot_id']}"
                )

                return False


            # 空闲，第一次占用
            self.occupied = True

            self.owner = {
                "pot_id": pot_id,
                "start_action": action,
                "time": time.time()
            }

            print(
                f"POT{pot_id}占用成功"
            )

            return True



    def release(self, pot_id):
        """
        释放轨道

        注意:
        不再关心 action

        因为释放的是:
            pot 对轨道资源的所有权

        而不是某一个动作
        """

        with self.lock:

            # 当前没有占用
            if not self.occupied:
                return False


            # 防止其他锅误释放
            if not self.owner:
                return False


            if self.owner["pot_id"] != pot_id:

                print(
                    f"POT{pot_id}尝试释放失败,"
                    f"当前拥有者 POT{self.owner['pot_id']}"
                )

                return False


            print(
                f"POT{pot_id}释放轨道"
            )


            self.occupied = False
            self.owner = None

            return True



    def status(self):
        """
        查询当前轨道状态
        """

        with self.lock:

            return {
                "occupied": self.occupied,
                "owner": self.owner
            }