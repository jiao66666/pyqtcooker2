# flaskcontrol.py
from flask import Flask, render_template, jsonify,request
from lib.boardcontroller import BoardController
from lib.boardtype import *
import argparse
import sys
import time

app = Flask(__name__)

boardercontrollers = {}


# 设置命令行参数解析器
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=5000, help='Set the port for the server (default is 3000)')
parser.add_argument('--stepmotor_port', type=str, default='COM6', help='Step motor port (default is COM6)')
parser.add_argument('--feedermotor_port', type=str, default='COM7', help='Feeder motor port (default is COM7)')
args = parser.parse_args()

# 根据传入的命令行参数设置端口,方便测试和生产环境使用不同的端口
port = args.port
stepmotor_port = args.stepmotor_port
feedermotor_port = args.feedermotor_port

# 渲染前端的 HTML 页面
@app.route('/')
def index():
    return render_template('index.html')  # Flask 会自动在 templates 目录下寻找 index.html

# API 路由
@app.route('/connect', methods=['POST'])
def connect():
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
        success =  boardercontrollers["boardcontroller1"].motors[motorid].reset_one_motor(int(direction))
    if success :
        print("测试复位成功!")
        return jsonify({"status": "success","message": f"复位电机成功!电机：{motorid}，方向：{direction}"})
    else:
        print("测试复位失败!")
        return jsonify({"status": "fail","message": "复位电机失败!"})


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


@app.route('/testmultitaskabs', methods=['POST'])   #绝对位置任务测试
def testmultitaskabs():
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
        
        if not boardercontrollers["boardcontroller1"].motors[1].homed or not boardercontrollers["boardcontroller1"].motors[2].homed:
           print("电机未归位，无法操作")
           return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})

        #runtask参数：[圈数，速度，方向]
        print("**************************************1号锅测试水平翻转任务开始******************************")
        move_speed = 720
        flip_speed = 1080

        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(4.5,flip_speed)  
        success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(4.20,move_speed)
        time.sleep(1)    
        success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(0,move_speed)
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(0,flip_speed)
        time.sleep(1)

        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(4.5,flip_speed)
        success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(4.20,move_speed)
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(20.2,flip_speed)
        time.sleep(1)
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(-12.1,flip_speed)
        time.sleep(1)
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(4.5,flip_speed)

        success = boardercontrollers["boardcontroller1"].motors[POT1_MOVE_MOTOR].gotask(0,move_speed)
        success = boardercontrollers["boardcontroller1"].motors[POT1_FLIP_MOTOR].gotask(0,flip_speed)

        print("**************************************1号锅测试水平翻转任务结束******************************")

    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})  



@app.route('/testmultitaskabs2', methods=['POST'])   #绝对位置任务测试
def testmultitaskabs2():
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
        
        if not boardercontrollers["boardcontroller1"].motors[3].homed or not boardercontrollers["boardcontroller1"].motors[4].homed:
           print("电机未归位，无法操作")
           return jsonify({"status": "error","message": "电机未归位，无法操作,请先复位"})

        #runtask参数：[圈数，速度，方向]
        print("**************************************2号锅测试水平翻转任务开始******************************")
        move_speed = 360
        flip_speed = 180 


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


           
if __name__ == '__main__':
    # 绑定到所有网络接口，允许局域网访问,测试使用3000端口，实际生产使用5000端口
    app.run(debug=True, host='0.0.0.0', port=port)
