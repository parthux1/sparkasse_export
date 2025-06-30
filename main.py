"""Login to Sparkasse EE online banking and download transaction history (default time on website = 3 months).
Used webdriver: firefox at default snap installation path
Exit codes:
0: Downlaod sucessfull
1: unspecified error. might be: config.yaml not found
2: login failed due to oauth2 timeout
"""

CONFIG_FILE = 'config.yaml'

# credentials
import yaml
# selenium
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

import sys  # early exit
import os  # concat os paths
import pathlib  # get current path

# logging
import logging
from datetime import datetime

# sleep timer
import tqdm
from time import sleep

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

print(f'loading config from {CONFIG_FILE}')
with open(CONFIG_FILE, 'r') as ymlfile:
    CONFIG = yaml.safe_load(ymlfile)
    CREDENTIALS = CONFIG['personal']
    CONF_SCRIPT = CONFIG['script']

print(f'finished. Initialising logger')

formatter = logging.Formatter('[%(asctime)s|%(levelname)s] %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
handler_console = logging.StreamHandler()
handler_console.setFormatter(formatter)

FILE_NAME = CONF_SCRIPT['log_path'] + '/' + datetime.now().strftime('%Y-%m%-d_%H-%M-%S.log')
handler_file = logging.FileHandler(FILE_NAME, mode='w+')
handler_file.setFormatter(formatter)

logger.addHandler(handler_console)
logger.addHandler(handler_file)
logger.info('Logger initialized')

DRIVER_LOC = os.path.join(CONF_SCRIPT['firefox_install_path'], "geckodriver")
BINARY_LOC = os.path.join(CONF_SCRIPT['firefox_install_path'], "firefox")

logger.info(f'Using firefox driver at: {DRIVER_LOC}')
logger.info(f'Using firefox binary at: {BINARY_LOC}')
logger.info(f'Debug mode: {CONF_SCRIPT["debug"]}')

# setup driver
service = Service(DRIVER_LOC)
opts = Options()
opts.binary_location = BINARY_LOC

FULL_DOWNLOAD_PATH = str(pathlib.Path().resolve()) + '/' + CONF_SCRIPT['download_path']
if not CONF_SCRIPT['debug']:
    opts.add_argument('-headless')  # don't display firefox window

opts.set_preference('browser.download.dir', FULL_DOWNLOAD_PATH)  # custom download path
opts.set_preference("browser.download.folderList", 2)  # use custom download path

driver = Firefox(service=service, options=opts)
logger.info(f'Driver started with\noptions: {opts.arguments}\npreferences: {opts.preferences}')

# login
driver.get(CONF_SCRIPT['website_url'])

# decline cookies
logger.info('Declining cookies.')
driver.find_element(By.CLASS_NAME, 'secondary').click()

# id for username & password input are randomized each time. Access them by other unique mappings
# both can be accessed using their label. It references the input-id with its 'for' attribute

# username
logger.info('Entering username')
driver.find_element(By.CLASS_NAME, 'nbf-text-input').send_keys(CREDENTIALS['username'])
XPATH_CONTINUE_BTN = '//input[@value="Weiter" and @title="Weiter"]'
driver.find_element(By.XPATH, XPATH_CONTINUE_BTN).click()

# password
INPUT_PW_TEXT = CONFIG['script']['input_password_label_text']
logger.info('Entering password')
XPATH_STR_PW = f'//label[text()="{INPUT_PW_TEXT}"]'
WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, XPATH_STR_PW))).click()
WEB_ID_PW = driver.find_element(By.XPATH, XPATH_STR_PW).get_attribute('for')

driver.find_element(By.ID, WEB_ID_PW).send_keys(CREDENTIALS['password'])
XPATH_LOGIN_BTN = '//input[@value="Anmelden" and @title="Anmelden"]'
driver.find_element(By.XPATH, XPATH_LOGIN_BTN).click()

logger.info(f'Waiting for 2auth. Timeout in {CREDENTIALS["2auth_timeout"]} seconds')
try:
    # wait till 2auth completion
    WebDriverWait(driver, CREDENTIALS['2auth_timeout']).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'mkp-notification-header-headline')))
    XPATH_2AUTH_CONTINUE_BTN = '//input[@value="Weiter" and @title="Weiter"]'
    driver.find_element(By.XPATH, XPATH_2AUTH_CONTINUE_BTN).click()

except TimeoutException:
    logger.warning(f'hit timeout. Exiting.')
    sys.exit(2)



logger.info('Waiting for potential overlay-popup.')
try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@title="Schliessen"]'))).click()
except TimeoutException:
    logger.warning(f'hit timeout. Continuing.')

logger.info('Selecting bank account.')

XPATH_STR = f'//div[@data-iban="{CREDENTIALS["iban"]}"]'
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_STR))).click()

BUTTON_EXPORT_TEXT = CONFIG['script']['button_export_span_text']
logger.info('Opening export area.')
driver.find_element(By.XPATH, f'//button/span[contains(text(), "{BUTTON_EXPORT_TEXT}")]').click()


logger.info('Triggering export')
XPATH_STR = f'//span[text()="{CREDENTIALS["export_text"]}"]'

try:
    export_span = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, XPATH_STR)))
    export_span.find_element(By.XPATH, '..').click()
except TimeoutException:
    logger.error(f'Element with text "{CREDENTIALS["export_text"]}" not found.')


if not CONF_SCRIPT['debug']:
    logger.info('Sleeping 5 seconds for download to finish before logging out.')
    for i in tqdm.tqdm(range(0, 5)):
        sleep(1)

    # logout button has no id or class. Navigate to it using its span
    logout_span = driver.find_element(By.XPATH, '//span[text()="Abmelden"]')
    logout_span.find_element(By.XPATH, '..').click()

    driver.close()

logger.info('Script finished.')
