# flaskcontrol.py
from flask import Flask, render_template, jsonify,request, g
from lib.boardcontroller import BoardController
from lib.boardtype import BoardType

app = Flask(__name__)
# 在请求处理过程中使用 g 对象存储 boardcontroller1
@app.before_request
def before_request():
    # 假设 boardcontroller1 和 boardcontroller2 需要在请求开始时创建
    if not hasattr(g, 'boardcontroller1'):
        g.boardcontroller1 = None
    if not hasattr(g, 'boardcontroller2'):
        g.boardcontroller2 = None


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
        if not g.boardcontroller1:
           g.boardcontroller1 = BoardController(BoardType.FIVE_AXIS, board_name="五轴控制板")

        if g.boardcontroller1.connected:
           print("已经连接到主板，无需重复连接")
           return   
        success = g.boardcontroller1.connect(port=port,baudrate=baudrate)

    if success :
        print("连接成功!")
        return jsonify({"status": "success","message": "连接成功!"})
    else:
        print("连接失败!")
        return jsonify({"status": "fail","message": "连接失败!"})

@app.route('/run', methods=['POST'])
def run():
    print("web run starting.....")  # 调用 machinecontrol.py 中的 stop_motor 函数
    return jsonify({"message": "Motor stopped!"})

if __name__ == '__main__':
    # 绑定到所有网络接口，允许局域网访问
    app.run(debug=True, host='0.0.0.0', port=5000)
