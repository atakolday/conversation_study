
# Project Title

This project is designed to [briefly describe the purpose of the project]. It includes scripts for managing authentication, sending emails, handling participant data, and running the main application logic.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Files](#files)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/projectname.git
   cd projectname
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Setup the environment variables:**
   - Create a `.env` file in the root directory.
   - Add the necessary environment variables, such as API keys, email credentials, etc.

2. **Run the main script:**
   ```bash
   python main.py
   ```

## Files

- `Auth.py`: Contains the logic for user authentication, including login and token management.
- `emails.py`: Handles the sending of emails, including templating and SMTP configuration.
- `participants.py`: Manages participant data, including loading, saving, and processing participant-related information.
- `main.py`: The main entry point of the application, which orchestrates the execution of other scripts.

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
