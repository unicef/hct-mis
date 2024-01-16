import pytest
from time import sleep
from selenium.webdriver.common.by import By

from helpers.hope import HOPE

class TestAdminPanel(HOPE):

    def test_login(self):
        self.browser.get(f"{self.live_server_url}/api/unicorn/")
        self.wait_for(locator="id_username").send_keys('wrong1')
        self.get(locator="id_password").send_keys('wrong1')
        self.get(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
        self.wait_for(By.CLASS_NAME, "errornote")