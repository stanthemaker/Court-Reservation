import time
from PIL import Image
import io
import schedule
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
from filter import filterImage

login_url = "https://sports.tms.gov.tw/member/?U=login"

class Court_Reservation:
    def __init__(self):
        self.num = str()        
        self.time_str = str()
        self.data = dict()
        self.session = requests.Session()
        self.validation_code = 0
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options = op)
        
    def get_dataBase(self):
        self.driver.get(login_url)
        for i in range(100):
            ChkImg_element = self.driver.find_element(By.ID, "ChkImg")    
            ChkImg_element.screenshot( f"./Screenshots/validation{i}.png")
            raw_img = Image.open(f"./Screenshots/validation{i}.png")
            filtered_img = filterImage(raw_img)
            filtered_img.save(f"./filteredImage/filtered_img{i}.png")
            renew_botton = self.driver.find_element(By.CSS_SELECTOR, "#Form > div:nth-child(3) > label > div.Content > button:nth-child(3)")
            renew_botton.click()
            time.sleep(0.5)


if __name__ == "__main__":
    court_reservation = Court_Reservation()
    court_reservation.get_dataBase()

# initialize the Chrome driver

