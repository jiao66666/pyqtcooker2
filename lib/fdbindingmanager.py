from lib.fdmotordriver import FeederMotorDriver
class FeederBindingManager:
    def __init__(self):
        # material -> motor
        self.material_to_motor = {}

        # motor_id -> material
        self.motor_to_material = {}

    def bind(self, material: str, motor: FeederMotorDriver):
        """绑定材料到电机"""
        self.material_to_motor[material] = motor
        self.motor_to_material[motor.motor_id] = material

    def unbind(self, material: str):
        """解绑"""
        motor = self.material_to_motor.pop(material, None)
        if motor:
            self.motor_to_material.pop(motor.motor_id, None)

    def get_motor(self, material: str) -> FeederMotorDriver:
        """通过材料获取电机"""
        return self.material_to_motor.get(material)

    def get_material(self, motor_id: int) -> str:
        """通过电机ID获取材料"""
        return self.motor_to_material.get(motor_id)

    def run_material(self, material: str, overtime: int):
        """直接按材料执行"""
        motor = self.get_motor(material)
        if not motor:
            print(f"未绑定材料: {material}")
            return False
        return motor.run(overtime)