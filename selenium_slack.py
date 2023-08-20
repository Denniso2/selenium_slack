import argparse
import random
import re
import pickle
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class NotLoggedInException(Exception):
    """Exception to handle failed login attempts."""
    pass


class SlackAutomator:
    """Automate Slack login using saved cookies."""

    COOKIE_FILE = "slack_cookies.pkl"

    def __init__(self, workspace_url):
        self.driver = webdriver.Chrome()
        self.workspace_url = workspace_url

    def validate_workspace_url(self, workspace_url):
        pattern = r'^https://[\w\-]+(\.enterprise)?\.slack\.com$'
        if not re.match(pattern, workspace_url):
            raise ValueError("Invalid workspace URL format. It should be of the form https://company.slack.com or https://company.enterprise.slack.com")

    def is_logged_in(self, timeout=30):
        """
        Check if the user is logged into Slack by looking for a specific element.

        Args:
        - timeout: Time (in seconds) to wait for the login element to appear.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'p-ia__nav__user'))
            )
        except (NoSuchElementException, TimeoutException):
            raise NotLoggedInException("User is not logged in or the element was not found within the given timeout.")

    def save_cookies(self):
        """Save cookies to a file."""
        with open(self.COOKIE_FILE, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)

    def load_cookies(self):
        """Load cookies from a file and add them to the browser session."""
        with open(self.COOKIE_FILE, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def login_and_save_cookies(self):
        """Manually log into Slack and save the session cookies."""
        self.driver.get("https://slack.com/signin")
        input("Press Enter after you have logged in manually...")
        self.save_cookies()
        self.driver.quit()

    def load_cookies_and_login(self):
        """Load cookies from a file and attempt to log into Slack."""
        self.driver.get(self.workspace_url)
        self.load_cookies()
        self.driver.refresh()

        # To verify if the login was successful
        self.is_logged_in()

    def get_channel_title_element(self, channel_id):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, ".p-view_header__channel_title")
        except NoSuchElementException:
            raise ValueError(f"Channel with id {channel_id} does not exist")

    def navigate_to_channel(self, channel_id):
        """
        Navigate to a specific Slack channel using its channel_id.

        Args:
        - channel_id: ID of the Slack channel to navigate to.
        """
        channel_url = f"{self.workspace_url}/messages/{channel_id}/"
        self.driver.get(channel_url)

        title_element = self.get_channel_title_element(channel_id)
        if title_element.text == "unknown-channel":
            raise ValueError(f"Channel with id {channel_id} does not exist")

    def post_message(self, message, timeout=30):
        """
        Post a message to the currently active Slack channel.

        Args:
        - message: The text message to post.
        """
        message_box = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor"))
        )
        message_box.send_keys(message)

        # Clicking the "send" button, adjust this if Slack's UI changes
        send_button = self.driver.find_element(By.XPATH, "//button[@data-qa='texty_send_button']")
        send_button.click()
        time.sleep(10)

    def quit(self):
        """Quits the browser."""
        self.driver.quit()


def main():
    parser = argparse.ArgumentParser(description='Slack Automation Command Line Tool')

    parser.add_argument('--workspace', type=str, default="",
                        help='URL of the Slack workspace, e.g., https://company.slack.com. Not required for login.')
    parser.add_argument('--login', action='store_true',
                        help='Use this flag to log in manually to Slack and save cookies for future sessions.')
    parser.add_argument('--channel', type=str,
                        help='Provide the ID of the Slack channel to which you want to post a message.')
    parser.add_argument('--message', type=str, nargs='+',
                        help='The message you want to post to the specified Slack channel. If multiple one will be selected randomly.')

    args = parser.parse_args()

    automator = SlackAutomator(args.workspace)

    try:
        if args.login:
            automator.login_and_save_cookies()
        elif args.channel and args.message and args.workspace:
            automator.validate_workspace_url(args.workspace)
            selected_message = random.choice(args.message)  # Choose a random message
            automator.load_cookies_and_login()
            automator.navigate_to_channel(args.channel)
            automator.post_message(selected_message)
            print(f"Message '{selected_message}' posted successfully.")
        else:
            print("Invalid arguments. Use --help for usage information.")
    except NotLoggedInException:
        print("Error: You're not logged in to Slack. Please ensure you have valid cookies or use the --login flag.")
    except (IOError, pickle.UnpicklingError):
        print("Error: There was an issue with the cookie file. It might be corrupted, missing, or there might be permission issues.")
    except NoSuchElementException:
        print("Error: A necessary web element was not found. Slack's UI might have changed.")
    except TimeoutException:
        print("Error: Operation timed out. Ensure you have a stable internet connection.")
    except WebDriverException:
        print("Error: There was an issue with the WebDriver. Ensure the browser driver is correctly installed and up-to-date.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
