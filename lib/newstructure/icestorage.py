from threading import RLock
from lib.newstructure.constant import ICE_STORAGE_MAP


class IceStorage:

    EMPTY = 0
    FULL = 1

    def __init__(self):
        self._lock = RLock()

        # 初始化24个位置的运行状态
        self.positions = {
            position_id: {
                "status": self.EMPTY
            }
            for position_id in ICE_STORAGE_MAP
        }

    def get_position(self, position_id):
        """获取位置坐标和状态"""
        if position_id not in ICE_STORAGE_MAP:
            return None

        with self._lock:
            return {
                **ICE_STORAGE_MAP[position_id],
                **self.positions[position_id]
            }

    def get_status(self, position_id):
        """获取位置状态"""
        with self._lock:
            position = self.positions.get(position_id)
            return position["status"] if position else None

    def set_status(self, position_id, status):
        """设置位置状态"""
        if position_id not in self.positions:
            return False

        with self._lock:
            self.positions[position_id]["status"] = status

        return True

    def get_empty_positions(self):
        """获取所有空位置"""
        with self._lock:
            return [
                position_id
                for position_id, position in self.positions.items()
                if position["status"] == self.EMPTY
            ]

    def get_full_positions(self):
        """获取所有满位"""
        with self._lock:
            return [
                position_id
                for position_id, position in self.positions.items()
                if position["status"] == self.FULL
            ]
        
    #返回给前端更新状态
    def get_all_status(self):
        """获取全部24个储位状态，按照储位编号1-24排列"""
        with self._lock:
            return [
                self.positions[position_id]["status"] == self.FULL
                for position_id in sorted(self.positions)
            ]        