"""
基于Flask和MySQL的Web图书管理系统,支持图书的增删改查操作。
图书管理系统Web应用启动脚本
启动前先启动MySQL服务
终端输入mysql -u root -p 
运行此脚本启动Web服务器
访问地址: http://localhost:5000
按 Ctrl+C 停止服务器
"""
import os
import sys
from library_3 import app, initialize_database
def main():
    print("正在初始化数据库...")
    if initialize_database():
        print("数据库初始化成功")
    else:
        print("数据库初始化失败,请检查MySQL服务是否启动")
        return
    try:
        # 启动Flask应用
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n网站已关闭")
    except Exception as error:
        print(f"\n启动失败: {error}")

if __name__ == '__main__':
    main()