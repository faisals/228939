import sqlite3
from sqlite3 import Error
from datetime import datetime

class ProblemManager:
    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(f"Error connecting to database: {e}")
        return conn
    
    def record_attempt(self, problem_id, attempt_type, code=None, result=None):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO attempts (problem_id, code, result, attempt_type)
                    VALUES (?, ?, ?, ?)
                ''', (problem_id, code, result, attempt_type))
                conn.commit()
                print(f"Attempt recorded successfully.")
                return True
            except Error as e:
                print(f"Error recording attempt: {e}")
                return False
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")
            return False

    def add_problem(self, url, title, difficulty, description):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO problems (url, title, difficulty, description, completion_status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (url, title, difficulty, description, 'Not Started'))
                conn.commit()
                print(f"Problem added successfully. ID: {cursor.lastrowid}")
                return cursor.lastrowid
            except Error as e:
                print(f"Error adding problem: {e}")
                return None
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")
            return None

    def get_problem(self, problem_id):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
                problem = cursor.fetchone()
                return problem
            except Error as e:
                print(f"Error retrieving problem: {e}")
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")



    # ... (other methods remain the same)

    def update_problem_status(self, problem_id, status):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE problems
                    SET completion_status = ?
                    WHERE id = ?
                ''', (status, problem_id))
                conn.commit()
                print(f"Problem status updated successfully.")
                return True
            except Error as e:
                print(f"Error updating problem status: {e}")
                return False
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")
            return False

    def get_all_problems_with_details(self):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.title, p.difficulty, p.completion_status, 
                           MAX(a.timestamp) as last_attempt
                    FROM problems p
                    LEFT JOIN attempts a ON p.id = a.problem_id
                    GROUP BY p.id
                    ORDER BY last_attempt DESC NULLS LAST, p.id DESC
                ''')
                problems = cursor.fetchall()
                return problems
            except Error as e:
                print(f"Error retrieving all problems with details: {e}")
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")
        return []
    
    def delete_problem(self, problem_id):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                # Delete the problem
                cursor.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
                # Delete associated attempts
                cursor.execute("DELETE FROM attempts WHERE problem_id = ?", (problem_id,))
                conn.commit()
                print(f"Problem and associated attempts deleted successfully.")
                return True
            except Error as e:
                print(f"Error deleting problem: {e}")
                return False
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")
            return False

# You can add more methods here as needed