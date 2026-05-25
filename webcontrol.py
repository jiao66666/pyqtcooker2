# flaskcontrol.py
from flask import Flask, render_template, jsonify,request
from lib.newstructure.constant import *
from lib.newstructure.tools import is_dev_mode,apply_action_speed_override,get_pot_pos
import webview
import threading
from lib.newstructure.system import run_system,init_system,shutdown_system,set_system_dirty
from lib.newstructure.cookservice import cookservice
from lib.newstructure.system_runtime import system

#  2.0版本Flask Control WEB 后端服务控制程序
app = Flask(__name__)

# 根据传入的命令行参数设置端口,方便测试和生产环境使用不同的端口
if is_dev_mode():
    print("当前环境: 开发环境，使用测试端口")
    port = 3000
else:
    print("当前环境: 生产环境，使用生产端口")
    port = 5000

# 渲染前端的 HTML 页面
@app.route('/')
def index():
    return render_template('index.html')  # Flask 会自动在 templates 目录下寻找 index.html

# API 路由
@app.route('/connect', methods=['POST'])
def connect():
    print("start Enable Power")
    success=system["motorsmanager"].enable_all_motors()
    if success:
        print("使能成功!")
        return jsonify({"status": "success","message": "使能成功!"})
    else:
        print("使能失败!")
        return jsonify({"status": "fail","message": f"使能失败!"})
    
@app.route('/disconnect', methods=['POST'])

def disconnect():
    print("start STOP Enable Power")
    success=system["motorsmanager"].stop_all_motors()
    if success:
        print("关闭炒菜机成功!")
        return jsonify({"status": "success","message": "关闭炒菜机成功!"})
    else:
        print("关闭炒菜机失败!")
        return jsonify({"status": "fail","message": f"关闭炒菜机失败!"})

@app.route('/testtastboardping', methods=['POST'])
def testtastboardping():
    print("测试加料板连通性")
    success =  system["motors"]["feedermotor"][POT1_FLAVORMOTOR1].ping()
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
  
    success =  system["motors"]["feedermotor"][int(motorid)].run(int(overtime))
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

    success = system["motors"]["feedermotor"][int(motorid)].getfb(int(mode))
    if success :
        print("测试加料板打开成功!")
        return jsonify({"status": "success","message": f"运行获取反馈成功，反馈结果"})
    else:
        print("测试加料板打开失败!")
        return jsonify({"status": "fail","message": "运转失败!"})
    
@app.route('/runlong', methods=['POST'])
def runlong():
    print("运行电机长运转")
    data = request.get_json()
    motorid = data.get('motorid')  
    direction = data.get('direction')  
    speed = data.get('speed')  
    success = False
    print("收到参数 :", motorid, direction,speed)
    success =  cookservice.run_single_action(motorid,"runlong",{"speed":int(int(speed)*360),"direction":int(direction)})
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
    motorid = data.get('motorid')  
    direction = data.get('direction')  
    speed = data.get('speed')  
    circles = data.get('circle') 
    success = False
    print("收到参数 :", motorid, direction,speed)

    success =  cookservice.run_single_action(motorid,"run",{"circle":float(circles),"speed":int(int(speed)*360),"direction":int(direction)})
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
    motorid = data.get('motorid')  
    direction = data.get('direction')  
    speed = data.get('speed')  
    circles = data.get('circle') 
    success = False
    print("收到参数 :", motorid, direction,speed)
      
    success =  cookservice.run_single_action(motorid,"go",{"target":float(circles),"anglespeed":int(int(speed)*360)})
    currentpos = system["motors"]["stepmotor"][int(motorid)].get_current_pos()
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
    motorid = data.get('motorid') 
    success = False
    print("收到参数 :", motorid)

    success =  cookservice.run_control_cmd(motorid,"pause",{})
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
    motorid = data.get('motorid') 
    success = False
    print("收到参数 :", motorid)

    success = cookservice.run_control_cmd(motorid,"stop",{})
    if success :
        print("电机暂停成功!")
        return jsonify({"status": "success","message": "电机暂停成功!"})
    else:
        print("电机暂停失败!")
        return jsonify({"status": "fail","message": "电机暂停失败!"})    
    
@app.route('/stopall', methods=['POST'])
def stopall():
    print("所有电机急停")
    success1 = system["motorsmanager"].stop_all_motors()
    success2 = system["motorsmanager"].reset_home_all()
    set_system_dirty(system,True)
    if success1 and success2 :
        print("测试成功!")
        return jsonify({"status": "success","message": "急停所有电机成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "急停所有电机失败!"})
    
@app.route('/resetmotor', methods=['POST'])
def resetmotor():
    print("运行电机长运转")
    data = request.get_json()
    motorid = data.get('motorid')  
    direction = data.get('direction')  
    speed = data.get('speed')  
    success = False
    print("收到参数 :", motorid, direction,speed)

    success =  cookservice.run_single_action(motorid,"reset",{})
    if success :
        print("测试复位成功!")
        return jsonify({"status": "success","message": f"复位电机成功!电机：{motorid}，方向：{direction}"})
    else:
        print("测试复位失败!")
        return jsonify({"status": "fail","message": f"复位电机失败!,电机：{motorid}，错误信息"})

@app.route('/resetmotorpot', methods=['POST'])
def resetmotorpot():
    print("运行整体复位任务")
    data = request.get_json()
    potnum = int(data.get('potnum'))  # 获取 'boardtype' 参数
    success = False
    print("收到参数 :", potnum)

    action_param = "resetzero"
    pot_param = potnum
    print("run resetmotorpot action now.........")
    success = cookservice.run_task(action_param,pot_param)
    if success :
        print("测试复位成功!")
        return jsonify({"status": "success","message": f"复位电机成功!锅号：{potnum}"})
    else:
        print("测试复位失败!")
        return jsonify({"status": "fail","message": f"复位电机失败!,锅号：{potnum}，错误信息"})

@app.route('/testmultitaskabs', methods=['POST'])   #绝对位置任务测试
def testmultitaskabs():
    print("1号锅测试水平翻转任务开始")

    data = request.get_json()
    speed_level = data.get('speed_level') 
    speed_flip = data.get('speed_flip') 
   
    success = False
    #runtask参数：[圈数，速度，方向]
    print("**************************************1号锅测试水平翻转任务开始******************************")
    move_speed = int(speed_level)   
    flip_speed = int(speed_flip)    
    move_speed = max(360, min(move_speed, 3600))
    flip_speed = max(360, min(flip_speed, 3600))

    ####### 动态修改固定动作参数 #######
    apply_action_speed_override(
        "take_fire_pour",
        move_speed,
        flip_speed
    )
    action_param = "take_fire_pour"
    pot_param = 1
    print("simulate click....")
    success = cookservice.run_task(action_param,pot_param)
    print("**************************************1号锅测试水平翻转任务结束******************************")
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

    #runtask参数：[圈数，速度，方向]
    print("**************************************2号锅测试水平翻转任务开始******************************")
    move_speed = int(speed_level)   #2160  tested
    flip_speed = int(speed_flip)   #2520  tested 
    move_speed = max(360, min(move_speed, 3600))
    flip_speed = max(360, min(flip_speed, 3600))

    ####### 动态修改固定动作参数 #######
    apply_action_speed_override(
        "take_fire_pour",
        move_speed,
        flip_speed
    )
    action_param = "take_fire_pour"
    pot_param = 1
    print("simulate click....")
    success = cookservice.run_task(action_param,pot_param)
    print("**************************************2号锅测试水平翻转任务结束******************************")
    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})  

@app.route('/testdc_command', methods=['POST'])
def testdc_command():
    print("-------测试DC板开始------- ")
    data = request.get_json()
    dc_speed = data.get('dc_speed') 
    dc_time = data.get('dc_time') 
    command = data.get('command')    
    pot     = data.get('pot') 
    direction = data.get('direction') 

    success = False
    print(f"recv params {dc_speed},{dc_time},{command},{pot},{direction}") 
    print("收到参数:",dc_speed,dc_time,command,pot)
    
    if pot == 1:
       choosed_motor = POT1_SPIN_MOTOR
    else:
       choosed_motor = POT2_SPIN_MOTOR
       
    if command == "longrun":
        success =  system["motors"]["spinmotor"][choosed_motor].longrun(direction,dc_speed) 
    elif command == "run":
        success =  system["motors"]["spinmotor"][choosed_motor].run(direction,dc_time,dc_speed)   
    elif command == "stop":
        success =  system["motors"]["spinmotor"][choosed_motor].stop() 

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
    
    speed = speed * 360  # 转换为电机实际速度值
    speed = max(360, min(speed, 3600))

    success = False
    pos_info = get_pot_pos(potnum,postype)
    ####### 动态修改固定动作参数 #######
    apply_action_speed_override(
        "take_fire_pour",
        speed,
        speed,
        pos_info["level_pos"],
        pos_info["flip_pos"]
    )

    action_param = "go_to_potpos"
    pot_param = potnum
    success = cookservice.run_task(action_param,pot_param)
    
    if success :
        print("测试成功!")
        return jsonify({"status": "success","message": "测试成功!"})
    else:
        print("测试失败!")
        return jsonify({"status": "fail","message": "测试失败!"})    
    
#启动flask后端服务器WEB UI
def run_flask():
    app.run(
    host='0.0.0.0',   # 监听所有地址
    port=port,
    debug=False,       # 禁用调试模式
    use_reloader=False # 禁止自动重载
)

def start_server():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

#启动webview的Windows窗口控制UI
def start_webview():
    url = f"http://127.0.0.1:{port}"
    window=webview.create_window("炒菜机", url)
    window.events.closed += on_windows_close
    webview.start()

def on_windows_close():
    shutdown_system(system)

#启动炒菜机控制系统
def start_system():
    init_system()

    t = threading.Thread(
        target=lambda: run_system(system),
        daemon=True
    )
    t.start()

if __name__ == '__main__':
    start_server()
    start_system()
    start_webview()
