import sqlite3
from sqlite3 import Error
from datetime import datetime, date, timedelta
import logging
import random


class ProblemManager:
    def __init__(self, db_file):
        self.db_file = db_file

    def get_activity_grid_data(self):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=28)  # 4 weeks
                
                query = '''
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM attempts
                    WHERE DATE(timestamp) BETWEEN ? AND ?
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp)
                '''
                
                print(f"Executing query: {query}")
                print(f"With parameters: {start_date.isoformat()}, {end_date.isoformat()}")
                
                cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
                
                results = cursor.fetchall()
                print(f"Query results: {results}")
                
                # Create a dict with all dates initialized to 0
                all_dates = {(start_date + timedelta(days=i)).isoformat(): 0 for i in range(29)}
                
                # Update the dict with actual counts
                for date_str, count in results:
                    all_dates[date_str] = count
                
                print("Processed data before sample generation:", all_dates)
                
                # If no data found, generate sample data
                if all(count == 0 for count in all_dates.values()):
                    for date in all_dates.keys():
                        all_dates[date] = random.randint(0, 5)
                    print("Generated sample data")
                else:
                    print("Using real data")
                
                print("Final activity grid data:", all_dates)
                return all_dates
            except Error as e:
                print(f"Error fetching activity grid data: {e}")
            finally:
                conn.close()
        return {}

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(f"Error connecting to database: {e}")
        return conn
    
    def update_daily_progress(self, problem_id, is_completed):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                today = date.today().isoformat()
                
                # Check if there's an entry for today
                cursor.execute('SELECT * FROM daily_progress WHERE date = ?', (today,))
                entry = cursor.fetchone()
                
                if entry:
                    # Update existing entry
                    if is_completed:
                        cursor.execute('UPDATE daily_progress SET problems_worked = problems_worked + 1, problems_completed = problems_completed + 1 WHERE date = ?', (today,))
                    else:
                        cursor.execute('UPDATE daily_progress SET problems_worked = problems_worked + 1 WHERE date = ?', (today,))
                else:
                    # Create new entry
                    if is_completed:
                        cursor.execute('INSERT INTO daily_progress (date, problems_worked, problems_completed) VALUES (?, 1, 1)', (today,))
                    else:
                        cursor.execute('INSERT INTO daily_progress (date, problems_worked, problems_completed) VALUES (?, 1, 0)', (today,))
                
                conn.commit()
                print(f"Daily progress updated for {today}")
                return True
            except Error as e:
                print(f"Error updating daily progress: {e}")
                return False
            finally:
                conn.close()
        return False

    def get_daily_progress(self, start_date=None, end_date=None):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                if start_date and end_date:
                    cursor.execute('SELECT * FROM daily_progress WHERE date BETWEEN ? AND ? ORDER BY date', (start_date, end_date))
                else:
                    cursor.execute('SELECT * FROM daily_progress ORDER BY date')
                return cursor.fetchall()
            except Error as e:
                print(f"Error retrieving daily progress: {e}")
            finally:
                conn.close()
        return []
    
    def update_last_attempt(self, problem_id):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    INSERT INTO attempts (problem_id, attempt_type, timestamp)
                    VALUES (?, ?, ?)
                ''', (problem_id, 'interaction', current_time))
                conn.commit()
                logging.info(f"Last attempt updated for problem {problem_id}")
                return True
            except Error as e:
                logging.error(f"Error updating last attempt for problem {problem_id}: {e}")
                return False
            finally:
                conn.close()
        else:
            logging.error(f"Failed to create database connection for problem {problem_id}")
        return False
    
    def add_hint(self, problem_id, hint_type, content):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO hints (problem_id, hint_type, content)
                    VALUES (?, ?, ?)
                ''', (problem_id, hint_type, content))
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error adding hint: {e}")
            finally:
                conn.close()
        return None
    
    def add_conversation(self, problem_id, user_message, ai_response):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (problem_id, user_message, ai_response)
                    VALUES (?, ?, ?)
                ''', (problem_id, user_message, ai_response))
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error adding conversation: {e}")
            finally:
                conn.close()
        return None
    
    def get_hints(self, problem_id):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT hint_type, content, timestamp
                    FROM hints
                    WHERE problem_id = ?
                    ORDER BY timestamp DESC
                ''', (problem_id,))
                return cursor.fetchall()
            except Error as e:
                print(f"Error retrieving hints: {e}")
            finally:
                conn.close()
        return []
    
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
        
    def get_conversations(self, problem_id):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_message, ai_response, timestamp
                    FROM conversations
                    WHERE problem_id = ?
                    ORDER BY timestamp ASC
                ''', (problem_id,))
                return cursor.fetchall()
            except Error as e:
                print(f"Error retrieving conversations: {e}")
            finally:
                conn.close()
        return []

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
                    SELECT p.id, p.url, p.title, p.difficulty, p.completion_status, 
                           MAX(a.timestamp) as last_attempt
                    FROM problems p
                    LEFT JOIN attempts a ON p.id = a.problem_id
                    GROUP BY p.id
                    ORDER BY last_attempt DESC NULLS LAST, p.id DESC
                ''')
                problems = cursor.fetchall()
                logging.debug(f"Fetched {len(problems)} problems")
                if problems:
                    logging.debug(f"Sample problem data: {problems[0]}")
                return problems
            except Error as e:
                logging.error(f"Error retrieving all problems with details: {e}")
            finally:
                conn.close()
        return []
    
    def check_attempts(self, problem_id):
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM attempts
                    WHERE problem_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 5
                ''', (problem_id,))
                attempts = cursor.fetchall()
                return attempts
            except Error as e:
                print(f"Error checking attempts: {e}")
            finally:
                conn.close()
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