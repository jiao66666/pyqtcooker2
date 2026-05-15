from lib.newstructure.constant import *

class StepBuilder:

    def __init__(self, motors):
        self.motors = motors

    def build(self, action, pot_id):
        # 电机映射
        motor_map = self._get_motor_map(pot_id)

        if action not in ACTION_PARAMS_KEYLIST:
            return []

        return self._build_steps(ACTION_PARAMS_KEYLIST[action], pot_id, motor_map)

    def _get_motor_map(self, pot_id):
        if pot_id == 1:
            return {
                "v": self.motors[POT1_FLIP_MOTOR],
                "h": self.motors[POT1_MOVE_MOTOR],
            }
        elif pot_id == 2:
            return {
                "v": self.motors[POT2_FLIP_MOTOR],
                "h": self.motors[POT2_MOVE_MOTOR],
            }
        else:
            raise ValueError(f"Invalid pot_id: {pot_id}")

    def _build_steps(self, template, pot_id, motor_map):
        print("构建动作中。》》》》》》")
        steps = []

        for item in template:
            motor_key = item[0]
            action_name = item[1]
            sub_template = item[2] if len(item) > 2 else None

            action_key = f"{action_name}_{pot_id}"

            step = {
                "motor": motor_map[motor_key],
                "action": action_key,
                "params": ACTION_PARAMS_CONFIG[action_key]
            }

            # 递归处理 on_block
            if sub_template:
                step["on_block"] = self._build_steps(sub_template, pot_id, motor_map)

            steps.append(step)

        return steps