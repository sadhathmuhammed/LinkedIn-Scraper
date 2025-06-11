import pickle, os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

class LinkedInScraper:
    def __init__(self):
        """
        Initialize the LinkedIn scraper. This will launch a headless Chrome instance and
        login to LinkedIn using the credentials stored in the LINKEDIN_USER and
        LINKEDIN_PASS environment variables. If a session is already saved on disk,
        it will be loaded instead of re-logging in.
        """
        self.session_file = "session.pkl"
        self.driver = self._init_driver()
        self.session = requests.Session()
        self.base_api = "https://www.linkedin.com/voyager/api/relationships/connections"

        if not self._load_session():
            self._login()

    def _init_driver(self):
        """
        Initialize the Chrome driver used for web scraping. The driver will be run in
        headless mode, and a flag will be set to disable the "Automation controlled"
        feature that LinkedIn uses to detect bots. This flag is necessary to prevent
        LinkedIn from presenting a CAPTCHA when logging in.
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return webdriver.Chrome(options=options)

    def _login(self):
        """
        Log in to LinkedIn using the credentials stored in the LINKEDIN_USER and
        LINKEDIN_PASS environment variables. This is necessary to access the
        LinkedIn API endpoints used by the scraper.

        This function will launch a headless Chrome instance and navigate to the
        LinkedIn login page. It will then enter the credentials and submit the
        form. After the form is submitted, it will wait for 5 seconds to allow the
        page to fully load, and then it will retrieve the cookies set by the
        LinkedIn server. The cookies will be added to the requests session used
        by the scraper, and they will also be saved to disk.

        If a session is already saved on disk, it will be loaded instead of
        re-logging in.
        """
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        self.driver.find_element("id", "username").send_keys(os.getenv("LINKEDIN_USER"))
        self.driver.find_element("id", "password").send_keys(os.getenv("LINKEDIN_PASS"))
        self.driver.find_element("xpath", "//button[@type='submit']").click()
        time.sleep(5)

        cookies = self.driver.get_cookies()
        self.session.cookies.update({cookie['name']: cookie['value'] for cookie in cookies})
        self._save_session(cookies)

    def _save_session(self, cookies):
        """
        Save the given cookies to the session file saved on disk.

        This function is called after a successful login, and it will save the
        cookies set by the LinkedIn server to a file on disk. The file will be
        used to load the session cookies the next time the scraper is run.

        Args:
            cookies (list[dict]): The cookies to be saved to disk.
        """
        with open(self.session_file, "wb") as f:
            pickle.dump(cookies, f)

    def _load_session(self):
        """
        Load the session cookies from the session file saved on disk. If the file
        does not exist, return False. Otherwise, load the cookies and try a small
        Voyager call to validate that the session is still valid. If the call
        succeeds, return True. Otherwise, return False.
        """
        if not os.path.exists(self.session_file):
            return False
        with open(self.session_file, "rb") as f:
            cookies = pickle.load(f)
            self.session.cookies.update({cookie['name']: cookie['value'] for cookie in cookies})
        r = self.session.get(self.base_api, headers=self._headers(), params={"count": 1})
        return r.status_code == 200

    def _headers(self):
        return {
            "Csrf-Token": self.session.cookies.get("JSESSIONID").strip('"'),
            "x-restli-protocol-version": "2.0.0",
            "accept": "application/json"
        }

    def fetch_connections(self, start=0, count=10):
        """
        Fetch connections from LinkedIn.

        This function makes a GET call to the LinkedIn connections API with the
        given start and count parameters. It will return a list of dictionaries,
        each with the name, title, and profile URL of a connection.

        Args:
            start (int): The index of the first connection to return.
            count (int): The number of connections to return.

        Returns:
            list[dict]: A list of dictionaries, each with the name, title, and
                profile URL of a connection.
        """
        url = self.base_api
        params = {"start": start, "count": count}
        r = self.session.get(url, headers=self._headers(), params=params)
        r.raise_for_status()
        elements = r.json().get("elements", [])
        return [{
            "name": e.get("miniProfile", {}).get("firstName", "") + " " + e.get("miniProfile", {}).get("lastName", ""),
            "title": e.get("occupation"),
            "profile_url": f"https://www.linkedin.com/in/{e.get('miniProfile', {}).get('publicIdentifier')}/"
        } for e in elements]
