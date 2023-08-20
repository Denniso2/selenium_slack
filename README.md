# Slack Automation Command Line Tool

This tool allows you to log into Slack manually, save the session cookies for future sessions, and send messages to specified channels using command line arguments.

## Prerequisites

- Python 3.x
- Selenium library
- ChromeDriver for Selenium

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Denniso2/selenium_slack.git
   ```

2. Navigate to the directory:

   ```bash
   cd selenium_slack
   ```

3. Install the required libraries:

   ```bash
   pip install selenium
   ```

4. Download [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) and ensure it's available in your `PATH` or in the same directory as the script.

## Usage

1. Manually log into Slack and save cookies for future sessions:

   ```bash
   python selenium_slack.py --login
   ```

2. Send a message to a specified channel:

   ```bash
   python selenium_slack.py --workspace [Your Workspace URL] --channel [Channel ID] --message "Your message here"
   ```
   
3. Send a random message to a specified channel:

   ```bash
   python selenium_slack.py --workspace [Your Workspace URL] --channel [Channel ID] --message "Message 1" "Message 2" "Message 3"
   ```

For more detailed information about command arguments, run:

```bash
python selenium_slack.py --help
```

## Issues & Contributions

- If you find any bugs or want to suggest improvements, please open an issue.
- Pull requests are always welcome!
