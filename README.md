# LeetCoder

LeetCoder is a Flask-based web application designed to help users manage, practice, and track their progress on LeetCode problems. It provides an intuitive interface for adding problems, viewing details, getting AI-powered hints, and managing your coding practice routine.

## Features

- **Quick Add**: Automatically add LeetCode problems by URL
- **Problem Management**: View and organize your LeetCode problems
- **Progress Tracking**: Keep track of your problem-solving status
- **AI-Powered Hints**: Get helpful hints using OpenAI's GPT model
- **Code Editor**: Write and run Python code directly in the application
- **Problem Details**: View comprehensive problem information including difficulty and description

## Prerequisites

- Python 3.10 or higher
- Conda (for environment management)
- OpenAI API key

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/leetcoder.git
   cd leetcoder
   ```

2. Set up a Conda environment:
   ```
   conda create -n leetcoder python=3.10
   conda activate leetcoder
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `config.py` file in the project root and add your OpenAI API key:
   ```python
   OPENAI_API_KEY = 'your_openai_api_key_here'
   DATABASE_FILE = 'leetcoder.db'
   ```

5. Initialize the database:
   ```
   python database.py
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Open a web browser and navigate to `http://localhost:5000`

## Usage

### Adding Problems
- Use the "Quick Add Problem" form on the home page to add new LeetCode problems by URL.
- The application will automatically fetch the problem details from LeetCode.

### Viewing Problems
- The main page displays a list of all added problems with their ID, title, difficulty, status, and last attempt date.
- Click on a problem's "View" link to see its full details.

### Problem Details
- On the problem details page, you can:
  - View the full problem description
  - Get AI-generated hints
  - Write and run Python code
  - Update the problem's status

### Getting Hints
- Click the "Get Hint" button on a problem's detail page to receive an AI-generated hint.
- For more specific code-related hints, use the "Get Code Hint" button.

### Writing and Running Code
- Use the built-in code editor on the problem details page to write your solution.
- Click "Run Code" to execute your Python code and see the output.

### Updating Problem Status
- On the problem details page, use the dropdown menu to update a problem's status (Not Started, In Progress, Completed).

## Contributing

Contributions to LeetCoder are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository on GitHub.
2. Clone your forked repository locally.
3. Create a new branch for your feature or bug fix.
4. Make your changes and commit them with clear, descriptive commit messages.
5. Push your changes to your fork on GitHub.
6. Submit a Pull Request to the main LeetCoder repository.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Thanks to LeetCode for providing a platform for coding practice.
- This project uses OpenAI's GPT model for generating hints.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.