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


class Scraper:

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    def __init__(self, email, password, start, end):
        self.email = email
        self.password = password
        self.accessor = tk.Tk()
        self.browser = webdriver.Chrome(
            desired_capabilities=Scraper.caps, executable_path=r"C:\\Users\Tanweer\\Downloads\\Compressed\\HackerRank_Scrape-master\\chromedriver.exe")
        self.browser.implicitly_wait(10)
        self.start = start
        self.end = end

    def login(self):
        self.browser.get('https://www.hackerrank.com/dashboard')

        time.sleep(5)

        # elem = self.browser.find_element_by_xpath(
        #     '//*[@id="content"]/div/div/div/div[2]/div[1]/nav/div/div[2]/ul[2]/li[2]/button')

        # elem.click()

        loginbar = self.browser.find_element_by_name("username")
        loginbar.send_keys(self.email)

        passwordbar = self.browser.find_element_by_name("password")
        passwordbar.send_keys(self.password)

        remebermebutton = self.browser.find_element_by_css_selector(
            "input.checkbox-input")
        remebermebutton.click()

        loginbutton = self.browser.find_element_by_css_selector(
            "button.ui-btn.ui-btn-large.ui-btn-primary.auth-button")
        loginbutton.click()

    def go_to_submissions(self):

        profilebutton = self.browser.find_element_by_css_selector(
            "span.mmR.username.text-ellipsis")
        profilebutton.click()

        subs = self.browser.find_element_by_partial_link_text("Submissions")
        subs.click()

    def navigate_and_download(self):

        langauges_dict = {'Java 7': 'java', 'C++': 'cpp', 'MySQL': 'sql', 'C++14': 'cpp', 'C': 'c',
                          'Python 3': 'py', 'Scala': 'scala', 'Oracle': 'oracle'}

        for i in range(self.start, self.end):
            current_page_url = "https://www.hackerrank.com/submissions/all/page/%d" % i
            print(current_page_url)
            self.browser.get(current_page_url)
            time.sleep(0.5)
            for j in range(0, 10):
                print(current_page_url, j)
                list_subs = self.browser.find_elements_by_css_selector(
                    "a.challenge-slug.backbone.root")
                list_subs_lang = self.browser.find_elements_by_css_selector(
                    "p.small")
                particular_sub_driver = list_subs[j]
                particular_sub_lang_driver = list_subs_lang[4*j]
                challege_name = particular_sub_driver.text
                lang_coded_in = particular_sub_lang_driver.text
                print(challege_name, lang_coded_in)

                if lang_coded_in in langauges_dict:
                    lang_ext = langauges_dict[lang_coded_in]
                else:
                    lang_ext = lang_coded_in

                save_file_name = challege_name + '.' + lang_ext

                try:
                    particular_sub_driver.click()
                    challege_tabs = self.browser.find_elements_by_css_selector(
                        "span.ui-icon-label")
                    time.sleep(0.5)
                    subs_tab = challege_tabs[1].click()
                    time.sleep(0.5)
                    view_results = self.browser.find_element_by_css_selector(
                        'a.text-link').click()
                    time.sleep(0.5)

                    if ((len(self.browser.find_elements_by_css_selector("span.cm-keyword"))) != 0):
                        text_box = self.browser.find_element_by_css_selector(
                            "span.cm-keyword")
                    elif ((len(self.browser.find_elements_by_css_selector("span.cm-variable"))) != 0):
                        text_box = self.browser.find_element_by_css_selector(
                            "span.cm-variable")
                    elif ((len(self.browser.find_elements_by_css_selector("span.cm-meta"))) != 0):
                        text_box = self.browser.find_element_by_css_selector(
                            "span.cm-meta")

                    time.sleep(0.5)
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
                    print(
                        'Selenium StaleElementReferenceException.')
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
                print('Success')

                self.browser.get(current_page_url)
                time.sleep(0.5)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--start', type=int,
                        default=4, help="start index")
    parser.add_argument('-e', '--end', type=int, default=7, help="end index")
    args = parser.parse_args()
    print('---------START---------')

    if not os.path.exists('./results'):
        os.mkdir('./results')

    email, password = get_cred.get_credentials()

    instance = Scraper(email, password, args.start, args.end)
    time.sleep(5)
    instance.login()
    time.sleep(5)
    # instance.go_to_submissions()
    time.sleep(5)
    instance.navigate_and_download()

print('---------DONE---------')
