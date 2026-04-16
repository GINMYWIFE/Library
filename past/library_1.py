'''任务一初版1.0'''

import mysql.connector as mc
from mysql.connector import Error
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '994694', 
    'database': 'library' 
}
def dis_w (s): #计算字符串长度
    if not s:
        return 0
    width = 0
    for char in s:
        #是否为中文字符
        if '\u4e00' <= char <= '\u9fff':
            width += 2
        else:
            width += 1
    return width
def connect(): #连接数据库
    try:
        conn = mc.connect(**config)
        return conn
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def create():
    conn=connect()
    if conn is None:
        print("无法连接到数据库")
        return False
    try:
        cursor = conn.cursor()#创建游标
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                isbn VARCHAR(20) UNIQUE,
                year YEAR,#4/2位格式，00~69->2000~2069，70~99->1970~1999
                type VARCHAR(100)
            )
        """)
        conn.commit()
        return True
    except Error as e:
        print(f"创建失败: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def add(title, author, isbn=None, year=None, type=None):
    conn = connect()
    if conn is None:
        print("无法连接到数据库")
        return False
    try:    
        cursor = conn.cursor()
        sql = """
            INSERT INTO books (title, author, isbn, year, type) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (title, author, isbn, year, type))#执行SQL语句
        conn.commit()
        return True
    except Error as e:
        print(f"添加失败: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def refer(): #查询所有图书记录
    conn=connect()
    if conn is None:
        print("无法连接到数据库")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall() 
        return books
    except Error as e:
        print(f"查询失败: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def ref_id(id):
    conn=connect()
    if conn is None:
        print("无法连接到数据库")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
        book = cursor.fetchone()
        return book
    except Error as e:
        print(f"查询失败: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def upd_id(id, title=None, author=None, isbn=None, year=None, type=None):
    conn=connect()
    if conn is None:
        print("无法连接到数据库")
        return False
    upd=[]#更新内容
    para=[]#参数
    if title is not None:
        upd.append("title = %s")
        para.append(title)
    if author is not None:
        upd.append("author = %s")
        para.append(author)
    if isbn is not None:
        upd.append("isbn = %s")
        para.append(isbn)
    if year is not None:
        upd.append("year = %s")
        para.append(year)
    if type is not None:
        upd.append("type = %s")
        para.append(type)

    if not upd:
        print("没有更新信息")
        return False
    sql = f"UPDATE books SET " + ", ".join(upd) + " WHERE id = %s"
    para.append(id)

    try:
        cursor = conn.cursor()
        cursor.execute(sql, para)
        conn.commit()
        if cursor.rowcount > 0:
            print(f"成功更新图书")
            return True
        else:
            print(f"未找到图书，更新失败")
            return False
    except Error as e:
        print(f"更新失败: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def delete(id):
    conn=connect()
    if conn is None:
        print("无法连接到数据库")
        return False
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM books WHERE id = %s"
        cursor.execute(sql, (id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"成功删除图书ID {id}")
            return True
        else:
            print(f"未找到图书ID {id}，删除失败")
            return False
    except Error as e:
        print(f"删除失败: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def menu():
    print("图书管理系统")
    print("1. 添加图书")
    print("2. 查询所有图书")
    print("3. 查询图书")
    print("4. 更新图书")
    print("5. 删除图书")
    print("6. 退出")

def view():
    print("\n--- 所有图书信息 ---")
    books = refer()
    if books:
        id_w=5
        title_w=30
        author_w=20
        isbn_w=15
        year_w=10
        type_w=15
        header=f"{'ID':<{id_w}} {'书名':<{title_w}} {'作者':<{author_w}} {'ISBN':<{isbn_w}} {'出版年份':<{year_w}} {'类型':<{type_w}}"
        print(header)
        print("-" * (id_w + title_w + author_w + isbn_w + year_w + type_w + 5))
        for book in books:
            book_id_str = str(book[0])
            title_str = book[1] or 'N/A'
            author_str = book[2] or 'N/A'
            isbn_str = book[3] or 'N/A'
            year_str = str(book[4]) if book[4] else 'N/A'
            type_str = book[5] or 'N/A'

            def pad_to_width(s, width):
                current_width = dis_w(s)
                if current_width >= width:
                    return s
                else:
                    return s + ' ' * (width - current_width)
            
            padded_id = pad_to_width(book_id_str, id_w)
            padded_title = pad_to_width(title_str, title_w)
            padded_author = pad_to_width(author_str, author_w)
            padded_isbn = pad_to_width(isbn_str, isbn_w)
            padded_year = pad_to_width(year_str, year_w)
            padded_type = pad_to_width(type_str, type_w)

            print(f"{padded_id} {padded_title} {padded_author} {padded_isbn} {padded_year} {padded_type}")

    else:
        print("暂无图书信息")

def hadd():
    title = input("请输入图书名称：")
    if title == "":
        print("请输入图书名称")
        return False

    author = input("请输入作者：")
    if author == "":
        print("请输入作者")
        return False

    isbn = input("请输入ISBN：")
    if isbn == "":
        print("请输入ISBN")
        return False

    year = input("请输入出版年份：")
    if year == "":
        print("请输入出版年份")
        return False

    type = input("请输入图书类型：")
    if type == "":
        print("请输入图书类型")
        return False

    if add(title, author, isbn, year, type):
        print("添加成功")
        return True
    else:
        print("添加失败")
        return False

def search():
    id = input("请输入图书ID：")
    if id == "":
        print("请输入图书ID")
        return False
    book = ref_id(id)
    if book:
        print(f"图书ID：{book[0]}")
        print(f"书名：{book[1]}")
        print(f"作者：{book[2]}")
        print(f"ISBN：{book[3]}")
        print(f"出版年份：{book[4]}")
        print(f"类型：{book[5]}")
        return True
    
def update():
    id = input("请输入图书ID：")
    if id == "":
        print("请输入图书ID")
        return False
    book = ref_id(id)
    if book:
        title = input(f"请输入图书名称（当前：{book[1]}）：")
        if title == "":
            title = book[1]

        author = input(f"请输入作者（当前：{book[2]}）：")
        if author == "":
            author = book[2]

        isbn = input(f"请输入ISBN（当前：{book[3]}）：")
        if isbn == "":
            isbn = book[3]

        year = input(f"请输入出版年份（当前：{book[4]}）：")
        if year == "":
            year = book[4]

        type = input(f"请输入图书类型（当前：{book[5]}）：")
        if type == "":
            type = book[5]

        if update(id, title, author, isbn, year, type):
            print("更新成功")
            return True
        else:
            print("更新失败")
            return False

def del_book():
    id = input("请输入图书ID：")
    if id == "":
        print("请输入图书ID")
        return False
    if delete(id):
        print("删除成功")
        return True
    else:
        print("删除失败")
        return False

if __name__ == "__main__":
    while True:
        menu()
        choice = input("请选择操作：")
        if choice == "1":
            if hadd():
                view()
        elif choice == "2":
            view()
        elif choice == "3":
            search()
        elif choice == "4":
            update()
        elif choice == "5":
            del_book()
        elif choice == "6":
            print("感谢使用，再见!")
            break
        else:
            print("请输入 1 到 6 之间的数字。")
