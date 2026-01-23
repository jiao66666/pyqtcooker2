
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import tkinter.messagebox as msgbox
from lib.stepmotor_communication import *

class MainWindow:
    def __init__(self, root):
            # 创建通信对象
        
        self.comm = None
        self.connected = False
        self.root = root
        self.root.title("极傲炒菜机-五轴电机板控制面板")
        self.root.geometry("650x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 创建主框架
        main_frame = ttk.LabelFrame(root, text="五轴电路板控制",padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True,padx=20,pady=10)
        

       # 创建功能按钮
        button_frame_func = ttk.Frame(main_frame)
        button_frame_func.pack(fill=tk.X, pady=5)
        
      # 创建选择框
        select_frame_port = ttk.Frame(button_frame_func)
        select_frame_port.pack(fill=tk.X, pady=5)
        
        
        ttk.Label(select_frame_port, text="选择端口:").pack(side=tk.LEFT, padx=5)
        self.port_var = StringVar()
        self.port_combo = ttk.Combobox(select_frame_port, textvariable=self.port_var)
        self.port_combo['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5','COM6','COM7','COM8','COM9','COM10')
        self.port_combo.current(1)
        self.port_combo.pack(side=tk.LEFT, padx=5)


              # 创建选择框
        select_frame_baud = ttk.Frame(button_frame_func)
        select_frame_baud.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame_baud, text="选择波特率:").pack(side=tk.LEFT, padx=5)
        self.baudrate_var = StringVar()
        self.baudrate_combo = ttk.Combobox(select_frame_baud, textvariable=self.baudrate_var)
        self.baudrate_combo['values'] = ('9600', '19200', '38400', '57600', '115200')
        self.baudrate_combo.current(0)
        self.baudrate_combo.pack(side=tk.LEFT, padx=5)


        self.status_text = StringVar()
        self.status_text.set("未连接")
        # 创建样式对象
        style = ttk.Style()
        # 配置样式
        style.configure("Connected.TLabel", foreground="green")  # 设置为绿色
        ttk.Label(select_frame_baud, textvariable=self.status_text, style="Connected.TLabel").pack(side=tk.LEFT, padx=5)

  
        self.button_connect = ttk.Button(button_frame_func, text="连接串口", command=self.on_button_connect_clicked)
        self.button_connect.pack(side=tk.LEFT, padx=5)

        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
                # --- 第一行：电机号 ---
        # 创建一个临时的 Frame 用于水平排列这一行的元素
        runFrame = ttk.Frame(main_frame)
        runFrame.pack(fill="x", pady=2) # fill="x" 让这一行横向填满

        # 标签
        ttk.Label(runFrame, text="电 机号:").pack(side="left", padx=5)
        
        # 选择框
        # StringVar 用于跟踪选择框的值
        self.motor_id_var = tk.StringVar()
        self.motor_id_var.set("0")  
        motor_combobox = ttk.Combobox(runFrame, textvariable=self.motor_id_var, values=["0", "1", "2", "3", "4"], state="readonly", width=10)
        motor_combobox.pack(side="left", padx=5)

        # --- 第二行：转动速度 ---
        # 创建第二行的 Frame
        row2_frame = ttk.Frame(main_frame)
        row2_frame.pack(fill="x", pady=2)

        ttk.Label(row2_frame, text="转动速度(角度/秒):").pack(side="left", padx=5)
        
        # 输入框
        self.speed_var = tk.StringVar()
        speed_entry = ttk.Entry(row2_frame, textvariable=self.speed_var, width=12)
        speed_entry.pack(side="left", padx=5)

        # --- 第三行：转动距离 ---
        # 创建第三行的 Frame
        row3_frame = ttk.Frame(main_frame)
        row3_frame.pack(fill="x", pady=2)

        ttk.Label(row3_frame, text="转动距离(圈):").pack(side="left", padx=5)
        
        # 输入框
        self.distance_var = tk.StringVar()
        distance_entry = ttk.Entry(row3_frame, textvariable=self.distance_var, width=12)
        distance_entry.pack(side="left", padx=5)

        row4_frame = ttk.Frame(main_frame)
        row4_frame.pack(fill="x", pady=2)

        self.button_enable = ttk.Button(row4_frame, text="使能电机", command=self.on_button_enable_clicked)
        self.button_enable.pack(side=tk.LEFT, padx=5)

        self.button_run = ttk.Button(row4_frame, text="单次运行", command=self.on_button_run_clicked)
        self.button_run.pack(side=tk.LEFT, padx=5)

        self.button_runlong = ttk.Button(row4_frame, text="长运行", command=self.on_button_runlong_clicked)
        self.button_runlong.pack(side=tk.LEFT, padx=5)

        self.button_pause = ttk.Button(row4_frame, text="暂停电机", command=self.on_button_pause_clicked)
        self.button_pause.pack(side=tk.LEFT, padx=5)

        self.button_stop = ttk.Button(row4_frame, text="急停电机", command=self.on_button_stop_clicked)
        self.button_stop.pack(side=tk.LEFT, padx=5)

        row5_frame = ttk.Frame(main_frame)
        row5_frame.pack(fill="x", pady=2)

        self.button_enableall = ttk.Button(row5_frame, text="使能全部", command=self.on_button_enableall_clicked)
        self.button_enableall.pack(side=tk.LEFT, padx=5)

        self.button_pauseall = ttk.Button(row5_frame, text="暂停全部", command=self.on_button_pauseall_clicked)
        self.button_pauseall.pack(side=tk.LEFT, padx=5)

        self.button_stopall = ttk.Button(row5_frame, text="急停全部", command=self.on_button_stopall_clicked)
        self.button_stopall.pack(side=tk.LEFT, padx=5)



        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)


    def on_closing(self):
        """窗口关闭时的处理函数"""
        if self.comm and self.connected:
            try:
                self.comm.disconnect()
                print("窗口关闭时断开串口连接")
            except Exception as e:
                print(f"断开连接时出错: {e}")
        self.root.destroy()  # 关闭窗口

    def on_button_connect_clicked(self):
        print("串口连接按钮被点击")
        print("初始化>>>创建通信对象")
        port = self.port_var.get()
        baudrate = int(self.baudrate_var.get())
        self.comm = RS485Communication(port=port, baudrate=baudrate, timeout=1.0)
        print(f"   串口: {self.comm.port}, 波特率: {self.comm.baudrate}, 超时: {self.comm.timeout}秒")
        self.connected =  self.comm.connect()
        if self.connected:
            self.status_text.set("已连接")
            print("   串口连接成功")
        else:
            self.status_text.set("连接失败")
            print("   串口连接失败")  

    def on_button_run_clicked(self):
        print("电机运行按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        speed = self.speed_var.get()
        distance = self.distance_var.get()

        if speed == "" or speed == 0:
            print("   请输入有效的速度值")
            return
        
        if distance == "" or distance == 0:
            print("   请输入有效的距离值")
            return
        
        motor_id = int(self.motor_id_var.get())
        speed = str(speed)
        distance = int(distance)

         # 将圈数转换为脉冲数
        pulses=str(self.convert_revolutions_to_pulses(distance))
        print(f"   电机号: {motor_id}, 转动速度: {speed}转/秒, 转动距离: {distance}圈")
        self.comm.run_single_motor(1, motor_id, [pulses,speed])


    def on_button_enable_clicked(self):
        print("电机使能按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        motor_id = int(self.motor_id_var.get())

        print(f" 使能电机号: {motor_id}")
        self.comm.enable_single_motor(1, motor_id, [])
    

    def on_button_enableall_clicked(self):
        print("电机使能全部按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        self.comm.enable_all_motor(1)


    def on_button_pauseall_clicked(self):
        print("电机暂停全部按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        self.comm.pause_all_motor(1)

    def on_button_stopall_clicked(self):
        print("电机急停全部按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        self.comm.stop_all_motor(1)                

    def on_button_pause_clicked(self):
        print("电机暂停按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        motor_id = int(self.motor_id_var.get())

        print(f" 暂停电机号: {motor_id}")
        self.comm.pause_single_motor(1, motor_id, [])        


    def on_button_stop_clicked(self):
        print("电机急停按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        motor_id = int(self.motor_id_var.get())

        print(f" 急停电机号: {motor_id}")
        self.comm.stop_single_motor(1, motor_id, [])

    def on_button_runlong_clicked(self):
        print("电机长运行按钮被点击")               
        if not self.connected:
            print("   串口未连接，无法运行电机")    
            return
        
        motor_id = int(self.motor_id_var.get())
        speed = str(self.speed_var.get())
        print(f"   长运行电机号: {motor_id}, 转动速度: {speed}转/秒")
        self.comm.run_single_motor_long(1, motor_id, ["-1",speed])


    def convert_revolutions_to_pulses(self,revolutions: int, step_angle: float = 1.8, microstepping: int = 1) -> int:
        """
        将圈数转换为脉冲数

        参数:
            revolutions: 圈数
            step_angle: 每步的角度（默认为 1.8°）
            microstepping: 细分模式（默认为 1，即无细分）

        返回:
            int: 计算得到的脉冲数
        """
        # 计算每圈的脉冲数
        pulses_per_revolution = 360 / step_angle * microstepping
        # 计算总脉冲数
        pulses = revolutions * pulses_per_revolution
        return int(pulses)






if __name__ == "__main__":
    print("启动极傲炒菜机-五轴电路板控制面板。。。")
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
