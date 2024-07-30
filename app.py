from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import initialize_database
from problem_manager import ProblemManager
from config import DATABASE_FILE, OPENAI_API_KEY, OPENAI_MODEL  
from openai import OpenAI
from datetime import datetime
import subprocess
import tempfile
import markdown
import requests
import re
import logging


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # needed for flashing messages

initialize_database()
problem_manager = ProblemManager(DATABASE_FILE)

client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Add this function to create a markdown filter
def markdown_filter(text):
    return markdown.markdown(text, extensions=['fenced_code', 'codehilite'])

# Register the markdown filter with the Jinja environment
app.jinja_env.filters['markdown'] = markdown_filter

@app.route('/')
def index():
    problems = problem_manager.get_all_problems_with_details()
    return render_template('index.html', problems=problems)

@app.route('/add_problem', methods=['GET', 'POST'])
def add_problem():
    if request.method == 'POST':
        url = request.form['url']
        title = request.form['title']
        difficulty = request.form['difficulty']
        description = request.form['description']
        
        problem_id = problem_manager.add_problem(url, title, difficulty, description)
        if problem_id:
            flash('Problem added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to add problem.', 'error')
    
    return render_template('add_problem.html')

""" @app.route('/problem/<int:problem_id>')
def problem_details(problem_id):
    problem = problem_manager.get_problem(problem_id)
    if problem:
        hints = problem_manager.get_hints(problem_id)
        conversations = problem_manager.get_conversations(problem_id)
        return render_template('problem_details.html', problem=problem, hints=hints, conversations=conversations)
    else:
        flash('Problem not found.', 'error')
        return redirect(url_for('index')) """

@app.route('/problem/<int:problem_id>')
def problem_details(problem_id):
    problem = problem_manager.get_problem(problem_id)
    if problem:
        hints = problem_manager.get_hints(problem_id)
        conversations = problem_manager.get_conversations(problem_id)
        recent_attempts = problem_manager.check_attempts(problem_id)
        return render_template('problem_details.html', problem=problem, hints=hints, conversations=conversations, recent_attempts=recent_attempts)
    else:
        flash('Problem not found.', 'error')
        return redirect(url_for('index'))

@app.route('/update_status/<int:problem_id>', methods=['POST'])
def update_status(problem_id):
    new_status = request.form['status']
    success = problem_manager.update_problem_status(problem_id, new_status)
    if success:
        # Record the attempt with the current timestamp
        problem_manager.update_last_attempt(problem_id)
        flash('Problem status updated successfully!', 'success')
    else:
        flash('Failed to update problem status.', 'error')
    return redirect(url_for('problem_details', problem_id=problem_id))

@app.route('/run_code/<int:problem_id>', methods=['POST'])
def run_code(problem_id):
    code = request.json['code']
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(['python', temp_file_path], capture_output=True, text=True, timeout=5)
        output = result.stdout if result.returncode == 0 else result.stderr
        problem_manager.record_attempt(problem_id, 'run_code', code, output)
        problem_manager.update_last_attempt(problem_id)  # Update last attempt
    except subprocess.TimeoutExpired:
        output = "Execution timed out after 5 seconds."
    except Exception as e:
        output = f"An error occurred: {str(e)}"

    return jsonify({'output': output})

@app.route('/get_hint/<int:problem_id>')
def get_hint(problem_id):
    problem = problem_manager.get_problem(problem_id)
    if problem:
        prompt = f"Given this LeetCode problem: {problem[2]}\n\nDescription: {problem[4]}\n\nProvide a general hint to solve this problem without giving any code or specific algorithm steps. Focus on problem-solving strategies and key concepts to consider. Format your response using markdown."
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant providing general hints."},
                {"role": "user", "content": prompt}
            ]
        )
        hint = response.choices[0].message.content.strip()
        html_hint = markdown.markdown(hint)
        problem_manager.add_hint(problem_id, 'general', hint)
        problem_manager.update_last_attempt(problem_id)  # Update last attempt
        return jsonify({'hint': html_hint})
    else:
        return jsonify({'error': 'Problem not found'}), 404

@app.route('/get_code_hint/<int:problem_id>')
def get_code_hint(problem_id):
    problem = problem_manager.get_problem(problem_id)
    if problem:
        prompt = f"Given this LeetCode problem: {problem[2]}\n\nDescription: {problem[4]}\n\nProvide a code hint to solve this problem. Include a small code snippet or pseudo-code that demonstrates a key part of the solution without giving away the entire implementation. Format your response using markdown, and ensure code blocks are properly formatted."
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant providing code hints."},
                {"role": "user", "content": prompt}
            ]
        )
        hint = response.choices[0].message.content.strip()
        html_hint = markdown.markdown(hint, extensions=['fenced_code', 'codehilite'])
        problem_manager.add_hint(problem_id, 'code', hint)
        problem_manager.update_last_attempt(problem_id)  # Update last attempt
        return jsonify({'hint': html_hint})
    else:
        return jsonify({'error': 'Problem not found'}), 404


@app.route('/chat_with_ai', methods=['POST'])
def chat_with_ai():
    problem_id = request.json['problem_id']
    user_message = request.json['message']
    hint_type = request.json.get('hint_type', 'general')
    problem = problem_manager.get_problem(problem_id)

    if problem:
        if hint_type == 'code':
            system_message = "You are a helpful coding assistant providing code-related hints and explanations. Format your responses using markdown, and ensure code blocks are properly formatted."
            prompt = f"Context: LeetCode problem '{problem[2]}'\nDescription: {problem[4]}\n\nUser is asking about code hints. Provide code-related explanations or snippets as appropriate.\n\nUser: {user_message}\n\nAI:"
        else:
            system_message = "You are a helpful coding assistant providing general problem-solving hints and strategies. Format your responses using markdown."
            prompt = f"Context: LeetCode problem '{problem[2]}'\nDescription: {problem[4]}\n\nUser is asking for general hints. Avoid giving specific code solutions.\n\nUser: {user_message}\n\nAI:"

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        ai_response = response.choices[0].message.content.strip()
        html_response = markdown.markdown(ai_response, extensions=['fenced_code', 'codehilite'])
        problem_manager.add_conversation(problem_id, user_message, ai_response)
        return jsonify({'response': html_response})
    else:
        return jsonify({'error': 'Problem not found'}), 404


@app.route('/auto_add_problem', methods=['GET', 'POST'])
def auto_add_problem():
    if request.method == 'POST':
        url = request.form['url']
        try:
            # Extract the problem title slug from the URL
            match = re.search(r'/problems/([^/]+)/', url)
            if not match:
                raise ValueError("Invalid LeetCode problem URL")
            title_slug = match.group(1)

            # Fetch problem details from LeetCode's GraphQL API
            api_url = "https://leetcode.com/graphql"
            query = """
            query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionId
                title
                difficulty
                content
              }
            }
            """
            response = requests.post(api_url, json={
                'query': query,
                'variables': {'titleSlug': title_slug}
            })
            response.raise_for_status()
            data = response.json()

            # Extract problem details
            problem_data = data['data']['question']
            title = problem_data['title']
            difficulty = problem_data['difficulty']
            description = problem_data['content']

            # Add problem to database
            problem_id = problem_manager.add_problem(url, title, difficulty, description)
            
            if problem_id:
                flash('Problem automatically added successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Failed to add problem to database.', 'error')
        except requests.RequestException as e:
            flash(f'Failed to fetch problem details: {str(e)}', 'error')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('auto_add_problem.html')


@app.route('/delete_problem/<int:problem_id>', methods=['POST'])
def delete_problem(problem_id):
    success = problem_manager.delete_problem(problem_id)
    if success:
        flash('Problem deleted successfully!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Failed to delete problem.', 'error')
        return redirect(url_for('problem_details', problem_id=problem_id))


@app.route('/quick_add_problem', methods=['POST'])
def quick_add_problem():
    url = request.form['url']
    try:
        # Extract the problem title slug from the URL
        match = re.search(r'/problems/([^/]+)/', url)
        if not match:
            return jsonify({'success': False, 'message': "Invalid LeetCode problem URL"})
        title_slug = match.group(1)

        # Fetch problem details from LeetCode's GraphQL API
        api_url = "https://leetcode.com/graphql"
        query = """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            title
            difficulty
            content
          }
        }
        """
        response = requests.post(api_url, json={
            'query': query,
            'variables': {'titleSlug': title_slug}
        })
        response.raise_for_status()
        data = response.json()

        # Extract problem details
        problem_data = data['data']['question']
        title = problem_data['title']
        difficulty = problem_data['difficulty']
        description = problem_data['content']

        # Add problem to database
        problem_id = problem_manager.add_problem(url, title, difficulty, description)
        
        if problem_id:
            return jsonify({'success': True, 'message': 'Problem added successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add problem to database.'})
    except requests.RequestException as e:
        return jsonify({'success': False, 'message': f'Failed to fetch problem details: {str(e)}'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@app.template_filter('format_date')
def format_date(value):
    if value and isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            return value  # Return the original value if it's not a valid date string
    return value if value else 'N/A'

app.jinja_env.filters['format_date'] = format_date

if __name__ == '__main__':
    app.run(debug=True)