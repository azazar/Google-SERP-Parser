import argparse
import urllib
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import anticaptcha
import json


class Google:

    def __init__(self, proxy=None, headless=False):
        options = uc.ChromeOptions()

        if proxy is not None:
            options.add_argument('--proxy-server={}'.format(proxy))

        options.headless = headless

        # Enable headless mode if there is no X server
        if os.environ.get('DISPLAY') is None:
            headless = True

            print('Warning: DISPLAY environment variable is not set. Headless mode enabled. It is experimental and not guaranteed to work.')

        self.driver = None

        if anticaptcha.key_available():
            self.driver = anticaptcha.open_undetected_chrome('https://google.com/', options=options)
        else:
            self.driver = uc.Chrome(options)

            self.driver.get('https://google.com/')

        self.wait = WebDriverWait(self.driver, 30)

        self.wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, 'span>div[class][id]>div[class]>div[class]>div[class]>button'))

        buttons = self.driver.find_elements(By.CSS_SELECTOR, 'span>div[class][id]>div[class]>div[class]>div[class]>button')

        buttons[1].click()

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def parse_serp(self, query):
        url = 'https://google.com/search?q={}'.format(urllib.parse.quote(query))

        self.driver.get(url)

        results = list()
        next_page = 1

        while True:
            self.wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, 'a h3'))

            for h3 in self.driver.find_elements(By.CSS_SELECTOR, 'a h3'):
                a = h3.find_element(By.XPATH, '..')

                title = h3.text
                url = a.get_attribute('href')

                try:
                    snippet = h3.find_element(By.XPATH, '../../../..//span/em/..').text
                except:
                    snippet = None

                results.append({'title': title, 'url': url, 'snippet': snippet})

            next_page = next_page + 1

            found = False
            for a in self.driver.find_elements(By.CSS_SELECTOR, 'td a[aria-label]'):
                label = a.get_attribute('aria-label')
                if label == 'Page {}'.format(next_page):
                    a.click()
                    found = True
                    break

            if not found:
                return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google SERP Parser')
    parser.add_argument('-o', '--output', help='Output File', required=False)
    parser.add_argument('-p', '--proxy', help='Proxy Address', required=False)
    parser.add_argument('-e', '--headless', help='Headless Mode', action='store_true', required=False, default=False)
    parser.add_argument('arg',
                        type=str,
                        nargs='*',
                        help='Queries to parse')

    args = vars(parser.parse_args())
    output_file = args['output']

    if len(args['arg']) > 0:
        goog = Google(args['proxy'], args['headless'])
        for query in args['arg']:
            try:
                results = goog.parse_serp(query)

                for link in results:
                    print(link)

                if output_file is not None:
                    # ext is .json
                    if output_file[-5:] == '.json':
                        with open(output_file, 'a') as f:
                            f.write(json.dumps(results))
                    else:
                        with open(output_file, 'a') as f:
                            for link in results:
                                f.write(link['url'] + '\t' + link['title'] + '\n')

            except Exception as e:
                print('{}: {}'.format(query, e))
    else:
        print('No query provided')
