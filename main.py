from http import cookies
import time
from PIL import Image
import io
import schedule
import requests, sys, getpass, shutil, json, time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import recognition as recog
import configparser
login_url = "https://sports.tms.gov.tw/member/?U=login"
valid_img_path = "./validation.png"
browserIsOpen = True


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        log(question + prompt, False)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def log(to_print, verbose=True):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("./log.txt", 'a') as f:
        f.write("[%s] : %s\n" % (timestamp, to_print))
    if verbose:
        print("[%s] : %s" % (timestamp, to_print))

def get_credentials():
        config = configparser.ConfigParser()
        config.read('my_config.ini')
        username = config.get('Stan', 'username')
        password = config.get('Stan', 'password')
        return username , password

class Court_Reservation:
    def __init__(self):
        self.password = str()
        self.username = str()
        op = webdriver.ChromeOptions()
        if not query_yes_no("Do you want to run the program with browser open?"):
            op.add_argument('headless')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=op)
        self.authenticated = False
        self.retry_interval = 0.5
        self.date_str = str()
        self.start_time = str()
        self.end_time = str()
        self.place_seq = str()
        self.num = str()        
        self.time_str = str()
        self.data = dict()
        self.rec = recog.recognition()
        self.session = requests.Session()
        self.validation_code = 0
    def get_confirmation_code(self):
        confidence = 0
        validation_code = ""
        im = self.get_validation_img()
        validation_code, confidence = self.rec.recognition(im) 
        while confidence < 0.8 or (any(c.isalpha() for c in validation_code)):
            self.renew_validation_img()
            im = self.get_validation_img()
            #type: string, tensor
            validation_code, confidence = self.rec.recognition(im) 
        self.validation_code = validation_code

    def get_validation_img(self):
        ChkImg_element = self.driver.find_element(By.ID, "ChkImg")
        ChkImg_element.screenshot(valid_img_path)
        Img = Image.open(valid_img_path)
        # print(img.format, img.size, img.mode)
        return Img

    def renew_validation_img(self):
        renew_botton = self.driver.find_element(By.CSS_SELECTOR, "#Form > div:nth-child(3) > label > div.Content > button:nth-child(3)")
        renew_botton.click()
        time.sleep(0.5)

    def login(self):
        self.username, self.password = get_credentials()
        self.driver.get(login_url)
        self.driver.find_element(By.ID, "USERNAME").send_keys(self.username)
        self.driver.find_element(By.ID, "PASSWORD").send_keys(self.password)
        self.get_confirmation_code()
        self.driver.find_element(By.ID, "UserInputNo").send_keys(self.validation_code)
        self.driver.find_element(By.CSS_SELECTOR, "#Form > div.MemberBtn > button:nth-child(1)").click()



if __name__ == "__main__":
    court_reservation = Court_Reservation()
    court_reservation.login()

# initialize the Chrome driver

