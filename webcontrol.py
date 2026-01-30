# flaskcontrol.py
from flask import Flask, render_template, jsonify,request
from lib.boardcontroller import BoardController
from lib.boardtype import BoardType


app = Flask(__name__)

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
    print("web connect port start...")  # 调用 machinecontrol.py 中的 start_motor 函数
    return jsonify({"message": "连接成功!","port":port,"baudrate":baudrate})

@app.route('/run', methods=['POST'])
def run():
    print("web run starting.....")  # 调用 machinecontrol.py 中的 stop_motor 函数
    return jsonify({"message": "Motor stopped!"})

if __name__ == '__main__':
    # 绑定到所有网络接口，允许局域网访问
    app.run(debug=True, host='0.0.0.0', port=5000)
