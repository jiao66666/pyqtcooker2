
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import tkinter.messagebox as msgbox
from lib.stepmotor_communication import *
from lib.basecom import RS485Communication,BoardType

class MainWindow:
    def __init__(self, root):
        # 创建通信对象  root为tkinter的根窗口
        
        self.comm1 = None
        self.connected1 = False
        self.comm2 = None
        self.connected2 = False

        self.root = root
        self.root.title("极傲炒菜机-电机板控制系统")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        print("初始化>>>创建UI界面")
        self.init_ui()

    def init_ui(self):
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        # 创建主框架
        main_frame = ttk.LabelFrame(container, text="五轴电路板控制",padding="10")
        main_frame.place(relx=0, rely=0.05, relwidth=0.49, relheight=0.9)

        connection_section_frame = ttk.Frame(main_frame)
        connection_section_frame.pack(fill=tk.X, pady=5)
      # 创建选择框
        select_frame_port = ttk.Frame(connection_section_frame)
        select_frame_port.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame_port, text="选择端口:").pack(side=tk.LEFT, padx=5)
        self.port_var = StringVar()
        self.port_combo = ttk.Combobox(select_frame_port, textvariable=self.port_var)
        self.port_combo['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5','COM6','COM7','COM8','COM9','COM10')
        self.port_combo.current(1)
        self.port_combo.pack(side=tk.LEFT, padx=5)


        # 创建选择框
        select_frame_baud = ttk.Frame(connection_section_frame)
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

        self.button_connect = ttk.Button(connection_section_frame, text="连接串口", command=lambda:self.on_button_connect_clicked(BoardType.FIVE_AXIS))
        self.button_connect.pack(side=tk.LEFT, padx=5)

        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
                # --- 第一行：电机号 ---
        # 创建一个临时的 Frame 用于水平排列这一行的元素
        runFrame = ttk.Frame(main_frame)
        runFrame.pack(fill="x", pady=2) # fill="x" 让这一行横向填满

        motor_select_row = ttk.Frame(runFrame)
        motor_select_row.pack(fill="x", pady=2) 
        # 标签
        ttk.Label(motor_select_row, text="电 机号:").pack(side="left", padx=5)
        # 选择框
        # StringVar 用于跟踪选择框的值
        self.motor_id_var = tk.StringVar()
        self.motor_id_var.set("0")  
        motor_combobox = ttk.Combobox(motor_select_row, textvariable=self.motor_id_var, values=["0", "1", "2", "3", "4"], state="readonly", width=10)
        motor_combobox.pack(side="left", padx=5)

        # --- 第二行：转动速度 ---
        # 创建第二行的 Frame
        speed_select_row = ttk.Frame(runFrame)
        speed_select_row.pack(fill="x", pady=2)

        ttk.Label(speed_select_row, text="转动速度(角度/秒):").pack(side="left", padx=5)
        
        # 输入框
        self.speed_var = tk.StringVar()
        speed_entry = ttk.Entry(speed_select_row, textvariable=self.speed_var, width=12)
        speed_entry.pack(side="left", padx=5)

        # --- 第三行：转动距离 ---
        # 创建第三行的 Frame
        circle_input_row = ttk.Frame(runFrame)
        circle_input_row.pack(fill="x", pady=2)

        ttk.Label(circle_input_row, text="转动距离(圈):").pack(side="left", padx=5)
        
        # 输入框
        self.distance_var = tk.StringVar()
        distance_entry = ttk.Entry(circle_input_row, textvariable=self.distance_var, width=12)
        distance_entry.pack(side="left", padx=5)

        button_group_row1 = ttk.Frame(runFrame)
        button_group_row1.pack(fill=tk.X, pady=2)

        self.button_enable = ttk.Button(button_group_row1, text="使能电机", command=self.on_button_enable_clicked)
        self.button_enable.pack(side=tk.LEFT, padx=5)

        self.button_run = ttk.Button(button_group_row1, text="单次运行", command=self.on_button_run_clicked)
        self.button_run.pack(side=tk.LEFT, padx=5)


        self.button_stop = ttk.Button(button_group_row1, text="急停电机", command=self.on_button_stop_clicked)
        self.button_stop.pack(side=tk.LEFT, padx=5)
       

        self.button_pause = ttk.Button(button_group_row1, text="暂停电机", command=self.on_button_pause_clicked)
        self.button_pause.pack(side=tk.LEFT, padx=5)

        button_group_row2 = ttk.Frame(runFrame)
        button_group_row2.pack(fill=tk.X, pady=2)
     
        self.button_runlong = ttk.Button(button_group_row2, text="长运行", command=self.on_button_runlong_clicked)
        self.button_runlong.pack(side=tk.LEFT, padx=5)



        # 创建子框架
        sub_frame = ttk.LabelFrame(container, text="加料电路板控制",padding="10")
        sub_frame.place(relx=0.51, rely=0.05, relwidth=0.49, relheight=0.9)


        connection_section_frame2 = ttk.Frame(sub_frame)
        connection_section_frame2.pack(fill=tk.X, pady=5)
      # 创建选择框
        select_frame_port2 = ttk.Frame(connection_section_frame2)
        select_frame_port2.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame_port2, text="选择端口:").pack(side=tk.LEFT, padx=5)
        self.port_var2 = StringVar()
        self.port_combo2 = ttk.Combobox(select_frame_port2, textvariable=self.port_var2)
        self.port_combo2['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5','COM6','COM7','COM8','COM9','COM10')
        self.port_combo2.current(1)
        self.port_combo2.pack(side=tk.LEFT, padx=5)


        # 创建选择框
        select_frame_baud2 = ttk.Frame(connection_section_frame2)
        select_frame_baud2.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame_baud2, text="选择波特率:").pack(side=tk.LEFT, padx=5)
        self.baudrate_var2 = StringVar()
        self.baudrate_combo2 = ttk.Combobox(select_frame_baud2, textvariable=self.baudrate_var2)
        self.baudrate_combo2['values'] = ('9600', '19200', '38400', '57600', '115200')
        self.baudrate_combo2.current(0)
        self.baudrate_combo2.pack(side=tk.LEFT, padx=5)


        self.status_text2 = StringVar()
        self.status_text2.set("未连接")
        # 创建样式对象
        style = ttk.Style()
        # 配置样式
        style.configure("Connected.TLabel", foreground="green")  # 设置为绿色
        ttk.Label(select_frame_baud2, textvariable=self.status_text2, style="Connected.TLabel").pack(side=tk.LEFT, padx=5)

        self.button_connect2 = ttk.Button(connection_section_frame2, text="连接串口", command=lambda:self.on_button_connect_clicked(BoardType.FEEDER))
        self.button_connect2.pack(side=tk.LEFT, padx=5)

        separator_sub = ttk.Separator(sub_frame, orient='horizontal')
        separator_sub.pack(fill='x', pady=10)


         # 创建选择框
        select_frame = ttk.Frame(sub_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame, text="选择通道:").pack(side=tk.LEFT, padx=5)
        self.combo_numbers = ttk.Combobox(select_frame, values=[str(i) for i in range(1, 25)])
        self.combo_numbers.current(0)
        self.combo_numbers.pack(side=tk.LEFT, padx=5)
        
        # 创建输入框
        input_frame = ttk.Frame(sub_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="保持时间(ms):").pack(side=tk.LEFT, padx=5)
        self.input_keepruntime = ttk.Entry(input_frame)
        self.input_keepruntime.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)


        # 创建按钮容器
        button_frame = ttk.Frame(sub_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # 创建按钮列表
        buttons = [
            ("运行启动", self.on_button_runchannel_clicked),
        ]

        # 创建第一行按钮容器
        current_row = ttk.Frame(button_frame)
        current_row.pack(fill=tk.X)

        # 创建按钮并添加到当前行
        for i, (text, command) in enumerate(buttons):
            button = ttk.Button(current_row, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # 每隔2个按钮创建新的一行（可根据需要调整）
            if (i + 1) % 2 == 0:
                current_row = ttk.Frame(button_frame)
                current_row.pack(fill=tk.X)




    def on_closing(self):
        """窗口关闭时的处理函数"""
        if self.comm1 and self.connected1:
            try:
                self.comm1.disconnect()
                print("窗口关闭时断开串口连接1")
            except Exception as e:
                print(f"断开连接时出错: {e}")

        if self.comm2 and self.connected2:
            try:
                self.comm2.disconnect()
                print("窗口关闭时断开串口连接2")
            except Exception as e:
                print(f"断开连接时出错: {e}")    

        self.root.destroy()  # 关闭窗口

    def on_button_connect_clicked(self,boardtype:BoardType):
        print("串口连接按钮被点击")
        print(f"初始化>>>创建通信对象, 主板类型:{boardtype.value}")
        
        if boardtype == BoardType.FIVE_AXIS:
            port = self.port_var.get()
            baudrate = int(self.baudrate_var.get())
            self.comm1 = RS485Communication(port=port, baudrate=baudrate, timeout=1.0)
            print(f"   串口: {self.comm1.port}, 波特率: {self.comm1.baudrate}, 超时: {self.comm1.timeout}秒")
            self.connected1 =  self.comm1.connect()
            if self.connected1:
                self.status_text.set("已连接")
                print("   串口连接成功")
            else:
                self.status_text.set("连接失败")
                print("   串口连接失败")  

        elif boardtype == BoardType.FEEDER:   
            port = self.port_var2.get()
            baudrate = int(self.baudrate_var2.get())
            self.comm2 = RS485Communication(port=port, baudrate=baudrate, timeout=1.0)
            print(f"   串口: {self.comm2.port}, 波特率: {self.comm2.baudrate}, 超时: {self.comm2.timeout}秒")
            self.connected2 =  self.comm2.connect()
            if self.connected2:
                self.status_text2.set("已连接")
                print("   串口连接成功")
            else:
                self.status_text2.set("连接失败")
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


    def on_button_runchannel_clicked(self):
        print("启动运行按钮被点击")
        # 这里可以添加开按钮的具体功能
        selected_channel = self.combo_numbers.get()
        val_keepruntime = self.input_keepruntime.get()

        if not val_keepruntime.strip():  # 检查是否为空或仅包含空格
            print("输入数值不能为空") 
            msgbox.showwarning("提示", "输入数值不能为空")
            return 

        print(f"保存设置: 选择的加料通道={selected_channel}, 保持时间={val_keepruntime}")
        if self.connected:
            channel_id = int(selected_channel)
            params = [val_keepruntime]
            self.comm.run_channel(board_id=1, channel_id=channel_id, params=params, use_crc=True, timeout=0.3)
        else:
            print("串口未连接，无法执行运行启动操作")          
 

if __name__ == "__main__":
    print("启动极傲炒菜机-电路板控制面板。。。")
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
