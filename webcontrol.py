# flaskcontrol.py
from flask import Flask, render_template, jsonify,request
from lib.boardcontroller import BoardController
from lib.boardtype import *
import time
from lib.tools import is_dev_mode
from lib.websocket_server import WebSocketServer

import asyncio
from threading import Thread
app = Flask(__name__)

boardercontrollers = {}

# 根据传入的命令行参数设置端口,方便测试和生产环境使用不同的端口
if is_dev_mode():
    print("当前环境: 开发环境，使用测试端口")
    port = 3000
    stepmotor_port = "COM2"
    feedermotor_port = "COM3"
else:
    print("当前环境: 生产环境，使用生产端口")
    port = 5000
    stepmotor_port = 'COM6'
    feedermotor_port = 'COM7'


# 保持 WebSocket 服务器的全局实例
websocket_server = None

# 启动 WebSocket 服务器的异步函数
async def start_websocket_server():
    global websocket_server
    websocket_server = WebSocketServer()  # 创建 WebSocket 实例
    await websocket_server.start_in_thread()  # 启动 WebSocket 服务器

# 启动 WebSocket 服务器的线程
def run_websocket_server():
    # 创建新的事件循环，并设置为当前线程的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 启动 WebSocket 服务器
    loop.run_until_complete(start_websocket_server())


# 渲染前端的 HTML 页面
@app.route('/')
def index():
    return render_template('index.html')  # Flask 会自动在 templates 目录下寻找 index.html

# API 路由
@app.route('/connect', methods=['POST'])
def connect():
    """Flask 后端接口的 connect 方法"""
    global websocket_server

    # 如果 WebSocket 服务器还没有启动，则启动它
    if websocket_server is None:
        print("WebSocket 服务器未启动，正在启动...")
        # 使用 threading 启动 WebSocket 服务器
        from threading import Thread
        thread = Thread(target=run_websocket_server)
        thread.start()
    else:
        print("WebSocket 服务器已经启动，无需重复启动")    


    if not boardercontrollers.get("boardcontroller1"):
        boardercontrollers["boardcontroller1"] = BoardController(BOARDTYPE_FIVE_AXIS, board_name="五轴控制板")

    if not boardercontrollers.get("boardcontroller2"):
        boardercontrollers["boardcontroller2"] = BoardController(BOARDTYPE_FEEDER, board_name="加料控制板")           

    if  boardercontrollers["boardcontroller1"].connected:
        print("已经连接到五轴步进主板，无需重复连接")
        return jsonify({"status": "fail","message": "已经连接到五轴步进主板，无需重复连接"}) 
    
    if  boardercontrollers["boardcontroller2"].connected:
        print("已经连接到加料主板，无需重复连接")
        return jsonify({"status": "fail","message": "已经连接到加料主板，无需重复连接"}) 
    
    # 真实环境连接
    success1 =  boardercontrollers["boardcontroller1"].connect(port=stepmotor_port,baudrate="115200")
    success2 =  boardercontrollers["boardcontroller2"].connect(port=feedermotor_port,baudrate="9600")

    if success1 and success2 :
        print("连接成功!")
        return jsonify({"status": "success","message": "连接成功!"})
    else:
        print("连接失败!")
        return jsonify({"status": "fail","message": f"连接失败!,连接状态：五轴板：{success1}，加料板：{success2}"})
    

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if not boardercontrollers.get("boardcontroller1"):
        print("找不到步进主板控制器，无法操作")
        return jsonify({"status": "fail","message": "找不到步进主板控制器，无法操作"})   

    if not boardercontrollers.get("boardcontroller2"):
        print("找不到加料主板控制器，无法操作")
        return jsonify({"status": "fail","message": "找不到加料主板控制器，无法操作"})    

    if not  boardercontrollers["boardcontroller1"].connected:
        print("步进主板已经断开，无需重复操作")
        return jsonify({"status": "fail","message": "步进板已经断开，无需重复操作"})      

    if not  boardercontrollers["boardcontroller2"].connected:
        print("加料主板已经断开，无需重复操作")
        return jsonify({"status": "fail","message": "加料板已经断开，无需重复操作"})  
             
    success1 =  boardercontrollers["boardcontroller1"].disconnect()
    success2 =  boardercontrollers["boardcontroller2"].disconnect()

    if success1 and success2 :
        print("断开连接成功!")
        return jsonify({"status": "success","message": "断开连接成功!"})
    else:
        print("断开连接失败!")
        return jsonify({"status": "fail","message": f"断开连接失败!,断开状态：五轴板：{success1}，加料板：{success2}"})    


@app.route('/testtastboardping', methods=['POST'])
def testtastboardping():
    print("测试加料板连通性")
    if not boardercontrollers.get("boardcontroller2"):
        print("找不到加料主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到加料主板控制器，无法操作,请先连接串口"})
    success =  boardercontrollers["boardcontroller2"].motors[0].ping()
    if success :
        print("测试加料板连通性成功!")
        return jsonify({"status": "success","message": f"运行成功"})
    else:
        print("测试加料板连通性失败!")
        return jsonify({"status": "fail","message": "运转失败!"})


@app.route('/runtastmotor', methods=['POST'])
def runtastmotor():
    print("测试加料板运行")
    data = request.get_json()
    motorid = data.get('motorid')
    overtime = data.get('overtime')
    success = False
    print("收到参数 :", motorid)
    if not boardercontrollers.get("boardcontroller2"):
        print("找不到加料主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到加料主板控制器，无法操作,请先连接串口"})
    success =  boardercontrollers["boardcontroller2"].motors[int(motorid)].run(int(overtime))
    if success :
        print("测试加料板打开成功!")
        return jsonify({"status": "success","message": f"运行成功"})
    else:
        print("测试加料板打开失败!")
        return jsonify({"status": "fail","message": "运转失败!"})


@app.route('/gettastmotorfb', methods=['POST'])
def gettastmotorfb():
    print("测试加料板获取结果运行")
    data = request.get_json()
    motorid = data.get('motorid')
    mode = data.get('mode')
    success = False
    print("收到参数 :", motorid)
    if not boardercontrollers.get("boardcontroller2"):
        print("找不到加料主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到加料主板控制器，无法操作,请先连接串口"})
    success,resp =  boardercontrollers["boardcontroller2"].motors[int(motorid)].getfb(int(mode))
    if success :
        print("测试加料板打开成功!")
        return jsonify({"status": "success","message": f"运行获取反馈成功，反馈结果：{resp}"})
    else:
        print("测试加料板打开失败!")
        return jsonify({"status": "fail","message": "运转失败!"})
    


@app.route('/runlong', methods=['POST'])
def runlong():
    print("运行电机长运转")
    data = request.get_json()
    motorid = data.get('motorid')  # 获取 'port' 参数
    direction = data.get('direction')  # 获取 'baudrate' 参数
    speed = data.get('speed')  # 获取 'boardtype' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", motorid, direction,speed)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[motorid].runlong(int(int(speed)*360),int(direction))
    if success :
        print("电机长运转成功!")
        return jsonify({"status": "success","message": f"长运行成功!电机：{motorid}，方向：{direction}，速度：{speed}"})
    else:
        print("电机长运转失败!")
        return jsonify({"status": "fail","message": "长运转失败!"})
    

@app.route('/run', methods=['POST'])
def run():
    print("运行电机单次运转")
    data = request.get_json()
    motorid = data.get('motorid')  # 获取 'port' 参数
    direction = data.get('direction')  # 获取 'baudrate' 参数
    speed = data.get('speed')  # 获取 'boardtype' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    circles = data.get('circle')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", motorid, direction,speed)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[motorid].run(float(circles),int(int(speed)*360),int(direction))
    if success :
        print("电机单次运转成功!")
        return jsonify({"status": "success","message": f"单运行成功!电机：{motorid}，方向：{direction}，速度：{speed}"})
    else:
        print("电机单次运转失败!")
        return jsonify({"status": "fail","message": "单运转失败!"})




@app.route('/runabs', methods=['POST'])
def runabs():
    print("运行电机单次运转绝对值坐标")
    data = request.get_json()
    motorid = data.get('motorid')  # 获取 'port' 参数
    direction = data.get('direction')  # 获取 'baudrate' 参数
    speed = data.get('speed')  # 获取 'boardtype' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    circles = data.get('circle')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", motorid, direction,speed)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        ishomed = boardercontrollers["boardcontroller1"].motors[motorid].homed
        if not ishomed:
           return jsonify({"status": "error","message": "电机未归零，无法运行绝对位置，请先复位电机!"})
        
        success =  boardercontrollers["boardcontroller1"].motors[motorid].go(float(circles),int(int(speed)*360))
        currentpos = boardercontrollers["boardcontroller1"].motors[motorid].current_position
    if success :
        print("电机单次运转成功!")
        return jsonify({"status": "success","message": f"运行电机成功!电机号：{motorid}，速度：{speed}，当前位置：{currentpos}"})
    else:
        print("电机单次运转失败!")
        return jsonify({"status": "fail","message": "运转失败!"})

@app.route('/pause', methods=['POST'])
def pause():
    print("暂停电机运转")
    data = request.get_json()
    motorid = data.get('motorid')  # 获取 'port' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", motorid)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[motorid].pause()
    if success :
        print("电机暂停成功!")
        return jsonify({"status": "success","message": "电机暂停成功!"})
    else:
        print("电机暂停失败!")
        return jsonify({"status": "fail","message": "电机暂停失败!"})    


@app.route('/stop', methods=['POST'])
def stop():
    print("暂停电机运转")
    data = request.get_json()
    motorid = data.get('motorid')  # 获取 'port' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", motorid)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[motorid].stop()
    if success :
        print("电机暂停成功!")
        return jsonify({"status": "success","message": "电机暂停成功!"})
    else:
        print("电机暂停失败!")
        return jsonify({"status": "fail","message": "电机暂停失败!"})    
    
 
    
   
@app.route('/test', methods=['POST'])
def test():
    """
    print("测试开始")
    testSendDirectly()
    print("测试完成!")
    return jsonify({"status": "success","message": "测试成功!"})
    """
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[1].enable_all_motors()

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})


@app.route('/fixmotor', methods=['POST'])
def fixmotor():
    print("电机归零")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[1].fix_all_motors()

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})

@app.route('/stopall', methods=['POST'])
def stopall():
    print("所有电机急停")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[1].stop_all_motors()

        for motor_id in range(5):  # 由于是异常终止 ，需要手动将所有电机的归位状态设为 False
            motor = boardercontrollers["boardcontroller1"].motors[motor_id]
            if motor.homed:
                motor.homed = False

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "急停所有电机成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "急停所有电机失败!"})
    

@app.route('/enableall', methods=['POST'])
def enableall():
    print("所有电机使能")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[1].enable_all_motors()

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})    




@app.route('/resetmotor', methods=['POST'])
def resetmotor():
    print("运行电机长运转")
    data = request.get_json()
    motorid = data.get('motorid')  # 获取 'port' 参数
    direction = data.get('direction')  # 获取 'baudrate' 参数
    speed = data.get('speed')  # 获取 'boardtype' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", motorid, direction,speed)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success,resp =  boardercontrollers["boardcontroller1"].motors[motorid].reset_one_motor()
    if success :
        print("测试复位成功!")
        return jsonify({"status": "success","message": f"复位电机成功!电机：{motorid}，方向：{direction}"})
    else:
        print("测试复位失败!")
        return jsonify({"status": "fail","message": f"复位电机失败!,电机：{motorid}，错误信息：{resp}"})



@app.route('/resetmotorpot', methods=['POST'])
def resetmotorpot():
    print("运行整体复位任务")
    data = request.get_json()
    potnum = int(data.get('potnum'))  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", potnum)

    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})

    if potnum ==1:   
        success,resp =  boardercontrollers["boardcontroller1"].motors[2].resettask()
        success,resp =  boardercontrollers["boardcontroller1"].motors[1].resettask()
    else:
        success,resp =  boardercontrollers["boardcontroller1"].motors[4].resettask()        
        success,resp =  boardercontrollers["boardcontroller1"].motors[3].resettask()        
        
    if success :
        print("测试复位成功!")
        return jsonify({"status": "success","message": f"复位电机成功!锅号：{potnum}"})
    else:
        print("测试复位失败!")
        return jsonify({"status": "fail","message": f"复位电机失败!,锅号：{potnum}，错误信息：{resp}"})

@app.route('/readmotor', methods=['POST'])
def readmotor():
    print("电机状态读取")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    motorid = data.get('motorid')  # 获取 'port' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        success =  boardercontrollers["boardcontroller1"].motors[motorid].readmotor()

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})
    
@app.route('/testtask', methods=['POST'])
def testtask():
    print("电机状态读取")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    motorid = data.get('motorid')  # 获取 'port' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        
        #runtask参数：[圈数，速度，方向]
        success = boardercontrollers["boardcontroller1"].motors[motorid].runtask(0.5,360,1)   
        success = boardercontrollers["boardcontroller1"].motors[motorid].runtask(0.5,360,-1)

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})    





@app.route('/testtaskabs', methods=['POST'])
def testtaskabs():
    print("电机状态读取")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    motorid = data.get('motorid')  # 获取 'port' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        
        #runtask参数：[圈数，速度，方向]
        success = boardercontrollers["boardcontroller1"].motors[motorid].gotask(1,360)   
        success = boardercontrollers["boardcontroller1"].motors[motorid].gotask(0,360)

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})    


@app.route('/testmultitask', methods=['POST'])
def testmultitask():
    print("电机状态读取")
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    motorid = data.get('motorid')  # 获取 'port' 参数
    success = False
    if boardtype == '1':
        #list_ports()
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
        
        #runtask参数：[圈数，速度，方向]
        success = boardercontrollers["boardcontroller1"].motors[2].runtask(0.5,360,1)  
        success = boardercontrollers["boardcontroller1"].motors[2].runtask(0.5,360,-1)    
        success = boardercontrollers["boardcontroller1"].motors[1].runtask(0.2,360,-1)
        success = boardercontrollers["boardcontroller1"].motors[1].runtask(0.2,360,1)

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})    



@app.route('/readpulse', methods=['POST'])
def readpulse():
    print("已转脉冲读取")
    data = request.get_json()
    mode = int(data.get('mode') ) # 获取 'boardtype' 参数
    motorid =int(data.get('motorid'))  # 获取 'port' 参数
    success = False
    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
    
    if not boardercontrollers["boardcontroller1"].motors[1].homed or not boardercontrollers["boardcontroller1"].motors[2].homed:
        print("电机未归位，无法操作")
        return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})    
    
    #runtask参数：[圈数，速度，方向]
    print(f"正在读取已转脉冲数，当前motorid:{motorid}，mode:{mode}")
    success,resp = boardercontrollers["boardcontroller1"].motors[motorid].readpulse(mode) 

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": f"测试成功!,返回结果:{resp}"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})  

@app.route('/testmultitaskabs', methods=['POST'])   #绝对位置任务测试
def testmultitaskabs():
    print("1号锅测试水平翻转任务开始")

    data = request.get_json()
    speed_level = data.get('speed_level') 
    speed_flip = data.get('speed_flip') 
    success = False
    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
    
    if not boardercontrollers["boardcontroller1"].motors[1].homed or not boardercontrollers["boardcontroller1"].motors[2].homed:
        print("电机未归位，无法操作")
        return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})

    #runtask参数：[圈数，速度，方向]
    print("**************************************1号锅测试水平翻转任务开始******************************")
    move_speed = int(speed_level)   #2160  tested
    flip_speed = int(speed_flip)   #2520  tested 

    if move_speed > 3600:   #  10圈/秒  已经非常快了，超过这个速度可能会有安全隐患，限制最高速度为3600
        move_speed = 3600
    elif move_speed < 360:
        move_speed = 360

    if flip_speed > 3600:   
        flip_speed = 3600
    elif flip_speed < 360:
        flip_speed = 360    


    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(5.05,flip_speed)  
    success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(4.20,move_speed)
    time.sleep(1)    
    success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(0,move_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(0,flip_speed)
    time.sleep(1)

    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(5.05,flip_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(4.20,move_speed)
   
    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(20.2,flip_speed)
    time.sleep(1)
    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(-11.8,flip_speed)
    time.sleep(1)
    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(5.05,flip_speed)

    success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(0,move_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(0,flip_speed)

    print("**************************************1号锅测试水平翻转任务结束******************************")

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})  




@app.route('/testmultiaxis', methods=['POST'])   #绝对位置任务测试
def testmultiaxis():
    print("1号多轴同步运动任务开始")
    data = request.get_json()
    speed_level = data.get('speed_level') 
    speed_flip = data.get('speed_flip') 
    success = False
    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
    success = False
    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
    
    if not boardercontrollers["boardcontroller1"].motors[1].homed or not boardercontrollers["boardcontroller1"].motors[2].homed:
        print("电机未归位，无法操作")
        return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})

    #runtask参数：[圈数，速度，方向]
    print("**************************************1号多轴同步运动任务开始开始******************************")

    move_speed = int(speed_level)   #2160  tested
    flip_speed = int(speed_flip)   #2520  tested 

    if move_speed > 3600:   #  10圈/秒  已经非常快了，超过这个速度可能会有安全隐患，限制最高速度为3600
        move_speed = 3600
    elif move_speed < 360:
        move_speed = 360

    if flip_speed > 3600:   
        flip_speed = 3600
    elif flip_speed < 360:
        flip_speed = 360    


    success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask_advanced(5.05,flip_speed,False,4.4)  
    success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(4.20,move_speed)
    

    print("**************************************1号多轴同步运动任务开始任务结束******************************")

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})  




@app.route('/testmultitaskabs2', methods=['POST'])   #绝对位置任务测试
def testmultitaskabs2():
    print("2号锅测试水平翻转任务开始")
    data = request.get_json()
    speed_level = data.get('speed_level') 
    speed_flip = data.get('speed_flip') 

    success = False
    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
    
    if not boardercontrollers["boardcontroller1"].motors[3].homed or not boardercontrollers["boardcontroller1"].motors[4].homed:
        print("电机未归位，无法操作")
        return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})

    #runtask参数：[圈数，速度，方向]
    print("**************************************2号锅测试水平翻转任务开始******************************")
    move_speed = int(speed_level)   #2160  tested
    flip_speed = int(speed_flip)   #2520  tested 

    if move_speed > 3600:   #  10圈/秒  已经非常快了，超过这个速度可能会有安全隐患，限制最高速度为3600
        move_speed = 3600
    elif move_speed < 360:
        move_speed = 360

    if flip_speed > 3600:   
        flip_speed = 3600
    elif flip_speed < 360:
        flip_speed = 360    


    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(4.5,flip_speed)  
    success = boardercontrollers["boardcontroller1"].motors[POT2_MOVE_MOTOR].gotask(4.15,move_speed)
    time.sleep(1)    
    success = boardercontrollers["boardcontroller1"].motors[POT2_MOVE_MOTOR].gotask(0,move_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(0,flip_speed)
    time.sleep(1)

    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(4.5,flip_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT2_MOVE_MOTOR].gotask(4.15,move_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(20.2,flip_speed)
    time.sleep(1)
    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(-12.1,flip_speed)
    time.sleep(1)
    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(4.5,flip_speed)

    success = boardercontrollers["boardcontroller1"].motors[POT2_MOVE_MOTOR].gotask(0,move_speed)
    success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(0,flip_speed)

    print("**************************************2号锅测试水平翻转任务结束******************************")

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})  


@app.route('/gopos', methods=['POST'])
def gopos():
    print("锅位移动")
    data = request.get_json()
    potnum = int(data.get('potnum')) 
    postype = str(data.get('postype')) 
    speed= int(data.get('speed')) 

    if postype == 'pos_outfood':
        print("移动到外倒料口")
        flip_pos = POT1_POS_OUTFOOD_FLIP
        level_pos = POT1_POS_OUTFOOD_LEVEL
    elif postype == 'pos_infood':
        print("移动到内倒料口口")
        flip_pos = POT1_POS_INFOOD_FLIP
        level_pos = POT1_POS_INFOOD_LEVEL
    elif postype == 'pos_washpot':
        print("移动到洗锅位置")
        flip_pos = POT1_POS_WASHPOT_FLIP
        level_pos = POT1_POS_WASHPOT_LEVEL
    elif postype == 'pos_firepot':
        flip_pos = POT1_POS_FIREPOT_FLIP
        level_pos = POT1_POS_FIREPOT_LEVEL
        print("移动到灶位")        
    else:
        print("未知位置")
        return jsonify({"status": "fail","message": "未知位置"})

    speed = speed * 360  # 转换为电机实际速度值
    if speed > 3600:   
        speed = 3600
    elif speed < 360:
        speed = 360

    success = False

    if not boardercontrollers.get("boardcontroller1"):
        print("找不到主板控制器，无法操作")
        return jsonify({"status": "error","message": "找不到主板控制器，无法操作,请先连接串口"})
    
    if not boardercontrollers["boardcontroller1"].motors[1].homed or not boardercontrollers["boardcontroller1"].motors[2].homed:
        print("电机未归位，无法操作")
        return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})    
    
    if potnum == 1:
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(POT_POS_SAFE_FLIP,speed)  
        success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(level_pos,speed)  
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(flip_pos,speed)  
    elif potnum == 2:
        success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(POT_POS_SAFE_FLIP,speed)  
        success = boardercontrollers["boardcontroller1"].motors[POT2_MOVE_MOTOR].gotask(level_pos,speed)  
        success = boardercontrollers["boardcontroller1"].motors[POT2_FLIP_MOTOR].gotask(flip_pos,speed)    
    
    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})    



           
if __name__ == '__main__':
    # 绑定到所有网络接口，允许局域网访问,测试使用3000端口，实际生产使用5000端口
    app.run(debug=True, host='0.0.0.0', port=port)
