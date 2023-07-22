import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By


def test_admin_area():
    link = "http://localhost:8000/admin/"
    # browser = webdriver.Chrome()
    browser = webdriver.Firefox()
    browser.get(link)

    username_field = browser.find_element(By.XPATH, '//*[@id="id_username"]')
    password_field = browser.find_element(By.XPATH, '//*[@id="id_password"]')
    login_button = browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input')

    username = os.environ["ADMIN_USERNAME"]
    password = os.environ["ADMIN_PASSWORD"]
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    # Assert that the test logged in
    assert (
        browser.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/h1").text
        == "Site administration"
    )
    available_days = browser.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div[1]/div[3]/table/tbody/tr[1]/th/a",
    ).click()

    year_2023 = browser.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div/div/div[2]/details[2]/ul/li[3]/a",
    ).click()

    snow_days = browser.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div/div/div[1]/form/div[2]/table/tbody/tr[1]/td[2]/a",
    ).click()

    input_field = browser.find_element(By.ID, "id_allotted_days")
    allotted_days_value = input_field.get_attribute("value")
    # Assert that Jon Snow has 30 days in year 2023
    assert allotted_days_value == "30"

    browser.quit()
