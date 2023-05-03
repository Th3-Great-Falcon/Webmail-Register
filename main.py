import random
import string
import json
import os
import logging
import time
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep

def load_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except Exception as e:
        logging.error(f"Error loading file '{filepath}': {e}")
        return []

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except (IOError, FileNotFoundError) as e:
        logging.error(f"Error loading configuration file: {e}")
        return {}

def shuffle_and_choose(lst):
    random.shuffle(lst)
    return random.choice(lst)

def random_scroll(driver):
    scroll_actions = [webdriver.ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN) for _ in range(random.randint(1, 3))]
    random.shuffle(scroll_actions)
    for action in scroll_actions:
        action.perform()
        time.sleep(random.uniform(0.5, 1.5))

def type_with_delay(element, text, delay_range):
    for character in text:
        element.send_keys(character)
        random_delay(delay_range)

def random_first_name(config):
    return random.choice(config['first_names'])

def random_last_name(config):
    return random.choice(config['last_names'])

def random_birthday():
    day = str(random.randint(1, 9)).zfill(2)
    return day

def random_birthyear():
    return random.randint(1970, 2002)

def random_password(min_length=12, max_length=16):
    length = random.randint(min_length, max_length)
    characters = string.ascii_letters + string.digits + "$%^@%#()"
    return ''.join(random.choice(characters) for _ in range(length))

def setup_webdriver(config, user_agents, proxies):
    # Initialize the browser instance outside the loop
    options = uc.ChromeOptions()
    # Create a UserAgent instance
    ua = UserAgent()
    # options.add_argument("--headless")
    proxy = shuffle_and_choose(proxies)
    options.add_argument(f'user-agent={ua.random}')
    options.add_argument("--mute-audio")
    options.add_argument("--verify_ssl=False")
    options.add_argument(f'--proxy-server=http://{shuffle_and_choose(proxies)}')
    
    try:
        driver = uc.Chrome(executable_path=config['chromedriver_path'], options=options)
        return driver
    except Exception as e:
        logging.error(f"Error setting up webdriver: {e}")
        return None

def random_delay(delay_range):
    delay = random.uniform(*delay_range)
    sleep(delay)

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def random_digits(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

def fill_form(driver, config):
    name = random_first_name(config)
    last_name = random_last_name(config)
    birthday = random_birthday()
    birthyear = random_birthyear()
    account_name = f"{last_name}.{name}{random_digits(3)}"
    password = random_string(14)
    random_scroll(driver)
    delays = config['delays']

    # Locate input elements by their class names
    name_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']._2E5ne4oz8oud2n")
    last_name_input = driver.find_elements(By.CSS_SELECTOR, "input[type='text']._2E5ne4oz8oud2n")[1]
    birthday_input = driver.find_element(By.CSS_SELECTOR, "#birthdayDay")
    birthyear_input = driver.find_element(By.CSS_SELECTOR, "#birthdayYear")
    account_name_input = driver.find_elements(By.CSS_SELECTOR, "input[type='text']._2E5ne4oz8oud2n")[2]
    password_input = driver.find_element(By.ID, "password")
    repeat_password_input = driver.find_element(By.ID, "rePassword")

    # Fill the input fields with delays
    type_with_delay(name_input, name, config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])
    type_with_delay(last_name_input, last_name, config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])
    type_with_delay(birthday_input, birthday, config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])
    type_with_delay(birthyear_input, str(birthyear), config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])
    type_with_delay(account_name_input, account_name, config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])

    # Open the month dropdown
    try:
        month_dropdown = driver.find_element(By.CSS_SELECTOR, 'div.account-input-container.account-select:nth-child(2) input.fake-input')
    except NoSuchElementException as e:
        logging.error(f"Error locating element: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return

    driver.execute_script("arguments[0].click();", month_dropdown)
    random_delay(config['delays']['between_actions'])

    # Select a random month using keyboard interactions
    actions = ActionChains(driver)
    down_arrow_count = random.randint(1, 12)
    for _ in range(down_arrow_count):
        actions.send_keys(Keys.ARROW_DOWN)
        random_delay(config['delays']['between_actions'])

    actions.send_keys(Keys.ENTER)
    actions.perform()

    type_with_delay(password_input, password, config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])

    #password_input.send_keys(password)
    #random_delay(config['delays']['between_actions'])

    type_with_delay(repeat_password_input, password, config['delays']['between_keys'])
    random_delay(config['delays']['between_actions'])

    #repeat_password_input.send_keys(password)
    #random_delay(config['delays']['between_actions'])

    # Open the gender dropdown
    try:
        gender_dropdown = driver.find_element(By.XPATH, '//div[@class="account-input-container account-select"]/div[contains(@class, "account-input")]')
    except NoSuchElementException as e:
        logging.error(f"Error locating element: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return

    driver.execute_script("arguments[0].click();", gender_dropdown)
    random_delay(config['delays']['between_actions'])

    # Select a random gender using keyboard interactions
    actions = ActionChains(driver)
    down_arrow_count = random.randint(1, 2)
    for _ in range(down_arrow_count):
        actions.send_keys(Keys.ARROW_DOWN)
        random_delay(config['delays']['between_actions'])

    actions.send_keys(Keys.ENTER)
    actions.perform()

    # Click the checkbox
    checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][name="agreementacceptAll-acceptAll"]')
    driver.execute_script("arguments[0].click();", checkbox)
    random_delay(config['delays']['between_actions'])

def click_submit(driver, config):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='btn']"))
        )
        random_scroll(driver)
        random_scroll(driver)
        driver.find_element(By.XPATH, "//button[@class='btn']").click()
    except:
        logging.error("Submit Button not found")

def accept_popup(driver, config):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@class='rodo-popup-agree']"))
        )
        driver.find_element(By.XPATH, "//button[@class='rodo-popup-agree']").click()
    except:
        print("Popup not found")


def create_account(driver, config):
    fill_form(driver, config)
    sleep(random.uniform(*config['delays']['after_submit']))

def solve_captcha(api_key, site_key, login_url):
    captcha_api_url = "http://2captcha.com/in.php"
    payload = {
        "key": api_key,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": login_url,
        "json": 1
    }

    response = requests.get(captcha_api_url, params=payload)
    print(f"Initial captcha response: {response.text}")

    result = response.json()

    if result["status"] == 1:
        captcha_id = result["request"]
        result_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1"

        time.sleep(30)  # Add this line for the recommended delay

        while True:
            res = requests.get(result_url)
            result = res.json()

            print(f"Intermediate captcha response: {result}")

            if result["status"] == 1:
                return result["request"]
            elif result["request"] == "ERROR_CAPTCHA_UNSOLVABLE":
                return None

            time.sleep(5)
    
def input_captcha_solution(driver, captcha_solution):
    try:
        # Switch to the reCAPTCHA iframe
        iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        driver.switch_to.frame(iframe)

        # Locate the captcha input element (change the selector according to the website)
        captcha_input = driver.find_element(By.ID, "g-recaptcha-response")

        # Fill the input field with the captcha_solution
        type_with_delay(captcha_input, captcha_solution)

        # Switch back to the main content
        driver.switch_to.default_content()

    except NoSuchElementException:
        print("Error: Unable to locate the captcha input element or iframe.")


def run_account_creation(config):
    api_key = '04f7b1c2f6fa064f5f3f0107ab3699d5'
    site_key = '6LcGdmcUAAAAAKFJ8sYv7Gd6U4z6BvkpTcRzHDOY'
    
    captcha_solution = None
    for attempt in range(3):
        captcha_solution = solve_captcha(api_key, site_key, config['login_url'])
        if captcha_solution is not None:
            break
        if attempt < 2:  # Skip sleep after the last attempt
            print(f"Retrying captcha solving in 15 seconds... (Attempt {attempt + 1})")
            time.sleep(15)
    
    if captcha_solution is None:
        logging.error("Captcha solving failed.")
        return

    user_agents = load_file(os.path.join(config['user_agents_file']))
    proxies = load_file(os.path.join(config['proxies_file']))

    driver = setup_webdriver(config, user_agents, proxies)

    if driver is None:
        logging.error("Unable to start account creation due to webdriver setup failure.")
        return

    driver.get(config['login_url'])

    accept_popup(driver, config)
    input_captcha_solution(driver, captcha_solution)
    create_account(driver, config)
    click_submit(driver, config)
    input("Press Enter to close the browser...")

    driver.quit()


def main():
    config = load_config()
    run_account_creation(config)

main()
