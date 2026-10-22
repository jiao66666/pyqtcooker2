from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime

class IceBuilder:

    def __init__(self, motors):
        self.motors = motors

    def build(self, action):
        # 电机映射
        motor_map = self._get_motor_map()

        if action not in ACTION_PARAMS_KEYLIST:
            return []

        return self._build_steps(ACTION_PARAMS_KEYLIST[action], motor_map)

    def _get_motor_map(self):   #依据需要对电机进行扩展
        return {
            "v": self.motors["stepmotor"][POT1_FLIP_MOTOR],
            "h": self.motors["stepmotor"][POT1_MOVE_MOTOR],
            "s": self.motors["spinmotor"][POT1_SPIN_MOTOR]
        }


    def _build_steps(self, template, motor_map):
        steps = []

        for item in template:
            # 统一要求：电机标识、动作名称、动作类型
            if len(item) < 3:
                raise ValueError(
                    f"动作配置缺少 dotype，配置内容：{item}"
                )

            motor_key = item[0]
            action_name = item[1]
            dotype =  item[2]

            action_key = f"{action_name}"

            default_params = ACTION_PARAMS_CONFIG[action_key]


            final_params = runtime.get_final_action_params(   #动态修改固定动作，合并处
                action_key,
                default_params
            )

            step = {
                "type" : self._get_motor_type(motor_key),
                "motor": motor_map[motor_key],
                "dotype":dotype,
                "action": action_key,
                "params": final_params
            }

            steps.append(step)

        return steps

    #标记电机类型以方便状态机进行相应动作选择
    def _get_motor_type(self,motor_key):
          if motor_key == "v" or motor_key == "h":
              return "step_pot"
          elif motor_key == "s":
              return "spin_pot"
          elif motor_key == "f":
              return "feeder_pot"
          else:
              return "unknown"