import requests
from bs4 import BeautifulSoup

def fetch_problem_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_element = soup.find('div', class_='flex space-x-4')
        title = title_element.find('a').text.strip() if title_element else "Unknown Title"
        
        # Extract difficulty
        difficulty_element = soup.find('div', class_='mt-3 flex space-x-4')
        difficulty = difficulty_element.find('div').text.strip() if difficulty_element else "Unknown Difficulty"
        
        return {
            'title': title,
            'difficulty': difficulty
        }
    except requests.RequestException as e:
        print(f"Error fetching problem details: {e}")
        return None

# Note: This is a basic implementation and might need adjustments
# depending on LeetCode's actual HTML structure and any changes they make.