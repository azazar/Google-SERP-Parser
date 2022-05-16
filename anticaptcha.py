#!/usr/bin/python3

# Required:
# - undetected-chromedriver==3.1.5.post4
import os
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time
import json


# The API messages sending directly to the plugin
# For example for the anti-captcha.com API key init which is required for the plugin work
# Works only on the normal HTML web page
# https://antcpt.com/blank.html in our case
# Won't work on pages like about:blank etc
def acp_api_send_request(driver, message_type, data={}):
    message = {
        # this receiver has to be always set as antiCaptchaPlugin
        'receiver': 'antiCaptchaPlugin',
        # request type, for example setOptions
        'type': message_type,
        # merge with additional data
        **data
    }
    # run JS code in the web page context
    # preceicely we send a standard window.postMessage method
    return driver.execute_script("""
    return window.postMessage({});
    """.format(json.dumps(message)))


def key_available():
    return os.path.exists('anti-captcha.key')


def open_undetected_chrome(url='https://antcpt.com/blank.html', options=None):
    extension_download_url = 'https://antcpt.com/downloads/anticaptcha/chrome/anticaptcha-plugin_v0.62.zip'
    extension_path = 'anticaptcha-plugin'
    extension_abs_path = '{}/{}'.format(os.getcwd(), extension_path)

    # Load key from file
    anticaptcha_key = open('anti-captcha.key', 'r').readline()

    # Init the chrome options object for connection the extension
    if options is None:
        options = webdriver.ChromeOptions()

    # A full path to CRX or ZIP or XPI file which was downloaded earlier
    options.add_argument('--load-extension={}'.format(extension_abs_path))

    # Download the extension from the web if it doesn't exist
    if not os.path.exists(extension_path):
        os.mkdir(extension_path)
        os.system('cd {} && wget {} -O plugin.zip && unzip plugin.zip; rm plugin.zip'.format(extension_path,
                                                                                             extension_download_url))

    browser = uc.Chrome(options=options)

    browser.get(url)

    # Setting up the anti-captcha.com API key
    acp_api_send_request(
        browser,
        'setOptions',
        {'options': {'antiCaptchaApiKey': anticaptcha_key}}
    )

    # 3 seconds pause
    time.sleep(3)

    return browser


if __name__ == '__main__':
    # Run the browser (Chrome WebDriver) with passing the full path to the downloaded WebDriver file
    browser = open_undetected_chrome()

    # Go to the test form with reCAPTCHA 2
    browser.get('https://antcpt.com/rus/information/demo-form/recaptcha-2.html')

    # Test input
    browser.find_element_by_name('demo_text').send_keys('Test input')

    # Most important part: we wait upto 120 seconds until the AntiCaptcha plugin indicator with antigate_solver class
    # gets the solved class, which means that the captcha was successfully solved
    WebDriverWait(browser, 120).until(lambda x: x.find_element_by_css_selector('.antigate_solver.solved'))

    # Sending form
    browser.find_element_by_css_selector('input[type=submit]').click()
