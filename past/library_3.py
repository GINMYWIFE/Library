'''
任务四：小型书籍管理系统（改进版）
基于原有任务三2.0，增加用户系统 + 书籍分页 + 独立书单 + 封面上传
'''

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector as mc
from mysql.connector import Error
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 【新增】Session密钥
UPLOAD_FOLDER = 'static/covers'     # 【新增】封面文件路径
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

database_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '994694',
    'database': 'library'
}

# 连接数据库
def connect_():
    try:
        conn = mc.connect(**database_config)
        return conn
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def initialize_database():
    conn = connect_()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # 【修改】增加 users 表 与 books 表外键
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nickname VARCHAR(100),
                gender ENUM('男', '女', '其他') DEFAULT '其他'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                publisher VARCHAR(255),
                summary TEXT,
                cover VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        return True
    except Error as error:
        print(f"数据库初始化失败: {error}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/')
def index():
    return render_template('login.html')  # 【修改】主页改为登录页面

@app.route('/login', methods=['POST'])
def login():
    # 【新增】用户登录逻辑
    username = request.form['username']
    password = request.form['password']

    conn = connect_()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, nickname, gender FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and user[1] == password:
        session['user_id'] = user[0]
        session['nickname'] = user[2]
        session['gender'] = user[3]
        return redirect(url_for('books_page'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # 【新增】退出登录
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/update', methods=['POST'])
def update_user():
    # 【新增】修改昵称、性别、密码
    user_id = session.get('user_id')
    nickname = request.form.get('nickname')
    gender = request.form.get('gender')
    password = request.form.get('password')

    conn = connect_()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET nickname=%s, gender=%s, password=%s WHERE id=%s
    """, (nickname, gender, password, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    session['nickname'] = nickname
    session['gender'] = gender
    return jsonify({'message': '用户信息更新成功'})


@app.route('/upload_cover', methods=['POST'])#上传封面文件
def upload_cover():
    # 【新增】上传封面文件
    file = request.files['cover']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return jsonify({'path': '/' + filepath})


@app.route('/books')
def books_page():
    # 【新增】主书籍页面
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('books.html', nickname=session['nickname'], gender=session['gender'])


# API：书籍列表（分页+搜索）
@app.route('/api/books', methods=['GET'])
def get_books():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', '')
    limit = 20
    offset = (page - 1) * limit

    conn = connect_()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM books 
        WHERE user_id=%s AND (title LIKE %s OR summary LIKE %s)
        LIMIT %s OFFSET %s
    """, (session['user_id'], f'%{keyword}%', f'%{keyword}%', limit, offset))
    books = cursor.fetchall()

    book_list = []
    for b in books:
        book_list.append({
            'id': b[0],
            'title': b[2],
            'author': b[3],
            'publisher': b[4],
            'summary': b[5],
            'cover': b[6]
        })

    cursor.close()
    conn.close()
    return jsonify(book_list)

# API：添加书籍
@app.route('/api/books', methods=['POST'])
def add_book():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    data = request.get_json()
    conn = connect_()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (user_id, title, author, publisher, summary, cover)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session['user_id'], data['title'], data['author'], data.get('publisher', ''),
          data.get('summary', ''), data.get('cover', '')))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': '添加成功'})

# API：修改 & 删除书籍
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    data = request.get_json()
    conn = connect_()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE books SET title=%s, author=%s, publisher=%s, summary=%s, cover=%s
        WHERE id=%s AND user_id=%s
    """, (data['title'], data['author'], data['publisher'], data['summary'],
          data['cover'], book_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': '更新成功'})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    conn = connect_()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s AND user_id=%s", (book_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': '删除成功'})

# 启动应用
if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
