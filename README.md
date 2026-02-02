
# PyQt 控制面板

这是一个使用PyQt5创建的简单控制面板应用程序，集成了pyserial库以支持串口通信功能。

## 功能

- 数字选择框：可以选择1-24范围内的数字
- 开关按钮：包含"开"和"关"两个按钮
- 输入框：可以输入文本内容
- 设置保存按钮：保存当前设置
- 串口通信：支持通过pyserial库进行串口通信（预留功能）

## 安装与运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行程序：
   ```
   python main.py
   ```

## 使用说明

1. 从下拉框中选择1-24之间的数字
2. 使用"开"或"关"按钮进行控制
3. 在输入框中输入需要的文本
4. 点击"设置保存"按钮保存当前设置

## 注意事项

- 本程序基于PyQt5开发，确保已正确安装PyQt5
- 项目已集成pyserial库，可用于未来的串口通信功能开发
- 当前版本为基本功能实现，保存功能仅打印到控制台，可根据需求扩展
- 串口通信功能为预留接口，尚未实现具体功能
## bakup1

## build package command
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" webcontrol.py


## for test only
python webcontrol.py --port 3000

