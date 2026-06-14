import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

USERNAME = os.getenv("TEST_USERNAME")
PASSWORD = os.getenv("TEST_PASSWORD")

BASE_URL = "http://localhost:5000"


def get_driver():
    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        )
    )

    driver.implicitly_wait(5)

    return driver


def test_valid_login():

    driver = get_driver()

    driver.get(f"{BASE_URL}/login")

    driver.find_element(
        By.ID,
        "username"
    ).send_keys(USERNAME)


    driver.find_element(
        By.ID,
        "password"
    ).send_keys(PASSWORD)

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    
    assert "/login" not in driver.current_url

    driver.quit()


def test_invalid_login():

    driver = get_driver()

    driver.get(f"{BASE_URL}/login")

    driver.find_element(
        By.ID,
        "username"
    ).send_keys("fakeuser123")

    driver.find_element(
        By.ID,
        "password"
    ).send_keys("wrongpassword123")
    
    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

 
    assert "/login" in driver.current_url

    page_source = driver.page_source.lower()

    assert "incorrect" in page_source

    driver.quit()