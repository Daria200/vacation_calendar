import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def test_admin_area():
    link = "http://localhost:8000/admin/"

    # browser = webdriver.Chrome()

    driver = webdriver.Firefox()
    driver.get(link)

    username_field = driver.find_element(By.XPATH, '//*[@id="id_username"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="id_password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input')

    # TODO:remove it
    time.sleep(1)

    username = os.environ["ADMIN_USERNAME"]
    password = os.environ["ADMIN_PASSWORD"]
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    # TODO:remove it
    time.sleep(1)
    # Assert that the test logged in
    assert (
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/h1").text
        == "Site administration"
    )

    available_days = driver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div[1]/div[3]/table/tbody/tr[1]/th/a",
    ).click()

    year_2023 = driver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div/div/div[2]/details[2]/ul/li[3]/a",
    ).click()

    snow_days = driver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div/div/div[1]/form/div[2]/table/tbody/tr[1]/td[2]/a",
    ).click()
    # TODO:remove it
    time.sleep(1)

    input_field = driver.find_element(By.ID, "id_allotted_days")
    allotted_days_value = input_field.get_attribute("value")
    # Assert that Jon Snow has 30 days in year 2023
    assert allotted_days_value == "30"
    # TODO:remove it
    time.sleep(1)
    driver.quit()


def test_add_and_delete_row():
    link = "http://localhost:8000/admin/"
    # driver = webdriver.Chrome()
    driver = webdriver.Firefox()
    driver.get(link)

    username_field = driver.find_element(By.XPATH, '//*[@id="id_username"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="id_password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input')

    # TODO:remove it
    time.sleep(1)
    username = os.environ["ADMIN_USERNAME"]
    password = os.environ["ADMIN_PASSWORD"]
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
    # TODO:remove it
    time.sleep(1)

    # Assert that the test logged in
    assert (
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div[1]/h1").text
        == "Site administration"
    )

    # open available days table
    available_days_table = driver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[1]/div[1]/div[3]/table/tbody/tr[1]/th/a",
    ).click()

    # TODO:remove it
    time.sleep(1)

    # delete row with Jon Snow in 2022:
    # Pick year 2022:
    # TODO: it won't work if there are more elements
    year_2022 = driver.find_element(
        By.XPATH, '//*[@id="changelist-filter"]/details[2]/ul/li[2]/a'
    ).click()
    filter_jon_snow = driver.find_element(
        By.XPATH, '//*[@id="changelist-filter"]/details[1]/ul/li[5]/a'
    ).click()

    # Pick Jon Snow:
    jon_snow = driver.find_element(
        By.XPATH, '//*[@id="result_list"]/tbody/tr[1]/th/a'
    ).click()

    # TODO:remove it
    time.sleep(1)

    # delete Jon Snow for year 2022:
    delete_jon_snow = driver.find_element(
        By.XPATH, '//*[@id="availabledays_form"]/div/div/a'
    ).click()
    confirm_delete = driver.find_element(
        By.XPATH, "/html/body/div/div[2]/div/div[1]/form/div/input[2]"
    ).click()

    # Add a new row for Jon Snow in 2022
    # click add available days
    add_available_days = driver.find_element(
        By.XPATH, '//*[@id="content-main"]/ul/li/a'
    ).click()

    # choose the name Jon Snow
    selector = driver.find_element(By.XPATH, '//*[@id="id_employee"]').click()
    Select(driver.find_element(By.TAG_NAME, "select")).select_by_visible_text(
        "Jon Snow"
    )

    # Type in 20 days
    input_field_allotted_days = driver.find_element(
        By.XPATH, '//*[@id="id_allotted_days"]'
    )
    input_field_allotted_days.clear()
    input_field_allotted_days.send_keys(20)

    # Pick the year 2022
    input_field_year = driver.find_element(By.XPATH, '//*[@id="id_year"]').send_keys(
        2022
    )
    # TODO:remove it
    time.sleep(1)

    # Save
    save_button = driver.find_element(
        By.XPATH, '//*[@id="availabledays_form"]/div/div/input[1]'
    ).click()
    # TODO:remove it
    time.sleep(1)

    # TODO: assert Jon Snow has 20 days in 2022

    # Close the browser
    driver.quit()
