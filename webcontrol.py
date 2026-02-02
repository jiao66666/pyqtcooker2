# flaskcontrol.py
from flask import Flask, render_template, jsonify,request
from lib.boardcontroller import BoardController
from lib.boardtype import BoardType


app = Flask(__name__)

boardercontrollers = {}

# 渲染前端的 HTML 页面
@app.route('/')
def index():
    return render_template('index.html')  # Flask 会自动在 templates 目录下寻找 index.html

# API 路由
@app.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    port = data.get('port')  # 获取 'port' 参数
    baudrate = data.get('baudrate')  # 获取 'baudrate' 参数
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", port, baudrate,boardtype)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           boardercontrollers["boardcontroller1"] = BoardController(BoardType.FIVE_AXIS, board_name="五轴控制板")

        if  boardercontrollers["boardcontroller1"].connected:
           print("已经连接到主板，无需重复连接")
           return jsonify({"status": "fail","message": "已经连接到主板，无需重复连接"}) 
        success =  boardercontrollers["boardcontroller1"].connect(port=port,baudrate=baudrate)

    if success :
        print("连接成功!")
        return jsonify({"status": "success","message": "连接成功!"})
    else:
        print("连接失败!")
        return jsonify({"status": "fail","message": "连接失败!"})
    

@app.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
    boardtype = data.get('boardtype')  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", boardtype)
    if boardtype == '1':
        if not boardercontrollers.get("boardcontroller1"):
           print("找不到主板控制器，无法操作")
           return jsonify({"status": "fail","message": "找不到主板控制器，无法操作"})    

        if not  boardercontrollers["boardcontroller1"].connected:
           print("已经断开，无需重复操作")
           return jsonify({"status": "fail","message": "已经断开，无需重复操作"})       
        success =  boardercontrollers["boardcontroller1"].disconnect()
    if success :
        print("断开连接成功!")
        return jsonify({"status": "success","message": "断开连接成功!"})
    else:
        print("断开连接失败!")
        return jsonify({"status": "fail","message": "断开连接失败!"})    

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




           
if __name__ == '__main__':
    # 绑定到所有网络接口，允许局域网访问,测试使用3000端口，实际生产使用5000端口
    app.run(debug=True, host='0.0.0.0', port=3000)
