
import tkinter as tk
from tkinter import ttk
import sys
from lib.communication import *

class MainWindow:
    def __init__(self, root):
            # 创建通信对象
       
        self.comm = None
        self.connected = False
        self.root = root
        self.root.title("极傲炒菜机-加料电路板Y24控制面板")
        self.root.geometry("400x200")
        
        # 创建主框架
        main_frame = ttk.LabelFrame(root, text="加料通讯控制",padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True,padx=20,pady=10)
        

       # 创建功能按钮
        button_frame_func = ttk.Frame(main_frame)
        button_frame_func.pack(fill=tk.X, pady=5)
        
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
        self.input_field = ttk.Entry(input_frame)
        self.input_field.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)


        # 创建按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.button_on = ttk.Button(button_frame, text="启动", command=self.on_button_start_clicked)
        self.button_on.pack(side=tk.LEFT, padx=5)
                
    
    def on_button_start_clicked(self):
        print("启动钮被点击")
        # 这里可以添加开按钮的具体功能
        selected_number = self.combo_numbers.get()
        input_text = self.input_field.get()
        print(f"保存设置: 选择的加料通道={selected_number}, 保持时间={input_text}")


    def on_button_connect_clicked(self):
        print("串口连接按钮被点击")
        print("初始化>>>创建通信对象")
        self.comm = RS485Communication(port="COM2", baudrate=9600, timeout=1.0)
        print(f"   串口: {self.comm.port}, 波特率: {self.comm.baudrate}, 超时: {self.comm.timeout}秒")
        self.connected =  self.comm.connect()

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
