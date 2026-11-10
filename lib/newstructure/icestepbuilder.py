from lib.newstructure.constant import *
from lib.newstructure.runtime import runtime


class IceStepBuilder:

    def __init__(self, motors):
        self.motors = motors

    def build(self, action):
        motor_map = self._get_motor_map()

        if action not in ACTION_PARAMS_KEYLIST:
            return []

        return self._build_steps(
            ACTION_PARAMS_KEYLIST[action],
            motor_map
        )

    def build_bystep(self, action, index):
        motor_map = self._get_motor_map()

        if action not in ACTION_PARAMS_KEYLIST:
            return []

        return self._build_steps(
            [ACTION_PARAMS_KEYLIST[action][index]],
            motor_map
        )

    def _get_motor_map(self):
        return {
            "x": self.motors["icemotor"][ICE_MOTOR_X],
            "y": self.motors["icemotor"][ICE_MOTOR_Y],
            "z": self.motors["icemotor"][ICE_MOTOR_Z],
            "d": self.motors["icemotor"][ICE_MOTOR_DOOR],
            "s": self.motors["icemotor"][ICE_MOTOR_SPIN],
            "ml": self.motors["feedermotor"][POT1_FLAVORMOTOR7],
            "mr": self.motors["feedermotor"][POT1_FLAVORMOTOR8],
            "sk": self.motors["feedermotor"][POT2_FLAVORMOTOR9]
        }

    def _build_steps(self, template, motor_map):
        steps = []

        for item in template:

            # 并行动作组
            if item[0] == "parallel":

                if len(item) not in (2, 3):
                    raise ValueError(
                        f"并行动作组配置错误：{item}"
                    )

                parallel_actions = self._build_steps(
                    item[1],
                    motor_map
                )

                start_config = None

                if len(item) == 3 and item[2]:

                    config = item[2]

                    start_config = {
                        "start_mode": config["start_mode"],
                        "triggers": [
                            (
                                self._get_motor_id(trigger_motor),
                                trigger_position,
                                self._get_motor_id(target_motor),
                                trigger_direction
                            )
                            for trigger_motor, trigger_position, target_motor,trigger_direction
                            in config.get("triggers", [])
                        ]
                    }

                steps.append({
                    "type": "parallel_ice",
                    "actions": parallel_actions,
                    "start_config": start_config
                })

            else:

                steps.append(
                    self._build_single_step(item, motor_map)
                )

        return steps

    def _build_single_step(self, item, motor_map):

        if len(item) < 3:
            raise ValueError(
                f"动作配置缺少 dotype，配置内容：{item}"
            )

        motor_key = item[0]
        action_name = item[1]
        dotype = item[2]

        action_key = f"{action_name}"

        default_params = ACTION_PARAMS_CONFIG[action_key]

        final_params = runtime.get_final_action_params(
            action_key,
            default_params,
            motor_key
        )

        return {
            "type": self._get_motor_type(motor_key),
            "motor": motor_map[motor_key],
            "dotype": dotype,
            "action": action_key,
            "params": final_params
        }

    def _get_motor_type(self, motor_key):

        if motor_key in ("ml", "mr", "sk"):
            return "dc_ice"

        return "step_ice"


    def _get_motor_id(self, motor_key):
        """
        根据电机名称获取实际 motor_id。
        """
        for motor_id, name in ICE_MOTORID_NAME_MAP.items():
            if name == motor_key:
                return motor_id

        raise ValueError(f"未知的冰柜电机标识: {motor_key}")
    