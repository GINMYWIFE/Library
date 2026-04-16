import mysql.connector as mc
import random
from library_5 import initialize_database

# Configuration
database_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '994694',
    'database': 'library',
    'connection_timeout': 5
}

def connect_():
    try:
        conn = mc.connect(**database_config)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

# A list of real books to satisfy the requirement
REAL_BOOKS = [
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", "Grand Central Publishing"),
    ("1984", "George Orwell", "Science Fiction", "Signet Classic"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Scribner"),
    ("Pride and Prejudice", "Jane Austen", "Romance", "Penguin Classics"),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "Little, Brown and Company"),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "Houghton Mifflin Harcourt"),
    ("Fahrenheit 451", "Ray Bradbury", "Science Fiction", "Simon & Schuster"),
    ("Jane Eyre", "Charlotte Bronte", "Romance", "Penguin Classics"),
    ("Animal Farm", "George Orwell", "Satire", "Signet Classic"),
    ("Wuthering Heights", "Emily Bronte", "Romance", "Penguin Classics"),
    ("The Lord of the Rings", "J.R.R. Tolkien", "Fantasy", "Houghton Mifflin Harcourt"),
    ("Brave New World", "Aldous Huxley", "Science Fiction", "Harper Perennial"),
    ("The Chronicles of Narnia", "C.S. Lewis", "Fantasy", "HarperCollins"),
    ("The Kite Runner", "Khaled Hosseini", "Fiction", "Riverhead Books"),
    ("The Book Thief", "Markus Zusak", "Historical Fiction", "Knopf"),
    ("Gone with the Wind", "Margaret Mitchell", "Historical Fiction", "Scribner"),
    ("The Alchemist", "Paulo Coelho", "Fiction", "HarperOne"),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("Harry Potter and the Chamber of Secrets", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("Harry Potter and the Prisoner of Azkaban", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("Harry Potter and the Goblet of Fire", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("Harry Potter and the Order of the Phoenix", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("Harry Potter and the Half-Blood Prince", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("Harry Potter and the Deathly Hallows", "J.K. Rowling", "Fantasy", "Scholastic"),
    ("The Da Vinci Code", "Dan Brown", "Thriller", "Doubleday"),
    ("Angels & Demons", "Dan Brown", "Thriller", "Pocket Books"),
    ("Inferno", "Dan Brown", "Thriller", "Doubleday"),
    ("The Lost Symbol", "Dan Brown", "Thriller", "Doubleday"),
    ("Origin", "Dan Brown", "Thriller", "Doubleday"),
    ("A Game of Thrones", "George R.R. Martin", "Fantasy", "Bantam"),
    ("A Clash of Kings", "George R.R. Martin", "Fantasy", "Bantam"),
    ("A Storm of Swords", "George R.R. Martin", "Fantasy", "Bantam"),
    ("A Feast for Crows", "George R.R. Martin", "Fantasy", "Bantam"),
    ("A Dance with Dragons", "George R.R. Martin", "Fantasy", "Bantam"),
    ("The Hunger Games", "Suzanne Collins", "Science Fiction", "Scholastic Press"),
    ("Catching Fire", "Suzanne Collins", "Science Fiction", "Scholastic Press"),
    ("Mockingjay", "Suzanne Collins", "Science Fiction", "Scholastic Press"),
    ("Twilight", "Stephenie Meyer", "Romance", "Little, Brown and Company"),
    ("New Moon", "Stephenie Meyer", "Romance", "Little, Brown and Company"),
    ("Eclipse", "Stephenie Meyer", "Romance", "Little, Brown and Company"),
    ("Breaking Dawn", "Stephenie Meyer", "Romance", "Little, Brown and Company"),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Thriller", "Knopf"),
    ("The Girl Who Played with Fire", "Stieg Larsson", "Thriller", "Knopf"),
    ("The Girl Who Kicked the Hornet's Nest", "Stieg Larsson", "Thriller", "Knopf"),
    ("Life of Pi", "Yann Martel", "Fiction", "Harcourt"),
    ("The Fault in Our Stars", "John Green", "Young Adult", "Dutton Books"),
    ("Gone Girl", "Gillian Flynn", "Thriller", "Crown Publishing Group"),
    ("The Help", "Kathryn Stockett", "Historical Fiction", "Putnam"),
    ("Water for Elephants", "Sara Gruen", "Historical Fiction", "Algonquin Books"),
    ("Memoirs of a Geisha", "Arthur Golden", "Historical Fiction", "Knopf"),
    ("A Thousand Splendid Suns", "Khaled Hosseini", "Fiction", "Riverhead Books"),
    ("Divergent", "Veronica Roth", "Science Fiction", "Katherine Tegen Books"),
    ("Insurgent", "Veronica Roth", "Science Fiction", "Katherine Tegen Books"),
    ("Allegiant", "Veronica Roth", "Science Fiction", "Katherine Tegen Books"),
    ("The Maze Runner", "James Dashner", "Science Fiction", "Delacorte Press"),
    ("The Scorch Trials", "James Dashner", "Science Fiction", "Delacorte Press"),
    ("The Death Cure", "James Dashner", "Science Fiction", "Delacorte Press"),
    ("Eragon", "Christopher Paolini", "Fantasy", "Knopf"),
    ("Eldest", "Christopher Paolini", "Fantasy", "Knopf"),
    ("Brisingr", "Christopher Paolini", "Fantasy", "Knopf"),
    ("Inheritance", "Christopher Paolini", "Fantasy", "Knopf"),
    ("Percy Jackson & The Olympians: The Lightning Thief", "Rick Riordan", "Fantasy", "Disney-Hyperion"),
    ("The Sea of Monsters", "Rick Riordan", "Fantasy", "Disney-Hyperion"),
    ("The Titan's Curse", "Rick Riordan", "Fantasy", "Disney-Hyperion"),
    ("The Battle of the Labyrinth", "Rick Riordan", "Fantasy", "Disney-Hyperion"),
    ("The Last Olympian", "Rick Riordan", "Fantasy", "Disney-Hyperion"),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", "Farrar, Straus and Giroux"),
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "History", "Harper"),
    ("Homo Deus: A Brief History of Tomorrow", "Yuval Noah Harari", "History", "Harper"),
    ("21 Lessons for the 21st Century", "Yuval Noah Harari", "History", "Spiegel & Grau"),
    ("Becoming", "Michelle Obama", "Biography", "Crown"),
    ("Educated", "Tara Westover", "Biography", "Random House"),
    ("Steve Jobs", "Walter Isaacson", "Biography", "Simon & Schuster"),
    ("Elon Musk", "Ashlee Vance", "Biography", "Ecco"),
    ("The Wright Brothers", "David McCullough", "History", "Simon & Schuster"),
    ("Team of Rivals", "Doris Kearns Goodwin", "History", "Simon & Schuster"),
    ("A Brief History of Time", "Stephen Hawking", "Science", "Bantam Books"),
    ("The Selfish Gene", "Richard Dawkins", "Science", "Oxford University Press"),
    ("Cosmos", "Carl Sagan", "Science", "Random House"),
    ("Silent Spring", "Rachel Carson", "Science", "Houghton Mifflin"),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", "W. W. Norton"),
    ("Freakonomics", "Steven D. Levitt", "Economics", "William Morrow"),
    ("Outliers", "Malcolm Gladwell", "Psychology", "Little, Brown and Company"),
    ("The Tipping Point", "Malcolm Gladwell", "Psychology", "Little, Brown and Company"),
    ("Blink", "Malcolm Gladwell", "Psychology", "Little, Brown and Company"),
    ("Good to Great", "Jim Collins", "Business", "HarperBusiness"),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Finance", "Plata Publishing"),
    ("The 7 Habits of Highly Effective People", "Stephen R. Covey", "Self-Help", "Simon & Schuster"),
    ("How to Win Friends and Influence People", "Dale Carnegie", "Self-Help", "Simon & Schuster"),
    ("Atomic Habits", "James Clear", "Self-Help", "Avery"),
    ("The Power of Habit", "Charles Duhigg", "Psychology", "Random House"),
    ("Deep Work", "Cal Newport", "Productivity", "Grand Central Publishing"),
    ("Digital Minimalism", "Cal Newport", "Productivity", "Portfolio"),
    ("Zero to One", "Peter Thiel", "Business", "Crown Business"),
    ("The Lean Startup", "Eric Ries", "Business", "Crown Business"),
    ("Clean Code", "Robert C. Martin", "Technology", "Prentice Hall"),
    ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "Addison-Wesley"),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Technology", "MIT Press"),
    ("Design Patterns", "Erich Gamma", "Technology", "Addison-Wesley"),
    ("Refactoring", "Martin Fowler", "Technology", "Addison-Wesley"),
    ("Code Complete", "Steve McConnell", "Technology", "Microsoft Press"),
    ("Head First Design Patterns", "Eric Freeman", "Technology", "O'Reilly Media"),
    ("Python Crash Course", "Eric Matthes", "Technology", "No Starch Press"),
    ("Automate the Boring Stuff with Python", "Al Sweigart", "Technology", "No Starch Press"),
    ("Fluent Python", "Luciano Ramalho", "Technology", "O'Reilly Media"),
    ("Effective Java", "Joshua Bloch", "Technology", "Addison-Wesley"),
    ("JavaScript: The Good Parts", "Douglas Crockford", "Technology", "O'Reilly Media"),
    ("You Don't Know JS", "Kyle Simpson", "Technology", "O'Reilly Media"),
    ("Eloquent JavaScript", "Marijn Haverbeke", "Technology", "No Starch Press"),
    ("The Mythical Man-Month", "Frederick P. Brooks Jr.", "Technology", "Addison-Wesley"),
    ("Don't Make Me Think", "Steve Krug", "Technology", "New Riders"),
    ("The Design of Everyday Things", "Don Norman", "Design", "Basic Books"),
    ("Sprint", "Jake Knapp", "Business", "Simon & Schuster"),
    ("Hooked", "Nir Eyal", "Business", "Portfolio"),
    ("Start with Why", "Simon Sinek", "Business", "Portfolio"),
    ("Leaders Eat Last", "Simon Sinek", "Business", "Portfolio"),
    ("Dare to Lead", "Brené Brown", "Business", "Random House"),
    ("Quiet", "Susan Cain", "Psychology", "Crown"),
    ("Man's Search for Meaning", "Viktor E. Frankl", "Psychology", "Beacon Press"),
    ("The Road", "Cormac McCarthy", "Fiction", "Knopf"),
    ("No Country for Old Men", "Cormac McCarthy", "Fiction", "Knopf"),
    ("Blood Meridian", "Cormac McCarthy", "Fiction", "Random House"),
    ("The Handmaid's Tale", "Margaret Atwood", "Fiction", "McClelland and Stewart"),
    ("The Testaments", "Margaret Atwood", "Fiction", "Nan A. Talese"),
    ("Alias Grace", "Margaret Atwood", "Fiction", "McClelland and Stewart"),
    ("Oryx and Crake", "Margaret Atwood", "Science Fiction", "McClelland and Stewart"),
    ("The Year of the Flood", "Margaret Atwood", "Science Fiction", "McClelland and Stewart"),
    ("MaddAddam", "Margaret Atwood", "Science Fiction", "McClelland and Stewart"),
    ("American Gods", "Neil Gaiman", "Fantasy", "William Morrow"),
    ("Coraline", "Neil Gaiman", "Fantasy", "HarperCollins"),
    ("Stardust", "Neil Gaiman", "Fantasy", "Spike"),
    ("Good Omens", "Terry Pratchett & Neil Gaiman", "Fantasy", "Workman"),
    ("The Color Purple", "Alice Walker", "Fiction", "Harcourt Brace Jovanovich"),
    ("Beloved", "Toni Morrison", "Fiction", "Knopf"),
    ("The Bluest Eye", "Toni Morrison", "Fiction", "Holt, Rinehart and Winston"),
    ("Song of Solomon", "Toni Morrison", "Fiction", "Knopf"),
    ("Invisible Man", "Ralph Ellison", "Fiction", "Random House"),
    ("Native Son", "Richard Wright", "Fiction", "Harper & Brothers"),
    ("Their Eyes Were Watching God", "Zora Neale Hurston", "Fiction", "J.B. Lippincott"),
    ("Things Fall Apart", "Chinua Achebe", "Fiction", "William Heinemann"),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction", "Harper & Row"),
    ("Love in the Time of Cholera", "Gabriel Garcia Marquez", "Fiction", "Knopf"),
    ("Chronicle of a Death Foretold", "Gabriel Garcia Marquez", "Fiction", "Knopf"),
    ("The House of the Spirits", "Isabel Allende", "Fiction", "Knopf"),
    ("Don Quixote", "Miguel de Cervantes", "Classic", "Francisco de Robles"),
    ("The Count of Monte Cristo", "Alexandre Dumas", "Classic", "Pétion"),
    ("The Three Musketeers", "Alexandre Dumas", "Classic", "Baudry"),
    ("Les Misérables", "Victor Hugo", "Classic", "A. Lacroix, Verboeckhoven & Cie"),
    ("The Hunchback of Notre-Dame", "Victor Hugo", "Classic", "Gosselin"),
    ("War and Peace", "Leo Tolstoy", "Classic", "The Russian Messenger"),
    ("Anna Karenina", "Leo Tolstoy", "Classic", "The Russian Messenger"),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Classic", "The Russian Messenger"),
    ("The Brothers Karamazov", "Fyodor Dostoevsky", "Classic", "The Russian Messenger"),
    ("The Idiot", "Fyodor Dostoevsky", "Classic", "The Russian Messenger"),
    ("Madame Bovary", "Gustave Flaubert", "Classic", "Revue de Paris"),
    ("Great Expectations", "Charles Dickens", "Classic", "Chapman & Hall"),
    ("A Tale of Two Cities", "Charles Dickens", "Classic", "Chapman & Hall"),
    ("Oliver Twist", "Charles Dickens", "Classic", "Richard Bentley"),
    ("David Copperfield", "Charles Dickens", "Classic", "Bradbury & Evans"),
    ("Bleak House", "Charles Dickens", "Classic", "Bradbury & Evans"),
    ("Alice's Adventures in Wonderland", "Lewis Carroll", "Classic", "Macmillan"),
    ("Through the Looking-Glass", "Lewis Carroll", "Classic", "Macmillan"),
    ("Peter Pan", "J.M. Barrie", "Classic", "Hodder & Stoughton"),
    ("The Wind in the Willows", "Kenneth Grahame", "Classic", "Methuen"),
    ("Winnie-the-Pooh", "A.A. Milne", "Classic", "Methuen"),
    ("The Little Prince", "Antoine de Saint-Exupéry", "Classic", "Reynal & Hitchcock"),
    ("Charlotte's Web", "E.B. White", "Children", "Harper & Brothers"),
    ("Stuart Little", "E.B. White", "Children", "Harper & Brothers"),
    ("Matilda", "Roald Dahl", "Children", "Jonathan Cape"),
    ("Charlie and the Chocolate Factory", "Roald Dahl", "Children", "Knopf"),
    ("James and the Giant Peach", "Roald Dahl", "Children", "Knopf"),
    ("The BFG", "Roald Dahl", "Children", "Jonathan Cape"),
    ("Where the Wild Things Are", "Maurice Sendak", "Children", "Harper & Row"),
    ("The Giving Tree", "Shel Silverstein", "Children", "Harper & Row"),
    ("Green Eggs and Ham", "Dr. Seuss", "Children", "Random House"),
    ("The Cat in the Hat", "Dr. Seuss", "Children", "Random House"),
    ("Oh, the Places You'll Go!", "Dr. Seuss", "Children", "Random House"),
    ("The Very Hungry Caterpillar", "Eric Carle", "Children", "World Publishing Company"),
    ("Goodnight Moon", "Margaret Wise Brown", "Children", "Harper & Brothers"),
    ("Guess How Much I Love You", "Sam McBratney", "Children", "Walker Books"),
    ("Corduroy", "Don Freeman", "Children", "Viking Press"),
    ("Madeline", "Ludwig Bemelmans", "Children", "Simon & Schuster"),
    ("Curious George", "H.A. Rey", "Children", "Houghton Mifflin"),
    ("Paddington Bear", "Michael Bond", "Children", "William Collins & Sons"),
    ("The Tale of Peter Rabbit", "Beatrix Potter", "Children", "Frederick Warne & Co"),
    ("Pippi Longstocking", "Astrid Lindgren", "Children", "Rabén & Sjögren"),
    ("Heidi", "Johanna Spyri", "Children", "Perthes"),
    ("Anne of Green Gables", "L.M. Montgomery", "Children", "L.C. Page & Co."),
    ("Little Women", "Louisa May Alcott", "Classic", "Roberts Brothers"),
    ("The Secret Garden", "Frances Hodgson Burnett", "Children", "Frederick A. Stokes"),
    ("A Little Princess", "Frances Hodgson Burnett", "Children", "Charles Scribner's Sons"),
    ("Black Beauty", "Anna Sewell", "Children", "Jarrold & Sons"),
    ("The Call of the Wild", "Jack London", "Adventure", "Macmillan"),
    ("White Fang", "Jack London", "Adventure", "Macmillan"),
    ("Treasure Island", "Robert Louis Stevenson", "Adventure", "Cassell & Co."),
    ("Kidnapped", "Robert Louis Stevenson", "Adventure", "Cassell & Co."),
    ("Strange Case of Dr Jekyll and Mr Hyde", "Robert Louis Stevenson", "Horror", "Longmans, Green & Co."),
    ("Dracula", "Bram Stoker", "Horror", "Archibald Constable and Company"),
    ("Frankenstein", "Mary Shelley", "Horror", "Lackington, Hughes, Harding, Mavor & Jones"),
    ("The Picture of Dorian Gray", "Oscar Wilde", "Classic", "Lippincott's Monthly Magazine"),
    ("The Importance of Being Earnest", "Oscar Wilde", "Play", "Leonard Smithers & Co"),
    ("Hamlet", "William Shakespeare", "Play", "N/A"),
    ("Macbeth", "William Shakespeare", "Play", "N/A"),
    ("Romeo and Juliet", "William Shakespeare", "Play", "N/A"),
    ("Othello", "William Shakespeare", "Play", "N/A"),
    ("King Lear", "William Shakespeare", "Play", "N/A"),
    ("A Midsummer Night's Dream", "William Shakespeare", "Play", "N/A"),
    ("The Tempest", "William Shakespeare", "Play", "N/A"),
    ("Julius Caesar", "William Shakespeare", "Play", "N/A"),
    ("Much Ado About Nothing", "William Shakespeare", "Play", "N/A"),
    ("Twelfth Night", "William Shakespeare", "Play", "N/A"),
    ("The Odyssey", "Homer", "Epic", "N/A"),
    ("The Iliad", "Homer", "Epic", "N/A"),
    ("The Aeneid", "Virgil", "Epic", "N/A"),
    ("The Divine Comedy", "Dante Alighieri", "Epic", "N/A"),
    ("Paradise Lost", "John Milton", "Epic", "N/A"),
    ("Beowulf", "Unknown", "Epic", "N/A"),
    ("Gilgamesh", "Unknown", "Epic", "N/A"),
    ("The Art of War", "Sun Tzu", "Philosophy", "N/A"),
    ("Tao Te Ching", "Laozi", "Philosophy", "N/A"),
    ("The Republic", "Plato", "Philosophy", "N/A"),
    ("Meditations", "Marcus Aurelius", "Philosophy", "N/A"),
    ("Critique of Pure Reason", "Immanuel Kant", "Philosophy", "Hartknoch"),
    ("Beyond Good and Evil", "Friedrich Nietzsche", "Philosophy", "C.G. Naumann"),
    ("Thus Spoke Zarathustra", "Friedrich Nietzsche", "Philosophy", "E. Schmeitzner"),
    ("The Stranger", "Albert Camus", "Philosophy", "Gallimard"),
    ("The Plague", "Albert Camus", "Philosophy", "Gallimard"),
    ("Nausea", "Jean-Paul Sartre", "Philosophy", "Gallimard"),
    ("Being and Nothingness", "Jean-Paul Sartre", "Philosophy", "Gallimard"),
    ("The Metamorphosis", "Franz Kafka", "Classic", "Kurt Wolff"),
    ("The Trial", "Franz Kafka", "Classic", "Verlag Die Schmiede"),
    ("The Castle", "Franz Kafka", "Classic", "Kurt Wolff"),
    ("Ulysses", "James Joyce", "Classic", "Shakespeare and Company"),
    ("Dubliners", "James Joyce", "Classic", "Grant Richards"),
    ("A Portrait of the Artist as a Young Man", "James Joyce", "Classic", "B.W. Huebsch"),
    ("In Search of Lost Time", "Marcel Proust", "Classic", "Grasset & Gallimard"),
    ("Mrs. Dalloway", "Virginia Woolf", "Classic", "Hogarth Press"),
    ("To the Lighthouse", "Virginia Woolf", "Classic", "Hogarth Press"),
    ("A Room of One's Own", "Virginia Woolf", "Non-Fiction", "Hogarth Press"),
    ("Orlando", "Virginia Woolf", "Classic", "Hogarth Press"),
    ("The Sound and the Fury", "William Faulkner", "Classic", "Jonathan Cape and Harrison Smith"),
    ("As I Lay Dying", "William Faulkner", "Classic", "Jonathan Cape and Harrison Smith"),
    ("Light in August", "William Faulkner", "Classic", "Harrison Smith & Robert Haas"),
    ("Absalom, Absalom!", "William Faulkner", "Classic", "Random House"),
    ("The Old Man and the Sea", "Ernest Hemingway", "Classic", "Charles Scribner's Sons"),
    ("A Farewell to Arms", "Ernest Hemingway", "Classic", "Charles Scribner's Sons"),
    ("For Whom the Bell Tolls", "Ernest Hemingway", "Classic", "Charles Scribner's Sons"),
    ("The Sun Also Rises", "Ernest Hemingway", "Classic", "Charles Scribner's Sons"),
    ("Of Mice and Men", "John Steinbeck", "Classic", "Covici Friede"),
    ("The Grapes of Wrath", "John Steinbeck", "Classic", "The Viking Press"),
    ("East of Eden", "John Steinbeck", "Classic", "The Viking Press"),
    ("Cannery Row", "John Steinbeck", "Classic", "The Viking Press")
]

def generate_books(target_count=210):
    books = []
    
    # Use real books first
    for b in REAL_BOOKS:
        title, author, type_, publisher = b
        price = round(random.uniform(20.0, 150.0), 2)
        stock = random.randint(5, 100)
        isbn = f"978-{random.randint(1000000000, 9999999999)}"
        
        books.append({
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'year': random.randint(1900, 2023),
            'type': type_,
            'price': price,
            'stock': stock,
            'status': 'on_shelf',
            'summary': f"An excellent copy of {title} by {author}.",
            'cover': f"https://via.placeholder.com/200x300?text={title.replace(' ', '+')}"
        })

    # If we need more, generate variations
    while len(books) < target_count:
        base = random.choice(REAL_BOOKS)
        title = f"{base[0]} (Special Edition)"
        if any(b['title'] == title for b in books):
            title = f"{base[0]} (Vol. {random.randint(1,5)})"
        
        books.append({
            'title': title,
            'author': base[1],
            'publisher': base[3],
            'isbn': f"978-{random.randint(1000000000, 9999999999)}" ,
            'year': random.randint(1900, 2023),
            'type': base[2],
            'price': round(random.uniform(20.0, 200.0), 2),
            'stock': random.randint(0, 50),
            'status': 'on_shelf',
            'summary': f"Special edition of {base[0]}.",
            'cover': f"https://via.placeholder.com/200x300?text={title.replace(' ', '+')}"
        })
        
    return books

def populate():
    # Initialize DB first
    print("Initializing database schema...")
    if not initialize_database():
        print("Failed to initialize database")
        return

    conn = connect_()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("Clearing old data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute("TRUNCATE TABLE order_items")
    cursor.execute("TRUNCATE TABLE orders")
    cursor.execute("TRUNCATE TABLE books")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    
    print("Generating books...")
    books = generate_books(220) 
    
    print("Inserting books...")
    sql = """
        INSERT INTO books (title, author, publisher, isbn, year, type, price, stock, status, summary, cover)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = []
    for b in books:
        values.append((
            b['title'], b['author'], b['publisher'], b['isbn'], b['year'], 
            b['type'], b['price'], b['stock'], b['status'], b['summary'], b['cover']
        ))
    
    # Batch insert
    batch_size = 50
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        cursor.executemany(sql, batch)
        conn.commit()
        print(f"Inserted {min(i+batch_size, len(values))} books")
        
    print("Verifying users...")
    # Ensure Manager
    cursor.execute("SELECT id FROM users WHERE username='admin'")
    if not cursor.fetchone():
        print("Creating Manager...")
        cursor.execute("INSERT INTO users (username, password, nickname, role, balance) VALUES (%s, %s, %s, %s, %s)",
                       ('admin', 'admin', '店长', 'manager', 1000000))
    else:
        cursor.execute("UPDATE users SET role='manager' WHERE username='admin'")
    
    # Ensure Staff
    cursor.execute("SELECT id FROM users WHERE username='staff'")
    if not cursor.fetchone():
        print("Creating Staff...")
        cursor.execute("INSERT INTO users (username, password, nickname, role, balance) VALUES (%s, %s, %s, %s, %s)",
                       ('staff', 'staff', '店员', 'staff', 1000000))
    else:
        cursor.execute("UPDATE users SET role='staff' WHERE username='staff'")

    conn.commit()
    cursor.close()
    conn.close()
    print("Population complete!")

if __name__ == '__main__':
    populate()
