'''
任务三2.0
Flask 应用程序&&路由&&数据库连接
'''

from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector as mc
from mysql.connector import Error
import json
app = Flask(__name__)#创建一个Flask应用实例
database_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '994694', 
    'database': 'library' 
}
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                isbn VARCHAR(20) UNIQUE,
                year YEAR,
                type VARCHAR(100)
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

@app.route('/')#主路由
def index():
    return render_template('index.html')#返回index.html模板

@app.route('/api/books', methods=['GET'])#获取所有图书信息的API接口路由
def get_all_books():
    conn = connect_()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY id")
        books = cursor.fetchall()
        
        # 将查询结果转换为字典格式
        book_list = []
        for book in books:
            book_dict = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'isbn': book[3],
                'year': book[4],
                'type': book[5]
            }
            book_list.append(book_dict)
        
        return jsonify(book_list)
    except Error as error:
        return jsonify({'error': f'查询失败: {error}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/books/search', methods=['GET']) #搜索图书的API接口路由
def search_books():
    search_type = request.args.get('type', 'all')  # 搜索类型：id, title, author, isbn, year, type, all
    search_value = request.args.get('value', '').strip()  # 搜索值
    
    if not search_value:
        return jsonify({'error': '请输入搜索内容'}), 400
    
    conn = connect_()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        #搜索图书
        if search_type == 'id':
            try:
                book_id = int(search_value)
                cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            except ValueError:
                return jsonify({'error': 'ID必须是数字'}), 400
        elif search_type == 'title':
            cursor.execute("SELECT * FROM books WHERE title LIKE %s ORDER BY id", (f'%{search_value}%',))
        elif search_type == 'author':
            cursor.execute("SELECT * FROM books WHERE author LIKE %s ORDER BY id", (f'%{search_value}%',))
        elif search_type == 'isbn':
            cursor.execute("SELECT * FROM books WHERE isbn = %s", (search_value,))
        elif search_type == 'year':
            try:
                year_value = int(search_value)
                cursor.execute("SELECT * FROM books WHERE year = %s ORDER BY id", (year_value,))
            except ValueError:
                return jsonify({'error': '年份必须是数字'}), 400
        elif search_type == 'type':
            cursor.execute("SELECT * FROM books WHERE type LIKE %s ORDER BY id", (f'%{search_value}%',))
        else:
            # 全文搜索 - 在所有字段中搜索
            search_pattern = f'%{search_value}%'
            cursor.execute("""
                SELECT * FROM books 
                WHERE title LIKE %s 
                   OR author LIKE %s 
                   OR isbn LIKE %s 
                   OR type LIKE %s 
                   OR CAST(year AS CHAR) LIKE %s
                ORDER BY id
            """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        books = cursor.fetchall()#获取所有结果
        book_list = []
        for book in books:
            book_dict = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'isbn': book[3],
                'year': book[4],
                'type': book[5]
            }
            book_list.append(book_dict)
        #返回结果
        return jsonify({
            'books': book_list,
            'count': len(book_list),
            'search_type': search_type,
            'search_value': search_value
        })
    except Error as error:
        return jsonify({'error': f'搜索失败: {error}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/books', methods=['POST'])#添加图书
def add_book():
    data = request.get_json()
    # 验证必填字段
    if not data.get('title') or not data.get('author'):
        return jsonify({'error': '书名和作者为必填项'}), 400
    
    conn = connect_()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO books (title, author, isbn, year, type) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('title'),
            data.get('author'),
            data.get('isbn'),
            data.get('year'),
            data.get('type')
        ))
        conn.commit()
        
        return jsonify({'message': '图书添加成功', 'id': cursor.lastrowid}), 201
    except Error as error:
        return jsonify({'error': f'添加失败: {error}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/books/<int:book_id>', methods=['PUT'])#更新图书
def update_book(book_id):
    data = request.get_json()
    
    conn = connect_()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        # 动态更新SQL语句
        update_fields = []
        parameters = []
        
        if 'title' in data:
            update_fields.append("title = %s")
            parameters.append(data['title'])
        if 'author' in data:
            update_fields.append("author = %s")
            parameters.append(data['author'])
        if 'isbn' in data:
            update_fields.append("isbn = %s")
            parameters.append(data['isbn'])
        if 'year' in data:
            update_fields.append("year = %s")
            parameters.append(data['year'])
        if 'type' in data:
            update_fields.append("type = %s")
            parameters.append(data['type'])
        
        if not update_fields:
            return jsonify({'error': '没有提供更新信息'}), 400
        
        sql = f"UPDATE books SET {', '.join(update_fields)} WHERE id = %s"
        parameters.append(book_id)
        
        cursor.execute(sql, parameters)
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'message': '图书更新成功'})
        else:
            return jsonify({'error': '图书不存在'}), 404
    except Error as error:
        return jsonify({'error': f'更新失败: {error}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/books/<int:book_id>', methods=['DELETE'])#删除图书
def delete_book(book_id):
    conn = connect_()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'message': '图书删除成功'})
        else:
            return jsonify({'error': '图书不存在'}), 404
    except Error as error:
        return jsonify({'error': f'删除失败: {error}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, host='0.0.0.0', port=5000)#启动Flask应用