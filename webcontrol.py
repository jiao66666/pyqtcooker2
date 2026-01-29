# flaskcontrol.py
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# 渲染前端的 HTML 页面
@app.route('/')
def index():
    return render_template('index.html')  # Flask 会自动在 templates 目录下寻找 index.html

# API 路由
@app.route('/start_motor')
def run():
    print("run motor")  # 调用 machinecontrol.py 中的 start_motor 函数
    return jsonify({"message": "Motor runned!"})

@app.route('/stop_motor')
def stop():
    print("stop motor")  # 调用 machinecontrol.py 中的 stop_motor 函数
    return jsonify({"message": "Motor stopped!"})

if __name__ == '__main__':
    # 绑定到所有网络接口，允许局域网访问
    app.run(debug=True, host='0.0.0.0', port=5000)
