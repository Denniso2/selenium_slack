import os
import pickle
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class NotLoggedInException(Exception):
    """Exception to handle failed login attempts."""
    pass


class SlackAutomator:
    """Automate Slack login using saved cookies."""

    COOKIE_FILE = "slack_cookies.pkl"
    WORKSPACE_URL = "https://yourworkspace.slack.com"

    def __init__(self):
        self.driver = webdriver.Chrome()

    def cookies_exist(self):
        """Check if cookies file exists."""
        return os.path.exists(self.COOKIE_FILE)

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
        if not self.cookies_exist():
            return

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
        self.driver.get(self.WORKSPACE_URL)
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
        channel_url = f"{self.WORKSPACE_URL}/messages/{channel_id}/"
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


if __name__ == "__main__":
    automator = SlackAutomator()
    automator.load_cookies_and_login()
    automator.navigate_to_channel("", "")
    automator.post_message("hey there tester")
    automator.quit()
