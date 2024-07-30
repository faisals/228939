from database import initialize_database
from problem_manager import ProblemManager
from web_scraper import fetch_problem_details
from ai_assistant import get_hint, get_explanation
from config import DATABASE_FILE

def main():
    initialize_database()
    problem_manager = ProblemManager(DATABASE_FILE)

    while True:
        print("\nLeetCoder Menu:")
        print("1. Add new problem")
        print("2. Get problem details")
        print("3. Update problem status")
        print("4. Get AI hint")
        print("5. Get AI explanation")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            url = input("Enter problem URL: ")
            details = fetch_problem_details(url)
            if details:
                description = input("Enter problem description: ")
                problem_manager.add_problem(url, details['title'], details['difficulty'], description)
            else:
                print("Failed to fetch problem details.")

        elif choice == '2':
            problem_id = int(input("Enter problem ID: "))
            problem = problem_manager.get_problem(problem_id)
            if problem:
                print(f"ID: {problem[0]}")
                print(f"URL: {problem[1]}")
                print(f"Title: {problem[2]}")
                print(f"Difficulty: {problem[3]}")
                print(f"Description: {problem[4]}")
                print(f"Status: {problem[5]}")
            else:
                print("Problem not found.")

        elif choice == '3':
            problem_id = int(input("Enter problem ID: "))
            status = input("Enter new status: ")
            problem_manager.update_problem_status(problem_id, status)

        elif choice == '4':
            problem_id = int(input("Enter problem ID: "))
            problem = problem_manager.get_problem(problem_id)
            if problem:
                hint = get_hint(problem[4])  # problem[4] is the description
                print(f"AI Hint: {hint}")
            else:
                print("Problem not found.")

        elif choice == '5':
            problem_id = int(input("Enter problem ID: "))
            problem = problem_manager.get_problem(problem_id)
            if problem:
                user_code = input("Enter your code solution: ")
                explanation = get_explanation(problem[4], user_code)
                print(f"AI Explanation: {explanation}")
            else:
                print("Problem not found.")

        elif choice == '6':
            print("Thank you for using LeetCoder. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()