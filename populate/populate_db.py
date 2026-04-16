import mysql.connector as mc
import random

# Database configuration
database_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '994694',
    'database': 'library',
    'connection_timeout': 5
}

TARGET_BOOKS_PER_USER = 100

def connect_():
    try:
        conn = mc.connect(**database_config)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def populate():
    conn = connect_()
    if not conn:
        return

    cursor = conn.cursor()

    # 1. Create 5 users
    users = [
        ('user_alice', 'pass_alice123', 'AliceInWonderland', '女'),
        ('user_bob', 'pass_bob456', 'BobTheBuilder', '男'),
        ('user_charlie', 'pass_charlie789', 'CharlieChaplin', '男'),
        ('user_diana', 'pass_diana321', 'WonderDiana', '女'),
        ('user_evan', 'pass_evan654', 'EvanAlmighty', '其他')
    ]

    created_users = []

    print("Creating users...")
    for username, password, nickname, gender in users:
        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing = cursor.fetchone()
            if existing:
                print(f"User {username} already exists, skipping creation.")
                created_users.append({'id': existing[0], 'username': username, 'password': password})
            else:
                cursor.execute(
                    "INSERT INTO users (username, password, nickname, gender) VALUES (%s, %s, %s, %s)",
                    (username, password, nickname, gender)
                )
                user_id = cursor.lastrowid
                created_users.append({'id': user_id, 'username': username, 'password': password})
                print(f"Created user: {username}")
        except Exception as e:
            print(f"Error creating user {username}: {e}")

    conn.commit()

    # 2. Create books for each user
    # We need at least 100 books per user.
    # Let's define some sample data to mix and match.
    
    titles_base = ["Python Programming", "The Art of Code", "Data Science 101", "History of Earth", "Space Travel", 
                   "Cooking Master", "Gardening Tips", "Mystery of the Blue Train", "Silent Hill", "Machine Learning"]
    authors = ["John Doe", "Jane Smith", "Alan Turing", "Grace Hopper", "Isaac Asimov", 
               "Agatha Christie", "Stephen King", "J.K. Rowling", "George Orwell", "Mark Twain"]
    publishers = ["Tech Press", "Science House", "Mystery Inc.", "Classic Books", "Future Reads"]
    types = ["Science", "Fiction", "History", "Technology", "Art", "Cooking"]
    
    print("Creating books...")
    for user in created_users:
        user_id = user['id']
        username = user['username']
        cursor.execute("SELECT COUNT(*) FROM books WHERE user_id=%s", (user_id,))
        current_count = cursor.fetchone()[0] or 0
        need = max(0, TARGET_BOOKS_PER_USER - current_count)
        if need == 0:
            print(f"User {username} already has {current_count} books, skipping.")
            continue
        books_data = []
        for i in range(need):
            title = f"{random.choice(titles_base)} Vol.{current_count + i + 1}"
            author = random.choice(authors)
            isbn = f"978-{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(0, 9)}"
            year = random.randint(1950, 2023)
            book_type = random.choice(types)
            publisher = random.choice(publishers)
            summary = f"This is a great book about {title} written by {author}. It covers many interesting topics."
            cover = ""
            books_data.append((user_id, title, author, isbn, year, book_type, publisher, summary, cover))
        try:
            cursor.executemany(
                """
                INSERT INTO books (user_id, title, author, isbn, year, `type`, publisher, summary, cover)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                books_data
            )
            print(f"Added {len(books_data)} books for user {username} (from {current_count} to {current_count + need})")
        except Exception as e:
            print(f"Error adding books for user {username}: {e}")

    conn.commit()
    print("Population complete.")

    print("\n" + "="*30)
    print("USER CREDENTIALS:")
    print("="*30)
    for u in created_users:
        print(f"Username: {u['username']}, Password: {u['password']}")
    print("\n" + "="*30)
    print("BOOK COUNTS:")
    print("="*30)
    for u in created_users:
        cursor.execute("SELECT COUNT(*) FROM books WHERE user_id=%s", (u['id'],))
        cnt = cursor.fetchone()[0]
        print(f"{u['username']}: {cnt}")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    populate()
