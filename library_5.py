'''
店长admin，admin
店员staff，staff
store_index.html
购书者aice，1；a，1
'''

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import mysql.connector as mc
from mysql.connector import Error
import os
import datetime
import random
import uuid
from werkzeug.utils import secure_filename

# 创建Flask应用实例
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'bookstore_secret_key'
UPLOAD_FOLDER = 'static/covers'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 数据库配置
database_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '994694',
    'database': 'library', 
    'connection_timeout': 5
}

# 数据库连接
def connect_():
    try:
        conn = mc.connect(**database_config)
        return conn
    except Error as e:
        print(f"Database connection failed: {e}")
        return None

# 初始化数据库
def initialize_database():
    conn = connect_()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        
        # 临时禁用外键约束检查
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        #创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,   
                nickname VARCHAR(100),
                gender ENUM('男', '女', '其他') DEFAULT '其他',
                role ENUM('customer', 'staff', 'manager') DEFAULT 'customer',
                balance DECIMAL(10, 2) DEFAULT 0.00
            )
        """)
        
        # 检查，如果没有 role 和 balance 列，则添加
        cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN role ENUM('customer', 'staff', 'manager') DEFAULT 'customer'")
            cursor.execute("ALTER TABLE users ADD COLUMN balance DECIMAL(10, 2) DEFAULT 0.00")

        #books表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                publisher VARCHAR(255),
                summary TEXT,
                cover VARCHAR(255),
                isbn VARCHAR(20),
                year INT,
                type VARCHAR(50),
                price DECIMAL(10, 2) DEFAULT 0.00,
                stock INT DEFAULT 0,
                status ENUM('on_shelf', 'off_shelf') DEFAULT 'on_shelf'
            )
        """)
         
        cursor.execute("SHOW COLUMNS FROM books LIKE 'price'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE books ADD COLUMN price DECIMAL(10, 2) DEFAULT 0.00")
            cursor.execute("ALTER TABLE books ADD COLUMN stock INT DEFAULT 10")
            cursor.execute("ALTER TABLE books ADD COLUMN status ENUM('on_shelf', 'off_shelf') DEFAULT 'on_shelf'")
            try:
                cursor.execute("ALTER TABLE books MODIFY user_id INT NULL")
            except:
                pass #用户id列不存在则跳过

        # Orders表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                status ENUM('pending', 'approved', 'shipped', 'completed', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 关联用户（user_id 外键引用 users.id）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                book_id INT NOT NULL,
                quantity INT NOT NULL,
                price_snapshot DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """)

        #创建店长账号
        cursor.execute("SELECT id FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, nickname, role, balance) VALUES (%s, %s, %s, %s, %s)",
                           ('admin', 'admin', '店长', 'manager', 0.00))
        else:
            # Ensure admin has manager role
            cursor.execute("UPDATE users SET role='manager' WHERE username='admin'")
        #创建店员账号
        cursor.execute("SELECT id FROM users WHERE username='staff'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, nickname, role, balance) VALUES (%s, %s, %s, %s, %s)",
                           ('staff', 'staff', '店员', 'staff', 0.00))
        else:
            cursor.execute("UPDATE users SET role='staff' WHERE username='staff'")

        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()
        return True
    except Error as error:
        print(f"Database init failed: {error}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# 路由定义
# 主页路由，返回商店首页
@app.route('/')
def index():
    return send_from_directory('templates', 'store_index.html')

# 静态文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 获取当前会话信息
@app.route('/api/session', methods=['GET'])
def get_session():
    #从 Flask 的 session（基于加密 cookie 的会话机制）中尝试获取 user_id。
    #如果用户已登录，通常在登录时会将 user_id 存入 session；否则为 None。
    user_id = session.get('user_id')
    if user_id:
        conn = connect_()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT balance FROM users WHERE id=%s", (user_id,))
                db_user = cursor.fetchone()
                balance = float(db_user['balance']) if db_user else 0.00
                cursor.close()
            except:
                balance = float(session.get('balance', 0.00))
            finally:
                conn.close()
        else:
            balance = float(session.get('balance', 0.00))
    else:
        balance = 0.00
    
    user = {
        'id': user_id,
        'username': session.get('username'),
        'nickname': session.get('nickname'),
        'role': session.get('role', 'guest'),
        'balance': balance
    }
    return jsonify(user)

# 用户登录
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = connect_()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and user['password'] == password:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['nickname'] = user['nickname']
        session['role'] = user['role']
        session['balance'] = float(user['balance'])
        return jsonify({'message': 'Login successful', 'role': user['role']})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# 用户登出
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

# 用户注册
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    nickname = data.get('nickname')
    gender = data.get('gender', '其他')
    
    #虚拟币随机100-1000
    initial_balance = random.randint(100, 1000)

    conn = connect_()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, nickname, gender, role, balance) VALUES (%s, %s, %s, %s, 'customer', %s)",
                       (username, password, nickname, gender, initial_balance))
        conn.commit()
        return jsonify({'message': 'Registration successful', 'balance': initial_balance})
    except Error as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

# 产品API
# 获取图书列表，支持分页和搜索
@app.route('/api/books', methods=['GET'])
def get_books():
    role = session.get('role', 'guest')
    page = int(request.args.get('page', 1))
    limit = 20 #每页20本书
    offset = (page - 1) * limit
    
    search_type = request.args.get('searchType', 'all')#全字段搜索
    keyword = request.args.get('keyword', '')

    conn = connect_()
    cursor = conn.cursor(dictionary=True)
    
    where_clauses = []  #动态构建 SQL 的 WHERE 条件
    params = [] #存储 SQL 查询中的参数（防止 SQL 注入）
    
    if role not in ['staff', 'manager']:
        where_clauses.append("status = 'on_shelf'")
    
    if keyword:
        if search_type == 'all':
            where_clauses.append("(title LIKE %s OR author LIKE %s OR isbn LIKE %s)")
            like = f"%{keyword}%"
            params.extend([like, like, like])
        else:
            where_clauses.append(f"{search_type} LIKE %s")
            params.append(f"%{keyword}%")

    #将所有 WHERE 条件用 AND 连接
    #如果没有条件（如 guest 且无搜索），则使用 "1=1" 作为恒真条件
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    #分页
    cursor.execute(f"SELECT COUNT(*) as total FROM books WHERE {where_sql}", params)
    total = cursor.fetchone()['total']#总记录数

    cursor.execute(f"SELECT * FROM books WHERE {where_sql} ORDER BY id DESC LIMIT %s OFFSET %s", (*params, limit, offset))
    books = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'books': books,
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit
    })

# 添加图书（店员和店长）
@app.route('/api/books', methods=['POST'])
def add_book():
    if session.get('role') not in ['staff', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Handle file upload
    cover_filename = None
    if 'cover' in request.files:
        file = request.files['cover']
        if file and file.filename:
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                cover_filename = filename
            except Exception as e:
                return jsonify({'error': f'File upload failed: {str(e)}'}), 500
    
    data = request.form
    conn = connect_()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO books (title, author, publisher, isbn, year, type, price, stock, status, summary, cover)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['title'], data['author'], data.get('publisher'), data.get('isbn'), 
            data.get('year'), data.get('type'), data.get('price', 0), data.get('stock', 0),
            data.get('status', 'on_shelf'), data.get('summary'), cover_filename
        ))
        conn.commit()
        return jsonify({'message': 'Book added'})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 更新图书信息（仅店员和管理者）
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    if session.get('role') not in ['staff', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # 上传封面
    cover_filename = None
    if 'cover' in request.files:
        file = request.files['cover']
        if file and file.filename:
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                cover_filename = filename
            except Exception as e:
                return jsonify({'error': f'File upload failed: {str(e)}'}), 500
    
    data = request.form
    conn = connect_()
    cursor = conn.cursor()
    try:
        update_fields = []
        params = []
        
        fields = ['title', 'author', 'price', 'stock', 'status', 'summary']
        for field in fields:
            if field in data:
                update_fields.append(f"{field}=%s")
                params.append(data[field])
        
        if cover_filename:
            update_fields.append("cover=%s")
            params.append(cover_filename)
        
        if update_fields:
            params.append(book_id)
            cursor.execute(f"""
                UPDATE books SET {', '.join(update_fields)}
                WHERE id=%s
            """, params)
        
        conn.commit()
        return jsonify({'message': 'Book updated'})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# 购物车API
# 获取购物车内容
@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', {}) # 购物车存储在 session 中，格式为 {book_id: quantity}
    if not cart:
        return jsonify({'items': [], 'total': 0})
    
    book_ids = list(cart.keys())
    if not book_ids:
        return jsonify({'items': [], 'total': 0})
        
    conn = connect_()
    cursor = conn.cursor(dictionary=True)
    format_strings = ','.join(['%s'] * len(book_ids))
    cursor.execute(f"SELECT * FROM books WHERE id IN ({format_strings})", tuple(book_ids))
    books = cursor.fetchall()
    conn.close()
    
    items = []
    total = 0
    for book in books:
        qty = cart[str(book['id'])]
        item_total = float(book['price']) * qty
        total += item_total
        items.append({
            'book': book,
            'quantity': qty,
            'item_total': item_total
        })
        
    return jsonify({'items': items, 'total': total})

# 添加商品到购物车
@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    book_id = str(data.get('book_id'))
    quantity = int(data.get('quantity', 1))
    
    cart = session.get('cart', {})
    if book_id in cart:
        cart[book_id] += quantity
    else:
        cart[book_id] = quantity
    session['cart'] = cart
    return jsonify({'message': 'Added to cart', 'cart_count': sum(cart.values())})

# 更新购物车商品数量
@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.get_json()
    book_id = str(data.get('book_id'))
    quantity = int(data.get('quantity', 0))
    
    cart = session.get('cart', {})
    if quantity <= 0:
        if book_id in cart:
            del cart[book_id]
    else:
        cart[book_id] = quantity
    session['cart'] = cart
    return jsonify({'message': 'Cart updated'})

# 清空购物车
@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    return jsonify({'message': 'Cart cleared'})


# 订单API
# 创建订单
@app.route('/api/orders', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to checkout'}), 401
    
    user_id = session['user_id']
    user_role = session.get('role', 'customer')
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
        
    conn = connect_()
    cursor = conn.cursor(dictionary=True)
    
    try:
        conn.start_transaction()
        
        # 1.计算总价并检查库存
        total_price = 0
        order_items = []
        
        for book_id_str, qty in cart.items():
            book_id = int(book_id_str)
            cursor.execute("SELECT * FROM books WHERE id=%s FOR UPDATE", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                raise Exception(f"Book ID {book_id} not found")
            if book['stock'] < qty:
                raise Exception(f"Insufficient stock for {book['title']}")
                
            price = float(book['price'])
            item_total = price * qty
            total_price += item_total
            order_items.append((book_id, qty, price))
            
            # 扣减库存
            cursor.execute("UPDATE books SET stock = stock - %s WHERE id = %s", (qty, book_id))
            
        # 2. 检查用户余额（店员和管理者跳过）
        if user_role not in ['staff', 'manager']:
            cursor.execute("SELECT balance FROM users WHERE id=%s FOR UPDATE", (user_id,))
            user = cursor.fetchone()
            if float(user['balance']) < total_price:
                raise Exception("Insufficient balance")
                
            # 3. 扣减余额
            cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (total_price, user_id))
            session['balance'] = float(user['balance']) - total_price # Update session
        else:
            # 对于店员/管理者，不检查/扣减余额
            pass
        
        # 4. 创建订单
        cursor.execute("INSERT INTO orders (user_id, total_price, status) VALUES (%s, %s, 'pending')", (user_id, total_price))
        order_id = cursor.lastrowid
        
        # 5. 创建订单项
        for item in order_items:
            cursor.execute("INSERT INTO order_items (order_id, book_id, quantity, price_snapshot) VALUES (%s, %s, %s, %s)",
                           (order_id, item[0], item[1], item[2]))
                           
        conn.commit()
        session['cart'] = {} # Clear cart
        return jsonify({'message': 'Order placed successfully', 'order_id': order_id})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

# 获取订单列表
@app.route('/api/orders', methods=['GET'])
def get_orders():
    user_id = session.get('user_id')
    role = session.get('role', 'guest')
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = connect_()
    cursor = conn.cursor(dictionary=True)
    
    if role in ['staff', 'manager']:
        #店员和店长可查看所有订单，支持状态过滤
        status = request.args.get('status')
        if status:
            cursor.execute("SELECT orders.*, users.username FROM orders JOIN users ON orders.user_id = users.id WHERE status=%s ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT orders.*, users.username FROM orders JOIN users ON orders.user_id = users.id ORDER BY created_at DESC")
    else:
        #订单仅限客户自己查看
        cursor.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
        
    orders = cursor.fetchall()
    
    # 获取订单详情
    for order in orders:
        cursor.execute("""
            SELECT oi.*, b.title, b.cover 
            FROM order_items oi 
            JOIN books b ON oi.book_id = b.id 
            WHERE oi.order_id = %s
        """, (order['id'],))
        order['items'] = cursor.fetchall()
        
    conn.close()
    return jsonify(orders)

# 审核订单（批准、发货、取消）
@app.route('/api/orders/<int:order_id>/audit', methods=['POST'])
def audit_order(order_id):
    user_id = session.get('user_id')
    role = session.get('role', 'guest')
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    new_status = data.get('status') # 'approved', 'shipped', 'cancelled'
    
    print(f"Audit order {order_id} to {new_status} by user {user_id} role {role}")
    
    conn = None
    try:
        conn = connect_()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # 获取订单信息
        cursor.execute("SELECT user_id, total_price, status FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        old_status = order['status']
        order_user_id = order['user_id']
        total_price = float(order['total_price'] or 0)
        
        #用户可以取消订单
        if role not in ['staff', 'manager']:
            if order_user_id != user_id or new_status != 'cancelled':
                return jsonify({'error': 'Unauthorized'}), 403
        
        #发货订单不可取消
        if new_status == 'cancelled':
            if old_status == 'shipped':
                return jsonify({'error': '已发货订单不能取消'}), 400
        
        # 订单取消处理
        if new_status == 'cancelled' and old_status != 'cancelled':
            cursor.execute("SELECT role FROM users WHERE id=%s", (order_user_id,))
            user = cursor.fetchone()
            if user and user['role'] == 'customer':  #退款
                cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (total_price, order_user_id))
            
            # 恢复库存
            cursor.execute("SELECT book_id, quantity FROM order_items WHERE order_id=%s", (order_id,))
            items = cursor.fetchall()
            for item in items:
                cursor.execute("UPDATE books SET stock = stock + %s WHERE id = %s", (item['quantity'], item['book_id']))
        
        cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (new_status, order_id))
        conn.commit()
        return jsonify({'message': f'Order status updated to {new_status}'})
    
    except Exception as e:
        print(f"Error in audit_order: {str(e)}")
        return jsonify({'error': f'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

# 统计信息
@app.route('/api/stats', methods=['GET'])
def get_stats():
    if session.get('role') != 'manager':
        return jsonify({'error': 'Unauthorized'}), 403
        
    conn = connect_()
    cursor = conn.cursor(dictionary=True)
    
    # 今日订单数
    today = datetime.date.today()
    cursor.execute("SELECT COUNT(*) as count, SUM(total_price) as total FROM orders WHERE DATE(created_at) = %s AND status != 'cancelled'", (today,))
    daily_sales = cursor.fetchone()
    
    # 总订单数
    cursor.execute("SELECT COUNT(*) as count, SUM(total_price) as total FROM orders WHERE status != 'cancelled'")
    total_sales = cursor.fetchone()
    
   #查询销量前5的图书
    cursor.execute("""
        SELECT b.title, SUM(oi.quantity) as sold_count
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY b.id
        ORDER BY sold_count DESC
        LIMIT 5
    """)
    top_books = cursor.fetchall()
    
    conn.close()
    return jsonify({
        'daily': daily_sales,
        'total': total_sales,
        'top_books': top_books
    })

# 主程序入口
if __name__ == '__main__':
    initialize_database()
    app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
