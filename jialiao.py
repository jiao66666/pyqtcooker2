
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import tkinter.messagebox as msgbox
from lib.communication import *

class MainWindow:
    def __init__(self, root):
            # 创建通信对象
        
        self.comm = None
        self.connected = False
        self.root = root
        self.root.title("极傲炒菜机-加料电路板Y24控制面板")
        self.root.geometry("450x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 创建主框架
        main_frame = ttk.LabelFrame(root, text="加料通讯控制",padding="10")
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
        self.port_combo['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5')
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

        self.button_ping = ttk.Button(button_frame_func, text="板子连通性", command=self.on_button_ping_clicked)
        self.button_ping.pack(side=tk.LEFT, padx=5)

        self.button_reboot = ttk.Button(button_frame_func, text="板子重启", command=self.on_button_reboot_clicked)
        self.button_reboot.pack(side=tk.LEFT, padx=5)


        # 创建选择框
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame, text="选择通道:").pack(side=tk.LEFT, padx=5)
        self.combo_numbers = ttk.Combobox(select_frame, values=[str(i) for i in range(1, 25)])
        self.combo_numbers.current(0)
        self.combo_numbers.pack(side=tk.LEFT, padx=5)
        
        # 创建输入框
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="保持时间(ms):").pack(side=tk.LEFT, padx=5)
        self.input_keepruntime = ttk.Entry(input_frame)
        self.input_keepruntime.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)


        # 创建按钮容器
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # 创建按钮列表
        buttons = [
            ("运行启动", self.on_button_runchannel_clicked),
            ("获取通道反馈", self.on_button_getchannel_clicked),
            ("开关量-开", lambda: self.on_button_runoutput_clicked("1")),
            ("开关量-关", lambda: self.on_button_runoutput_clicked("0")),
            ("获取开关量反馈", self.on_button_getoutput_clicked)
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
        if self.comm and self.connected:
            try:
                self.comm.disconnect()
                print("窗口关闭时断开串口连接")
            except Exception as e:
                print(f"断开连接时出错: {e}")
        self.root.destroy()  # 关闭窗口

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



    def on_button_runoutput_clicked(self,status):
        print("开关量按钮被点击")
        # 这里可以添加开按钮的具体功能
        selected_channel = self.combo_numbers.get()
      

        print(f"保存设置: 选择的加料通道={selected_channel}")
        if self.connected:
            channel_id = int(selected_channel)
            params = [status]
            self.comm.run_output(board_id=1, channel_id=channel_id, params=params, use_crc=True, timeout=0.3)
        else:
            print("串口未连接，无法执行运行启动操作")    


    def on_button_getchannel_clicked(self):
        print("获取通道反馈按钮被点击")
        # 这里可以添加开按钮的具体功能
        selected_channel = self.combo_numbers.get()
       
        print(f"保存设置: 选择的获取通道={selected_channel}")
        if self.connected:
            channel_id = int(selected_channel)
            params = []
            self.comm.get_channel(board_id=1, channel_id=channel_id, params=params, use_crc=True, timeout=0.3)
        else:
            print("串口未连接，无法执行运行启动操作")

    def on_button_getoutput_clicked(self):
        print("获取开关量反馈按钮被点击")
        # 这里可以添加开按钮的具体功能
        selected_channel = self.combo_numbers.get()
       
        print(f"保存设置: 选择的获取通道={selected_channel}")
        if self.connected:
            channel_id = int(selected_channel)
            params = []
            self.comm.get_output(board_id=1, channel_id=channel_id, params=params, use_crc=True, timeout=0.3)
        else:
            print("串口未连接，无法执行运行启动操作")                               

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

    def on_button_ping_clicked(self):
        print("板子ping按钮被点击")
        if not self.connected:
            print("串口未连接，无法执行ping操作")
            return
        self.comm.check_ping(board_id=1, use_crc=True, timeout=0.3)

    def on_button_reboot_clicked(self):
        print("重启按钮被点击")
        if not self.connected:
            print("串口未连接，无法执行重启操作")
            return
        self.comm.restart_board(board_id=1, use_crc=True, timeout=0.3)
                      
    

if __name__ == "__main__":
    print("启动极傲炒菜机-加料电路板Y24控制面板。。。")
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
