# test_socket.py
import socket

def test_bind(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
        print(f"✅ 成功绑定到 127.0.0.1:{port}")
        sock.close()
        return True
    except OSError as e:
        print(f"❌ 绑定失败 (端口 {port}): {e}")
        return False

if __name__ == '__main__':
    for p in [5001, 5000, 8000, 8080, 9000]:
        test_bind(p)
        '''❌ 绑定失败 (端口 9000): [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。
        连原生 socket 都无法绑定，那 100% 是系统/安全软件问题，不是 Flask 的锅。'''