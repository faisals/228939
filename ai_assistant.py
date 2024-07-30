import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_hint(problem_description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": f"Can you give me a hint for this LeetCode problem? {problem_description}"}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error getting hint from OpenAI: {e}")
        return None

def get_explanation(problem_description, user_code):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful coding tutor."},
                {"role": "user", "content": f"Can you explain this solution for the following LeetCode problem?\n\nProblem: {problem_description}\n\nSolution:\n{user_code}"}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error getting explanation from OpenAI: {e}")
        return None

# Add more AI-assisted functions as needed