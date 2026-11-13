import queue
from lib.newstructure.runtime import runtime
import time
from lib.newstructure.constant import *
from lib.newstructure.tools import get_motor_position,get_motor_homestatus
#冰柜状态机模型
class IceStateMachine:
    def __init__(self, bus, resource_manager):
        self.state = "IDLE"

        self.bus = bus
        self.current_step = 0
        self.steps = None
        self.command_queue = queue.Queue()
        self.wait_start_time = 0
        self.running_tasks = set()
        self.running_task_id = None
        self.total_repeat = 0
        self.current_repeat = 0
        self.error_info = None

        self.running_task_type = None
        self.resource_manager = resource_manager

        self.delay_start_time = None
        self.delay_duration = None


        # 当前动作执行类型
        self.current_action_type = "single"
        # 并行动作组中尚未完成的电机
        # {(board_id, motor_id): step}
        self.parallel_pending = {}
        # 当前并行动作组
        self.parallel_actions = []       

        # 尚未达到触发位置、等待启动的电机
        self.parallel_waiting_start = {}


        # 等待位置触发的开始时间
        self.parallel_wait_start_time = None

        # 每个已启动电机的独立启动时间
        self.parallel_motor_start_times = {}

        # 并行超时时间（秒）
        self.parallel_trigger_timeout = TIMEOUT
        self.parallel_motor_timeout = TIMEOUT


        # 各触发轴的运动方向
        self.parallel_trigger_directions = {}        


        
        # 订阅电机完成事件
        self.bus.subscribe("ICE_MOTOR_DONE", self.on_icemotor_done)
        self.bus.subscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.subscribe("MOTOR_ERROR", self.on_motor_error)


    def submit_task(self, running_task_id, steps, repeat=1,task_type="normal_task"):

        if not isinstance(repeat, int) or isinstance(repeat, bool) or repeat < 1:
            return False

        if not steps:
            print(f"任务 {running_task_id} 的动作组为空，拒绝提交")
            return False

        # 统一任务 ID 类型，避免 1 和 "1" 被当成两个任务
        running_task_id = str(running_task_id)

        # 故障或急停状态不允许提交
        if self.state in ("STOPPED", "ERROR"):
            print(f"状态为 {self.state}，拒绝提交任务")
            return False

        # 检查任务是否已经提交或正在执行
        if running_task_id in self.running_tasks:
            print(f"任务 {running_task_id} 已经提交或正在执行")
            return False

        # 记录任务 ID（包含排队任务）
        self.running_tasks.add(running_task_id)

        # 将任务 ID、动作步骤、重复次数绑定在一起
        task = {
            "task_id": running_task_id,
            "steps": steps,
            "repeat": repeat,
            "task_type": task_type
        }

        self.command_queue.put(task)

        print(
            f"任务提交成功：{running_task_id}，"
            f"重复次数：{repeat}，"
            f"当前待执行任务数量：{self.command_queue.qsize()}"
        )

        return True

    def clear_running_task(self):
        self.running_tasks = set()
        self.running_task_id = None
        self.running_task_type = None
        self.total_repeat = 0
        self.current_repeat = 0

        self.parallel_pending.clear()
        self.parallel_actions = []
        self.current_action_type = "single"

        self.parallel_waiting_start.clear()
        self.parallel_trigger_directions.clear()
        self.parallel_wait_start_time = None
        self.parallel_motor_start_times.clear()

    def tick(self):
        if self.state in ["STOPPED"]:
            print(f"ice state machine state is STOPPED")
            return

        elif self.state == "IDLE":

            if not self.command_queue.empty():

                # 取出完整任务包
                task = self.command_queue.get()

                # 只有真正开始执行时，才设置当前任务 ID
                self.running_task_id = task["task_id"]
                self.running_task_type = task["task_type"]
                self.steps = task["steps"]
                self.total_repeat = task["repeat"]
                self.current_repeat = 0

                print(
                    f"========== 开始执行任务：{self.running_task_id} =========="
                )

                self.reset_step()
                self.state = "CHECK_HOME"

            return

        elif self.state == "CHECK_HOME":
            print(f"ice machine status is CHECK_HOME")
            # 整体回零和分步任务属于白名单，不需要检查当前零位
            if self.running_task_type in (STEP_TASK_TYPE, RESET_TASK_TYPE):
                self.state = "RUNNING"
                return

            if self.check_home():
                self.state = "RUNNING"
            return

        elif self.state == "RUNNING":
            print(f"ice machine state is RUNNING,current step is:{self.steps[self.current_step]}")
            step = self.steps[self.current_step]

            if step["type"] == "parallel_ice":
                self.start_parallel_actions(step["actions"],step.get("start_config"))
            elif step["type"] == "step_ice":
                print(f"<<<<<<<<<<<current action is {step['action']}>>>>>>>>>>>>")
                print(f"icemotor运行参数如下:{step['params']}")


                if step["dotype"] not in ("go", "reset","go_delay"):
                    self.state = "ERROR"
                    self.error_info = f"未知的动作类型：{step['dotype']}"
                    return

                # 2. 校验必要参数
                if not step.get("motor") or not step.get("action"):
                    self.state = "ERROR"
                    self.error_info = f"动作参数不完整：{step}"
                    return


                # 步进电机等待完成反馈
                self.state = "WAITING"
                self.wait_start_time = time.time()


                self.current_action_type = "single"
                runtime.set_running(
                    board_id=BOARDTYPE_ICE,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    params=step["params"],
                    task_id=f"{self.running_task_id}"
                )
                if step["dotype"] == "reset":
                    print("exectuing<<<<<[reset]>>>>>>do type")
                    step["motor"].reset_zero_byspeed(step["params"]["speed"])  
                elif step["dotype"] == "go":
                    print("exectuing<<<<<[go]>>>>>>do type")
                    step["motor"].go(step["params"]["target"],step["params"]["speed"]) 
                elif step["dotype"] == "go_delay":
                    print("exectuing<<<<<[go_delay]>>>>>>do type")
                    step["motor"].go(step["params"]["target"],step["params"]["speed"])   
                else:
                    self.state = "ERROR"
                    print(
                        f"未知动作类型 {step['dotype']}，"
                        f"动作名称：{step['action']}"
                    )
                    return 



            elif step["type"] == "dc_ice":

                if step["dotype"] not in ("on", "off"):
                    self.state = "ERROR"
                    self.error_info = f"未知的动作类型：{step['dotype']}"
                    return

                # 2. 校验必要参数
                if not step.get("motor") or not step.get("action"):
                    self.state = "ERROR"
                    self.error_info = f"动作参数不完整：{step}"
                    return

                self.current_action_type = "single"
                runtime.set_running(
                    board_id=BOARDTYPE_FEEDER,
                    motor_id=step["motor"].motor_id,
                    action=step["action"],
                    params=step["params"],
                    task_id=f"{self.running_task_id}"
                )
                if step["dotype"] == "on":
                    step["motor"].output_on()
                    time.sleep(step["params"]["delay"])  #阻塞一定时间以确保吸住
                elif step["dotype"] == "off":
                    step["motor"].output_off()    
                    time.sleep(step["params"]["delay"])  #阻塞一定时间以确保吸住
                else:
                    self.state = "ERROR"
                    print(
                        f"未知动作类型 {step['dotype']}，"
                        f"动作名称：{step['action']}"
                    )
                    return 

                # 当前磁吸动作完成，更新 RuntimeContext
                runtime.set_done(
                    motor_id=step["motor"].motor_id,
                    board_id=BOARDTYPE_FEEDER
                )

                # 当前磁吸动作完成，推进下一步
                self.go_next_step("on_icedc_done")
                if self.current_step >= len(self.steps):
                    self.state = "DONE"
                else:
                    self.state = "RUNNING"
   
        elif self.state == "WAITING":

            if self.current_action_type == "parallel":

                # 检查位置触发
                self.check_parallel_triggers()

                if self.state != "WAITING":
                    return

                # 检查并行超时
                self.check_parallel_timeout()

            else:

                # 普通单轴动作仍使用原来的超时机制
                if time.time() - self.wait_start_time > TIMEOUT:

                    print("motor time out !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                    step = self.steps[self.current_step]

                    self.error_info = {
                        "step": self.current_step,
                        "action": step["action"],
                        "reason": "timeout"
                    }

                    self.state = "ERROR"

        elif self.state == "DONE":
            print("ice machine state is DONE")
            self.current_repeat += 1

            if self.current_repeat < self.total_repeat:
                # 还有剩余次数，重新执行当前动作组
                print(f"当前次数为{self.current_repeat}，小于执行总数{self.total_repeat},将执行下一次")
                print(
                    f"准备执行第 {self.current_repeat + 1} 次，"
                    f"总次数 {self.total_repeat}"
                )

                self.reset_step()
                self.state = "CHECK_HOME"

            else:
                # 所有次数执行完毕，通知 ResourceManager 释放任务资源
                print(f"当前次数为{self.current_repeat}，大于等于执行总数{self.total_repeat},执行结束")
                self.bus.publish("TASK_DONE", {
                    "task_id": self.running_task_id,
                    "owner_id": self.running_task_id,
                    "owner_type": "task",
                })

                # 清理任务
                self.running_tasks.discard(self.running_task_id)
                self.running_task_id = None
                self.running_task_type = None
                self.steps = None
                self.state = "IDLE"

                # 重置重复执行计数
                self.total_repeat = 0
                self.current_repeat = 0

        elif self.state == "ERROR":
            print(f"ice machine state is ERROR")  


        elif self.state == "RECOVERING":
            print("ice machine state enter in recovering")   
            # 1. 释放当前任务占用的资源
            if self.running_task_id:
                self.resource_manager.release_resources(
                    self.running_task_id
                )

            # 2. 重置状态机
            self.reset()  


        elif self.state == "DELAY":

            elapsed = time.time() - self.delay_start_time

            if elapsed >= self.delay_duration:

                print(
                    f"步进电机延时结束，实际等待 {elapsed:.2f} 秒"
                )

                self.delay_start_time = None
                self.delay_duration = None

                self.go_next_step("on_delay_timeisup")

                if self.current_step < len(self.steps):
                    self.state = "RUNNING"
                else:
                    self.state = "DONE"            


    def start_parallel_actions(self, actions, start_config=None):
        """
        启动并行动作组。

        默认：
            所有电机立即启动。

        位置触发：
            没有触发条件的电机立即启动，
            其他电机等待触发轴到达指定位置。
        """

        print("========== 开始执行并行动作组 ==========")

        self.current_action_type = "parallel"
        self.parallel_actions = actions

        # 清理上一组状态
        self.parallel_pending = {}
        self.parallel_waiting_start = {}
        self.parallel_trigger_directions = {}

        self.parallel_wait_start_time = None
        self.parallel_motor_start_times.clear()

        # 检查动作组是否为空
        if not actions:
            print("并行动作组为空")
            self.state = "ERROR"
            return

        # 记录已经使用的电机，防止重复
        seen_resources = set()

        # 位置触发配置
        triggers = {}

        if start_config:
            for trigger in start_config.get("triggers", []):

                if len(trigger) != 4:
                    print(f"位置触发配置格式错误: {trigger}")
                    self.state = "ERROR"
                    return

                trigger_motor, trigger_position, target_motor,trigger_direction = trigger

                if trigger_direction not in (-1, 1):
                    print(f"触发方向错误: {trigger_direction}")
                    self.state = "ERROR"
                    return
                
                if target_motor in triggers:
                    print(f"目标电机存在重复触发配置: {target_motor}")
                    self.state = "ERROR"
                    return

                triggers[target_motor] = {
                    "trigger_motor": trigger_motor,
                    "trigger_position": trigger_position,
                    "trigger_direction": trigger_direction
                }

        # 第一步：检查所有动作是否合法
        for step in actions:

            if step["type"] != "step_ice":
                print(f"当前并行动作组暂不支持该电机类型: {step['type']}")
                self.state = "ERROR"
                return

            motor_id = step["motor"].motor_id
            resource_id = (BOARDTYPE_ICE, motor_id)

            if resource_id in seen_resources:
                print(f"并行动作组存在重复电机: {resource_id}")
                self.state = "ERROR"
                return

            seen_resources.add(resource_id)

            if step["dotype"] not in ("go", "reset"):
                print(f"未知并行动作类型: {step['dotype']}")
                self.state = "ERROR"
                return

            params = step.get("params") or {}

            if step["dotype"] == "go":
                if "target" not in params or "speed" not in params:
                    print(f"电机参数不完整: {resource_id}")
                    self.state = "ERROR"
                    return

            elif step["dotype"] == "reset":
                if "speed" not in params:
                    print(f"复位参数不完整: {resource_id}")
                    self.state = "ERROR"
                    return

        # 第二步：检查触发配置中的电机是否存在
        for target_motor, trigger_info in triggers.items():

            trigger_motor = trigger_info["trigger_motor"]

            if trigger_motor in triggers:
                print(
                    f"触发轴不能同时是等待启动的目标电机: "
                    f"{trigger_motor}"
                )
                self.state = "ERROR"
                return

            if target_motor not in [
                step["motor"].motor_id for step in actions
            ]:
                print(f"触发目标电机不存在: {target_motor}")
                self.state = "ERROR"
                return

            if trigger_motor not in [
                step["motor"].motor_id for step in actions
            ]:
                print(f"触发轴不在当前并行动作组中: {trigger_motor}")
                self.state = "ERROR"
                return

            # 触发轴必须是 go 动作，后续才能根据绝对目标推断运动方向
            trigger_step = next(
                step for step in actions
                if step["motor"].motor_id == trigger_motor
            )

            if trigger_step["dotype"] != "go":
                print(f"触发轴必须使用 go 动作: {trigger_motor}")
                self.state = "ERROR"
                return

        # 第三步：设置状态
        self.state = "WAITING"
        self.wait_start_time = None

        # 第四步：确定哪些电机立即启动，哪些等待触发
        waiting_steps = []
        immediate_steps = []

        for step in actions:

            motor = step["motor"]
            motor_id = motor.motor_id
            resource_id = (BOARDTYPE_ICE, motor_id)

            trigger_info = triggers.get(motor_id)

            if trigger_info is None:
                # 没有触发条件，稍后立即启动
                immediate_steps.append((resource_id, step))

            else:
                # 有触发条件，先放入等待列表
                trigger_motor_id = trigger_info["trigger_motor"]
                trigger_position = trigger_info["trigger_position"]
                trigger_direction = trigger_info["trigger_direction"]

                waiting_steps.append({
                    "resource_id": resource_id,
                    "step": step,
                    "trigger_motor_id": trigger_motor_id,
                    "trigger_position": trigger_position,
                    "direction": trigger_direction
                })

        # 第五步：先登记所有等待启动的电机
        for item in waiting_steps:

            resource_id = item["resource_id"]

            self.parallel_waiting_start[resource_id] = item

            print(
                f"电机 {resource_id} 等待位置触发："
                f"触发轴={item['trigger_motor_id']}, "
                f"触发位置={item['trigger_position']}"
            )

        # 第六步：启动没有触发条件的电机
        for resource_id, step in immediate_steps:

            result = self.start_one_parallel_motor(
                resource_id,
                step
            )

            # 启动失败或状态进入 ERROR，停止后续启动
            if result is False or self.state == "ERROR":
                print(f"并行电机启动失败: {resource_id}")
                return

        # 第七步：检查位置触发
        self.check_parallel_triggers()

        # 如果检查触发时发生错误，不再继续
        if self.state == "ERROR":
            return

        # 第八步：有等待触发的电机，才开始触发等待计时
        if self.parallel_waiting_start:
            self.parallel_wait_start_time = time.time()

        print("========== 并行动作组初始化完成 ==========")




    def start_one_parallel_motor(self, resource_id, step):
        """
        启动并行动作组中的单个电机。

        resource_id: (board_id, motor_id)
        step: 对应的 step_ice 动作
        """

        board_id, motor_id = resource_id

        # 防止重复启动
        if resource_id in self.parallel_pending:
            print(f"电机已经启动，忽略重复启动: {resource_id}")
            return False

        if step["type"] != "step_ice":
            print(f"不支持的并行电机类型: {step['type']}")
            self.state = "ERROR"
            return False

        if step["dotype"] not in ("go", "reset"):
            print(f"未知并行动作类型: {step['dotype']}")
            self.state = "ERROR"
            return False

        try:
            print(
                f"========== 启动并行电机 {resource_id} =========="
            )

            # 1. 先登记运行状态
            runtime.set_running(
                board_id=board_id,
                motor_id=motor_id,
                action=step["action"],
                params=step["params"],
                task_id=f"{self.running_task_id}"
            )



            # 2. 先加入等待完成集合
            self.parallel_pending[resource_id] = step

            # 3. 记录电机启动时间
            self.parallel_motor_start_times[resource_id] = time.time()
            # 3. 从待启动集合中移除
            self.parallel_waiting_start.pop(resource_id, None)
            # 2. 先加入等待完成集合


            # 4. 发送实际运动指令
            if step["dotype"] == "reset":

                step["motor"].reset_zero_byspeed(
                    step["params"]["speed"]
                )

            elif step["dotype"] == "go":

                step["motor"].go(
                    step["params"]["target"],
                    step["params"]["speed"]
                )

            print(
                f"并行电机启动成功: {resource_id}, "
                f"action={step['action']}"
            )

            return True

        except Exception as e:

            print(
                f"并行电机启动失败: {resource_id}, "
                f"action={step['action']}, error={e}"
            )

            self.error_info = {
                "reason": "parallel_motor_start_failed",
                "motor": resource_id,
                "action": step["action"],
                "detail": str(e)
            }

            self.parallel_pending.pop(resource_id, None)
            self.parallel_motor_start_times.pop(resource_id, None)
            self.state = "ERROR"

            return False



    def check_parallel_triggers(self):
        """
        检查并行动作组中尚未启动的电机，
        根据触发轴的绝对位置决定是否启动。
        """
        
        for resource_id, trigger_info in list(
            self.parallel_waiting_start.items()
        ):

            trigger_motor_id = trigger_info["trigger_motor_id"]
            trigger_position = trigger_info["trigger_position"]

            # 这里需要从 RuntimeContext 或轮询数据中读取
            # 触发轴当前的实时绝对位置

            current_position = get_motor_position(
                BOARDTYPE_ICE,
                trigger_motor_id
            )

            if current_position is None:
                continue

            direction = trigger_info["direction"]

            if direction == 1:
                triggered = current_position >= trigger_position

            elif direction == -1:
                triggered = current_position <= trigger_position

            else:
                print(f"触发方向无效: {direction}")
                self.state = "ERROR"
                return

            if triggered:
                step = trigger_info["step"]

                print(
                    f"位置触发成功：电机 {trigger_motor_id} "
                    f"当前位置 {current_position}，"
                    f"触发位置 {trigger_position}"
                )

                result = self.start_one_parallel_motor(resource_id, step)

                if result is False or self.state == "ERROR":
                  return


    def reset(self):

        self.state = "IDLE"

        # 清理任务队列
        while not self.command_queue.empty():
            self.command_queue.get()

        # 清理任务信息
        self.running_tasks.clear()
        self.running_task_id = None
        self.running_task_type = None

        self.steps = None
        self.total_repeat = 0
        self.current_repeat = 0

        self.reset_step()

        # 清理普通动作计时
        self.wait_start_time = 0


        # 清理错误信息
        self.error_info = None

        self.delay_start_time = None
        self.delay_duration = None


    def check_home(self):
        """
        检查冰柜四个电机是否全部回到零位。
        只有全部满足零位要求，才返回 True。
        """
        tolerance = 0.01
        check_motor_list = [ICE_MOTOR_X,ICE_MOTOR_Y,ICE_MOTOR_Z,ICE_MOTOR_SPIN]
        for motor_id in check_motor_list:

            current_position = get_motor_position(
                BOARDTYPE_ICE,
                motor_id
            )

            # 没有获取到有效位置
            if current_position is None:
                print(f"电机 {motor_id} 位置未知，无法确认零位")
                self.enter_recovering(
                    motor_id,
                    "POSITION_UNKNOWN",
                    f"异常：电机 {ICE_MOTORID_NAME_MAP[motor_id]} 位置未知，无法确认零位"
                )
                return False
            # 判断是否执行过归零操作
            current_homed = get_motor_homestatus(
                BOARDTYPE_ICE,
                motor_id
            )
            if motor_id != ICE_MOTOR_SPIN and not current_homed:
                self.enter_recovering(
                    motor_id,
                    "MOTOR_NOT_HOMED",
                    f"异常：电机 {ICE_MOTORID_NAME_MAP[motor_id]} 尚未完成归零操作"
                )

                print(f"电机 {motor_id} 尚未完成归零操作")
                return False
            # 判断是否在零位误差范围内
            if abs(float(current_position)) > tolerance:
                print(
                    f"电机 {motor_id} 未回到零位，"
                    f"当前位置：{current_position}"
                )
                self.enter_recovering(
                    motor_id,
                    "MOTOR_NOT_ZERO",
                    f"异常：电机 {ICE_MOTORID_NAME_MAP[motor_id]} 未回到零位，当前位置：{current_position}"
                )
                return False

        print("冰柜四个电机全部处于零位")
        return True       


    def enter_recovering(self, motor_id, reason, message):
        self.state = "RECOVERING"
        print(message)

        #通知前端
        self.bus.publish(
            "ICE_RECOVERY_REQUIRED",
            {
                "motor_id": motor_id,
                "reason": reason,
                "message": message
            }
        )


    def go_next_step(self,actor="unknown"):
        print(f"*************actor:{actor} push the state to the next action*****************")
        self.current_step += 1

    def reset_step(self):
        print("now reset the step to 0")
        self.current_step = 0
        self.current_action_type = "single"
        self.parallel_pending.clear()
        self.parallel_actions = []
        self.parallel_waiting_start.clear()
        self.parallel_trigger_directions.clear()    
        self.parallel_wait_start_time = None
        self.parallel_motor_start_times.clear() 

    def on_icemotor_done(self, data):
        print("冰柜步进电机完成运动@@@@@@@@@@@@@@@@@@@@@@@@----statemachine")
        print(f"subscribe data:",data)
        #self.state = "DONE"  #only for test
        motor_id = data["motor_id"]    
        ctx = runtime.get(motor_id,board_id=BOARDTYPE_ICE)
        if not ctx:
            print("》》》没有ctx《《《《")
            return      

        if self.state != "WAITING":
            print("》》》状态不对《《《")
            return          

        if ctx.get("task_id") != str(self.running_task_id):
            print("并行完成反馈任务 ID 不匹配，忽略旧反馈")
            return
        # ==============================
        # 并行动作组完成事件
        # ==============================
        if self.current_action_type == "parallel":
            self.handle_parallel_motor_done(
                motor_id,
                ctx
            )

            return

        step = self.steps[self.current_step]

        if ctx["action"] != step["action"] or data["motor_id"] != step["motor"].motor_id:  #确保数据的一致性
            print(f"》》》检查未过关《《《{ctx['action']},{step['action']},{data['motor_id']},{step['motor'].motor_id}")
            return

        if step["dotype"] == "go_delay":

            self.delay_start_time = time.time()
            self.delay_duration = step["params"]["delay"]

            print(
                f"步进电机完成运动，进入延时状态，"
                f"等待 {self.delay_duration} 秒"
            )

            self.state = "DELAY"
            return
        
        
        print(f"motor {motor_id} done the action {step['action']}")
        print(f"OK检查过关OK{ctx['action']},{step['action']},{data['motor_id']},{step['motor'].motor_id}")

        self.go_next_step("on_icemotor_done")

        if self.current_step < len(self.steps):
            print(f"current step is:{self.current_step},small than total{len(self.steps)},continue state running...")
            self.state = "RUNNING"                #继续取下一个动作执行
        else:
            print(f"current step is:{self.current_step},equal bigger than total{len(self.steps)},set state done!")
            self.state = "DONE"                   #动作组完成，变更状态


    def handle_parallel_motor_done(self, motor_id, ctx):

        resource_id = (BOARDTYPE_ICE, motor_id)

        step = self.parallel_pending.get(resource_id)

        if not step:
            print(f"该电机不属于当前并行动作组: {resource_id}")
            return

        # 校验动作名称
        if ctx["action"] != step["action"]:

            print(
                f"并行电机动作不匹配: "
                f"{ctx['action']} != {step['action']}"
            )
            return

        print(
            f"并行电机 {motor_id} 完成动作 {step['action']}"
        )

        # 移除已完成电机
        self.parallel_pending.pop(resource_id)

        # 删除该电机的独立计时
        self.parallel_motor_start_times.pop(resource_id, None)

        print(
            f"并行动作剩余等待电机: "
            f"{list(self.parallel_pending.keys())}"
        )

        # 所有电机完成
        if (
            not self.parallel_pending
            and not self.parallel_waiting_start
        ):

            print("========== XYZ 并行动作全部完成 ==========")

            self.parallel_actions = []
            self.current_action_type = "single"  # 重置动作类型

            self.parallel_wait_start_time = None
            self.parallel_motor_start_times.clear()

            self.go_next_step("parallel_actions_done")

            if self.current_step < len(self.steps):

                self.state = "RUNNING"

            else:

                self.state = "DONE"     


    def check_parallel_timeout(self):
        """
        检查并行动作组的两种超时：
        1. 等待位置触发超时
        2. 单个电机运行超时
        """

        now = time.time()

        # ==================================
        # 一、等待位置触发超时
        # ==================================
        if (
            self.parallel_waiting_start
            and self.parallel_wait_start_time is not None
        ):
            elapsed = now - self.parallel_wait_start_time

            if elapsed > self.parallel_trigger_timeout:

                self.error_info = {
                    "step": self.current_step,
                    "reason": "parallel_trigger_timeout",

                    # 尚未启动的电机
                    "waiting_motors": [
                        {
                            "motor": resource_id,
                            "action": item["step"]["action"],
                            "trigger_motor_id": item["trigger_motor_id"],
                            "trigger_position": item["trigger_position"]
                        }
                        for resource_id, item
                        in self.parallel_waiting_start.items()
                    ],

                    # 已启动但尚未完成的电机
                    "running_motors": [
                        {
                            "motor": resource_id,
                            "action": step["action"]
                        }
                        for resource_id, step
                        in self.parallel_pending.items()
                    ],

                    "elapsed": elapsed
                }

                print("并行动作等待位置触发超时！")
                self.state = "ERROR"
                return True

        # ==================================
        # 二、已启动电机运行超时
        # ==================================
        for resource_id, start_time in list(
            self.parallel_motor_start_times.items()
        ):

            elapsed = now - start_time

            if elapsed > self.parallel_motor_timeout:

                self.error_info = {
                    "step": self.current_step,
                    "reason": "parallel_motor_timeout",
                    "timeout_motor": resource_id,
                    "elapsed": elapsed,

                    # 所有正在运行的电机
                    "running_motors": [
                        {
                            "motor": motor_resource,
                            "action": step["action"],
                            "elapsed": now - self.parallel_motor_start_times.get(
                                motor_resource, now
                            )
                        }
                        for motor_resource, step
                        in self.parallel_pending.items()
                    ],

                    # 所有还在等待触发的电机
                    "waiting_motors": [
                        {
                            "motor": motor_resource,
                            "action": item["step"]["action"],
                            "trigger_motor_id": item["trigger_motor_id"],
                            "trigger_position": item["trigger_position"]
                        }
                        for motor_resource, item
                        in self.parallel_waiting_start.items()
                    ]
                }

                print(f"并行电机运行超时：{resource_id}")
                self.state = "ERROR"
                return True

        return False



    def on_estop(self, data=None):
        print(f"ice machine ESTOP triggered!")

        self.state = "STOPPED"

        # 清队列
        while not self.command_queue.empty():
            self.command_queue.get()

        # 清运行任务
        self.clear_running_task()

    def on_motor_error(self, data=None):

        self.error_info = {
            "reason": "motor_error",
            "detail": data
        }

        self.state = "ERROR" 

    def destroy(self):
        self.bus.unsubscribe("ICE_MOTOR_DONE", self.on_icemotor_done)
        self.bus.unsubscribe("ESTOP_TRIGGERED", self.on_estop)
        self.bus.unsubscribe("MOTOR_ERROR", self.on_motor_error)     