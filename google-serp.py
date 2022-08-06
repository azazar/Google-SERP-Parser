import argparse
import urllib
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import anticaptcha
import json
import sys


class Google:

    def __init__(self, proxy=None, headless=False):
        options = uc.ChromeOptions()

        chrome_version = get_chrome_major_version()

        if proxy is not None:
            options.add_argument('--proxy-server={}'.format(proxy))

        options.headless = headless

        if headless:
            sys.stderr.write('Warning: Headless mode enabled. It is experimental and not guaranteed to work.\n')
        # Enable headless mode if there is no X server
        elif os.environ.get('DISPLAY') is None:
            options.headless = True

            sys.stderr.write('Warning: DISPLAY environment variable is not set. Headless mode enabled. It is experimental and not guaranteed to work.\n')

        self.driver = None

        if anticaptcha.key_available():
            self.driver = anticaptcha.open_undetected_chrome('https://google.com/', options=options, version_main=chrome_version)
        else:
            self.driver = uc.Chrome(options, version_main=chrome_version)

            self.driver.get('https://google.com/')

        self.wait = WebDriverWait(self.driver, 30)

        selector = 'span>div>div>div>div>div>button'

        self.wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, selector))

        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)

        buttons[1].click()

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def parse_serp(self, query, max_page=100):
        url = 'https://google.com/search?q={}'.format(urllib.parse.quote(query))

        self.driver.get(url)

        results = list()
        next_page = 1

        while True:
            self.wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, 'a h3'))

            position = 0

            for h3 in self.driver.find_elements(By.CSS_SELECTOR, 'a h3'):
                a = h3.find_element(By.XPATH, '..')

                title = h3.text
                url = a.get_attribute('href')

                try:
                    snippet = h3.find_element(By.XPATH, '../../../..//span/em/..').text
                except:
                    snippet = None

                position = position + 1

                result = {
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'query': query,
                    'page': next_page,
                    'position': position,
                }

                results.append(result)

            next_page = next_page + 1

            if next_page > max_page:
                return results

            found = False
            for a in self.driver.find_elements(By.CSS_SELECTOR, 'td a[aria-label]'):
                label = a.get_attribute('aria-label')
                if label == 'Page {}'.format(next_page):
                    a.click()
                    found = True
                    break

            if not found:
                return results


def get_chrome_major_version():
    output = os.popen('chromium-browser --version').read().split(' ')

    if output[0] == 'Chromium':
        return output[1].split('.')[0]

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google SERP Parser')
    parser.add_argument('-o', '--output', help='Output File', required=False)
    parser.add_argument('-l', '--limit', help='Max Number of Pages', required=False)
    parser.add_argument('-p', '--proxy', help='Proxy Address', required=False)
    parser.add_argument('-e', '--headless', help='Headless Mode', action='store_true', required=False, default=False)
    parser.add_argument('arg',
                        type=str,
                        nargs='*',
                        help='Queries to parse')

    args = vars(parser.parse_args())
    output_file = args['output']
    if 'limit' in args:
        page_limit = int(args['limit'])
    else:
        page_limit = 100

    if len(args['arg']) > 0:
        goog = Google(args['proxy'], args['headless'])
        for query in args['arg']:
            try:
                results = goog.parse_serp(query, page_limit)

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
