
import tkinter as tk
from tkinter import ttk
import sys

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("控制面板")
        self.root.geometry("400x200")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选择框
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame, text="选择数字:").pack(side=tk.LEFT, padx=5)
        self.combo_numbers = ttk.Combobox(select_frame, values=[str(i) for i in range(1, 25)])
        self.combo_numbers.current(0)
        self.combo_numbers.pack(side=tk.LEFT, padx=5)
        
        # 创建按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.button_on = ttk.Button(button_frame, text="开", command=self.on_button_on_clicked)
        self.button_on.pack(side=tk.LEFT, padx=5)
        
        self.button_off = ttk.Button(button_frame, text="关", command=self.on_button_off_clicked)
        self.button_off.pack(side=tk.LEFT, padx=5)
        
        # 创建输入框
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="输入内容:").pack(side=tk.LEFT, padx=5)
        self.input_field = ttk.Entry(input_frame)
        self.input_field.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 创建保存按钮
        self.button_save = ttk.Button(main_frame, text="设置保存", command=self.on_button_save_clicked)
        self.button_save.pack(fill=tk.X, pady=10)
    
    def on_button_on_clicked(self):
        print("开按钮被点击")
        # 这里可以添加开按钮的具体功能
    
    def on_button_off_clicked(self):
        print("关按钮被点击")
        # 这里可以添加关按钮的具体功能
    
    def on_button_save_clicked(self):
        selected_number = self.combo_numbers.get()
        input_text = self.input_field.get()
        print(f"保存设置: 选择的数字={selected_number}, 输入内容={input_text}")
        # 这里可以添加保存功能的具体实现

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
