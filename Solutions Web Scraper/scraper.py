import os
from getpass import getpass
import get_cred
import time
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import argparse
import multiprocessing


class Scraper:

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    def __init__(self, email, password, start, end):
        self.email = email
        self.password = password
        self.accessor = tk.Tk()

        # Replace 'executable_path' with path of 'chromedriver' in your PC

        self.browser = webdriver.Chrome(
            desired_capabilities=Scraper.caps,
            executable_path="./chromedriver.exe")
        self.browser.implicitly_wait(10)
        self.start = start
        self.end = end

    def login(self):
        self.browser.get('https://www.hackerrank.com/auth/login')
        time.sleep(5)
        loginbar = self.browser.find_element_by_id("input-1")
        loginbar.send_keys(self.email)

        passwordbar = self.browser.find_element_by_id("input-2")
        passwordbar.send_keys(self.password)

        remebermebutton = self.browser.find_element_by_css_selector(
            "input.checkbox-input")
        remebermebutton.click()

        loginbutton = self.browser.find_element_by_css_selector(
            "button.ui-btn.ui-btn-large.ui-btn-primary.auth-button")
        loginbutton.click()

    def go_to_submissions(self):

        profilebutton = self.browser.find_element_by_xpath(
            "/html/body/div[4]/div/div/div/div/div[1]/nav/div/div[2]/ul[2]/li[3]/div")
        profilebutton.click()

        subs = self.browser.find_element_by_partial_link_text("Submissions")
        subs.click()

    def navigate_and_download(self):

        langauges_dict = {'Java 7': 'java', 'C++': 'cpp', 'MySQL': 'sql',
                          'C++14': 'cpp', 'C': 'c',
                          'Python 3': 'py', 'Scala': 'scala',
                          'Oracle': 'oracle'}

        for i in range(self.start, self.end):
            current_page_url = f"""https://www.hackerrank.com/submissions/all/page/{i}"""
            print("----------------")
            print("<- CURRENT PAGE -> ", current_page_url)
            print("----------------")
            self.browser.get(current_page_url)
            time.sleep(4)
            for j in range(0, 10):
                print(current_page_url, "<- At submission number ->", j)
                time.sleep(4)
                list_subs = self.browser.find_elements_by_css_selector(
                    "a.challenge-slug.backbone.root")
                list_subs_lang = self.browser.find_elements_by_css_selector(
                    "p.small")
                particular_sub_driver = list_subs[j]
                particular_sub_lang_driver = list_subs_lang[4*j]
                challege_name = particular_sub_driver.text
                lang_coded_in = particular_sub_lang_driver.text
                print("Challenge -> ", challege_name,
                      "<- Lang ->", lang_coded_in)

                if lang_coded_in in langauges_dict:
                    lang_ext = langauges_dict[lang_coded_in]
                else:
                    lang_ext = lang_coded_in

                save_file_name = challege_name + '.' + lang_ext

                try:
                    particular_sub_driver.click()
                    challege_tabs = self.browser.find_elements_by_css_selector(
                        "span.ui-icon-label")
                    time.sleep(1)
                    subs_tab = challege_tabs[1].click()
                    time.sleep(1)
                    view_results = self.browser.find_element_by_css_selector(
                        'a.text-link').click()
                    time.sleep(1)

                    if ((len(self.browser.find_elements_by_css_selector("span.cm-keyword"))) != 0):
                        text_box = self.browser.find_element_by_css_selector(
                            "span.cm-keyword")
                    elif ((len(self.browser.find_elements_by_css_selector("span.cm-variable"))) != 0):
                        text_box = self.browser.find_element_by_css_selector(
                            "span.cm-variable")
                    elif ((len(self.browser.find_elements_by_css_selector("span.cm-meta"))) != 0):
                        text_box = self.browser.find_element_by_css_selector(
                            "span.cm-meta")

                    time.sleep(1)
                    actions = ActionChains(self.browser)
                    actions.move_to_element(text_box)
                    actions.click()
                    actions.key_down(Keys.LEFT_CONTROL).send_keys(
                        "a").key_up(Keys.LEFT_CONTROL)
                    actions.key_down(Keys.LEFT_CONTROL).send_keys(
                        "c").key_up(Keys.LEFT_CONTROL)
                    actions.perform()

                    code = None
                    while code is None:
                        try:
                            code = self.accessor.clipboard_get()
                        except tk.TclError:
                            print('Tkinter TclError.')
                            exit()

                except (exceptions.StaleElementReferenceException):
                    print('Selenium StaleElementReferenceException.')
                    continue

                lang_used = langauges_dict.get(lang_coded_in)

                if lang_used is None:
                    lang_used = lang_coded_in

                lang_specific_dir = './results/' + lang_used

                if not os.path.exists(lang_specific_dir):
                    os.mkdir(lang_specific_dir)

                text_file = open(lang_specific_dir + '/' + save_file_name, 'w')
                text_file.write(code)
                text_file.close()
                print('Successfully scraped')

                self.browser.get(current_page_url)
                time.sleep(1)


def run(email, password, start, end):
    instance = Scraper(email, password, start, end)
    time.sleep(7)
    instance.login()
    time.sleep(7)
    instance.go_to_submissions()
    time.sleep(7)
    instance.navigate_and_download()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start', type=int,
                        required=True, help="start index")
    parser.add_argument('-e', '--end', type=int,
                        required=True, help="end index")
    parser.add_argument('-n', '--cores', type=int,
                        default=1, help="number of cores")

    args = parser.parse_args()
    print('---------START---------')

    if not os.path.exists('./results'):
        os.mkdir('./results')

    email, password = get_cred.get_credentials()

    list_data = []

    for i in range(args.start, args.end, int((args.end)/args.cores)):
        list_data.append([email, password, int(
            i), int(i+((args.end)/args.cores))])
    list_data[-1][3] = args.end

    with multiprocessing.Pool(processes=args.cores) as pool:
        pool.starmap(run, list_data)

    print('---------DONE---------')
