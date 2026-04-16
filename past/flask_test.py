from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Flask is working!"

if __name__ == '__main__':
    print("尝试在 8000 端口启动...")
    app.run(host='127.0.0.1', port=8000)
    ''' 如果这个也报同样错误 → 说明是系统级网络权限问题，与你的代码无关'''