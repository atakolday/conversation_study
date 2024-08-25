
# Stanford University Conversation Study

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
3. **Specify use case from available commands:**
   After running the main script, you can choose from the following commands:

   - **Invite:**
      - `rID_invite` : Send invitation email by RESPONDENT_ID.
      - `mass_invite` : Send invitation emails to each participant for a given day (e.g., Monday, Tuesday).
      - `send_zoom` : Send Zoom link, participant_id, and calendar event after confirmation.
      - `confirmation` : Send confirmation email after participants confirm their conversation time.

   - **Reminder:**
      - `rID_reminder` : Send reminder email by RESPONDENT_ID.
      - `reminder_1hr` : Send the 1-hour reminder email by RESPONDENT_ID.
      - `reminder_24hr` : Send the 24-hour reminder for confirmed participants by day of the week (e.g., Monday).
      - `noreply` : Re-send invitation as a reminder for non-confirmed participants.

   - **Other:**
      - `reschedule` : Send the reschedule email template by RESPONDENT_ID.
      - `reschedule_day` : Send the reschedule emails by RESPONDENT_ID for a specific day (e.g., Monday).
      - `reschedule_nw` : Send the rescheduling email for next week.
      - `conversation` : Generate pre-conversation information by slot (e.g., Monday-8:00 AM).
      - `payment` : Send payment email to Rick with day of the week as user input.
        
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
