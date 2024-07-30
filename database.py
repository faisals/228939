import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
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
        
        # Create Attempts table with attempt_type column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                code TEXT,
                result TEXT,
                attempt_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        # Create UserProgress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                topic TEXT PRIMARY KEY,
                proficiency_level INTEGER
            )
        ''')
        
        conn.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    initialize_database()