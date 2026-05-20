import threading
from lib.newstructure.system import get_system
class CookerService:
    def __init__(self,system):
        self.system = system

    # 运行锅电机动作组
    def run_action(self, action_name, pot_id):
        steps = self.system["stepbuilder"].build(action_name, pot_id)
        self.system["pots"][pot_id].submit_task(action_name,steps)
        return True


_service = None
_service_lock = threading.Lock()

def get_cookservice():
    global _service

    if _service is None:
        with _service_lock:
            if _service is None:
                _service = CookerService(get_system())

    return _service

cookservice = get_cookservice()
