from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime

class StepBuilder:

    def __init__(self, motors):
        self.motors = motors

    def build(self, action, pot_id):
        # 电机映射
        motor_map = self._get_motor_map(pot_id)

        if action not in ACTION_PARAMS_KEYLIST:
            return []

        return self._build_steps(ACTION_PARAMS_KEYLIST[action], pot_id, motor_map)

    def _get_motor_map(self, pot_id):   #依据需要对电机进行扩展，后续还有feedermotor,icemotors，可依据功能来命名，确保唯一即可
        if pot_id == 1:
            return {
                "v": self.motors["stepmotor"][POT1_FLIP_MOTOR],
                "h": self.motors["stepmotor"][POT1_MOVE_MOTOR],
                "s": self.motors["spinmotor"][POT1_SPIN_MOTOR]
            }
        elif pot_id == 2:
            return {
                "v": self.motors["stepmotor"][POT2_FLIP_MOTOR],
                "h": self.motors["stepmotor"][POT2_MOVE_MOTOR],
                "s": self.motors["spinmotor"][POT2_SPIN_MOTOR]
            }
        else:
            raise ValueError(f"Invalid pot_id: {pot_id}")

    def _build_steps(self, template, pot_id, motor_map):
        steps = []

        for item in template:
            # 统一要求：电机标识、动作名称、动作类型
            if len(item) < 3:
                raise ValueError(
                    f"动作配置缺少 doing_type，配置内容：{item}"
                )

            motor_key = item[0]
            action_name = item[1]
            dotype =  item[2]
            sub_template = item[3] if len(item) > 3 else None

            action_key = f"{action_name}"

            default_params = ACTION_PARAMS_CONFIG[action_key]

            # 获取当前锅的专属参数
            pot_params = default_params.get("pot_params", {}).get(pot_id, {})

            # 合并参数：锅专属参数覆盖公共参数
            default_params = {
                **{k: v for k, v in default_params.items() if k != "pot_params"},
                **pot_params
            }

            final_params = runtime.get_final_action_params(   #动态修改固定动作，合并处
                action_key,
                default_params,
                motor_key
            )

            step = {
                "type" : self._get_motor_type(motor_key),
                "motor": motor_map[motor_key],
                "dotype":dotype,
                "action": action_key,
                "params": final_params
            }

            # 递归处理 on_block
            if sub_template:
                step["on_block"] = self._build_steps(sub_template, pot_id, motor_map)

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