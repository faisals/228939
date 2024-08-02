import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('leetcoder.db')
        print(f"Successfully connected to SQLite. SQLite version: {sqlite3.version}")
        return conn
    except Error as e:
        print(f"Error connecting to SQLite database: {e}")
    return conn

def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # Create Problems table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                difficulty TEXT,
                description TEXT,
                completion_status TEXT
            )
        ''')
        
        # Create or update Attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                attempt_type TEXT,
                code TEXT,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                problems_worked INTEGER DEFAULT 0,
                problems_completed INTEGER DEFAULT 0
            )
        ''')
        
        # Check if attempt_type column exists, if not, add it
        cursor.execute("PRAGMA table_info(attempts)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'attempt_type' not in columns:
            cursor.execute('ALTER TABLE attempts ADD COLUMN attempt_type TEXT')
        
        # Create Hints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                hint_type TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        # Create Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                user_message TEXT,
                ai_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submitted_solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                code TEXT,
                language TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        conn.commit()
        print("Tables created or updated successfully")
    except Error as e:
        print(f"Error creating or updating tables: {e}")

def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    initialize_database()