from http import cookies
import time
from PIL import Image
import io
import schedule
import json
import requests, sys, getpass, shutil, json, time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import recognition as recog
from datetime import date, timedelta    # for time
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
        f = open('my_config.json')
        data = json.load(f)
        username = data["account"]["username"]
        password = data["account"]["password"]
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
        self.Court_num = 3 # 第幾面球場
        self.sdate = date(2022, 9, 1)   # start date
        self.edate = date(2022, 10, 31)   # end date
        self.weekdays = [0, 3]  # 練球日：[Monday, Thursday]
        self.date = []
        self.start_time = 8 # 開始練球時間（ 24小時制
        self.end_time = 11  # 結束練球時間（ start_time ~ end_time )
        self.place_seq = str()
        self.num = str()        
        self.time_str = str()
        self.data = dict()
        self.rec = recog.recognition()
        self.session = requests.Session()
        self.validation_code = 0
    def get_validation_code(self):
        validation_code = ""
        im = self.get_validation_img()
        validation_code = self.rec.recognition(im)
        # print("validation＿code", validation_code)
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
        self.get_validation_code()
        self.validation_code = self.validation_code.replace('\n', "")
        self.driver.find_element(By.ID, "UserInputNo").send_keys(self.validation_code)
        self.driver.find_element(By.CSS_SELECTOR, "#Form > div.MemberBtn > button:nth-child(1)").click()
        while ("驗證碼不正確，請重新輸入" in self.driver.switch_to.alert.text):
            self.driver.switch_to.alert.accept()
            self.driver.get(login_url)
            self.driver.find_element(By.ID, "USERNAME").send_keys(self.username)
            self.driver.find_element(By.ID, "PASSWORD").send_keys(self.password)
            self.get_validation_code()
            self.validation_code = self.validation_code.replace('\n', "")
            self.driver.find_element(By.ID, "UserInputNo").send_keys(self.validation_code)
            self.driver.find_element(By.CSS_SELECTOR, "#Form > div.MemberBtn > button:nth-child(1)").click()
        self.driver.switch_to.alert.accept()

    def reserve(self):
        year = self.sdate.year
        for months in range(self.sdate.month, self.edate.month+1) :
            self.driver.get("https://sports.tms.gov.tw/order/?K=472")
            select = Select(self.driver.find_element("name", 'EventType'))
            select.select_by_index(1)
            select = Select(self.driver.find_element("name", 'GovernmentType'))
            select.select_by_index(5)


            month = "%4d-%02d" % (year, months)
            select = Select(self.driver.find_element("name", 'TimePeriodSelect'))
            select.select_by_visible_text(month)
            if self.Court_num == 3: # 第三面球場
                self.driver.find_element(By.ID, "SubVenues_651").click()
            time.sleep(1) # needed


            while self.sdate < self.edate and self.sdate.month==months:
                if self.sdate.weekday() not in self.weekdays:  # not thursday or monday
                    self.sdate += timedelta(days=1)
                    continue
                for hours in range(self.start_time, self.end_time):
                    Book = self.driver.find_element(By.ID, "DataPickup.%4d.%d.%02d.%02d.1" % (year,self.sdate.month,self.sdate.day,hours)).find_element(By.TAG_NAME, "div")
                    # self.driver.execute_script("arguments[0].setAttribute('class', 'BookB UnBooked Booking')", Book)
                    Book.click()
                self.sdate += timedelta(days=1)

            self.driver.find_element(By.ID, "EventName").send_keys("台大電機系籃練球")
            self.driver.find_element(By.ID, "EventDescription").send_keys("籃球隊練球")
            select = Select(self.driver.find_element("name", 'EventSportType'))
            select.select_by_index(5) # 籃球
            self.driver.find_element(By.ID, "EventParticipantsNumber").send_keys("20")
            self.driver.find_element(By.NAME, "BackVenue").click()
            self.driver.find_element(By.NAME, "Send").click()
            self.driver.find_element(By.NAME, "Agree").click()
            self.driver.find_element(By.NAME, "SendConfirm").click()
            self.driver.find_element(By.NAME, "Send").click()
            self.driver.find_element(By.NAME, "End").click()
        

if __name__ == "__main__":
    court_reservation = Court_Reservation()
    court_reservation.login()
    court_reservation.reserve()

# initialize the Chrome driver

