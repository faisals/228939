# database_clean.py

import sqlite3
from sqlite3 import Error
from config import DATABASE_FILE

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        print(f"Successfully connected to SQLite database: {DATABASE_FILE}")
        return conn
    except Error as e:
        print(f"Error connecting to SQLite database: {e}")
    return conn

def clean_database(conn):
    try:
        cursor = conn.cursor()

        # Clean the attempts table
        cursor.execute("DELETE FROM attempts")
        print(f"Deleted {cursor.rowcount} rows from attempts table")

        # Clean the hints table
        cursor.execute("DELETE FROM hints")
        print(f"Deleted {cursor.rowcount} rows from hints table")

        # Clean the conversations table (if it exists)
        cursor.execute("DELETE FROM conversations")
        print(f"Deleted {cursor.rowcount} rows from conversations table")

        # Clean the daily_progress table
        cursor.execute("DELETE FROM daily_progress")
        print(f"Deleted {cursor.rowcount} rows from daily_progress table")

        # Reset the completion_status in the problems table to 'Not Started'
        cursor.execute("UPDATE problems SET completion_status = 'Not Started'")
        print(f"Reset completion status for {cursor.rowcount} problems")

        # Commit the changes
        conn.commit()
        print("Database cleaned successfully")

    except Error as e:
        print(f"Error cleaning database: {e}")
        conn.rollback()

def main():
    conn = create_connection()
    if conn is not None:
        clean_database(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()