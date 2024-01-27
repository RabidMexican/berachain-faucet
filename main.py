import os
import time
import random

from dotenv import load_dotenv
from enum import Enum
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


load_dotenv()

URL = 'https://artio.faucet.berachain.com/'
ADDRESS = os.getenv('ADDRESS', None)
INTERVAL = int(os.getenv('INTERVAL', 0))

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument('--start-maximized')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Firefox(options=options)


class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    SUCCESS = 3


def log(text: str, level: LogLevel = LogLevel.INFO):
    print(f'{level.name} : {text}')


def wait(duration: float = 1.0):
    random_seconds = random.uniform((duration / 2), duration)
    time.sleep(random_seconds)


def get_button_by_text(text: str):
    return driver.find_element(by=By.XPATH, value=f'//button[text()="{text}"]')


def print_results():
    try:
        warnings = driver.find_elements(by=By.XPATH, value='//div[@role="alert"]/*')
        if len(warnings):
            for warning in warnings:
                log(warning.text, LogLevel.WARNING)
            return
        log('BERA CLAIMED!', LogLevel.SUCCESS)
    except:
        log('Could not find any messages!', LogLevel.ERROR)


def handle_terms():
    try:
        accept_checkbox = driver.find_element(by=By.ID, value='terms')
        accept_checkbox.click()
        wait()

        log('Terms & conditions tick-box is checked, clicking agree...')

        agree_button = get_button_by_text('I AGREE')
        agree_button.click()
        wait()
    except:
        log('No terms & conditions were found...')


def try_faucet():
    log('Trying Faucet...')
    try:
        log('Fetching page...')
        driver.get(URL)
        wait()

        log('Handling terms & conditions...')
        handle_terms()

        log('Copying address...')
        address_input = driver.find_element(by=By.XPATH, value="//input")
        address_input.send_keys(ADDRESS)
        wait()

        log('Solving Captcha...')
        captcha = get_button_by_text('Click here to prove you are not a bot')
        driver.execute_script("arguments[0].click();", captcha)
        wait()

        log('Claiming tokens...')
        claim_button = get_button_by_text('Drip Tokens')
        claim_button.click()
        wait()

        print_results()

    except Exception as error:
        log('There was a problem loading/interacting with the faucet!', LogLevel.ERROR)
        log(str(error), LogLevel.ERROR)


if __name__ == '__main__':
    if not ADDRESS:
        log('ADDRESS was not set! Shutting-down!', LogLevel.ERROR)
        exit()
    if not INTERVAL:
        log('INTERVAL was not set! Shutting-down!', LogLevel.ERROR)
        exit()
    else:
        while True:
            print('-----------------------------')
            try_faucet()
            log(f'waiting {INTERVAL} seconds...')
            time.sleep(INTERVAL)

