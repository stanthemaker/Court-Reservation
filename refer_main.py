from tabnanny import check
import requests, sys, getpass, shutil, json, time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, datetime

from sympy import true

import recognition as recog
import time
from PIL import Image
import schedule

def log(to_print, verbose=True):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("./log.txt", 'a') as f:
        f.write("[%s] : %s\n" % (timestamp, to_print))
    if verbose:
        print("[%s] : %s" % (timestamp, to_print))

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

def checkDate(date):
    date = date.split("/")
    return len(date[0]) == 4 and int(date[1]) <= 12 and int(date[2]) <= 31

def check_order_info(date, start_time, end_time, place_seq, num):
    valid = True
    if not checkDate(date):
        log("Wrong date format: Please check the example...")
        valid = False
    if not (start_time < end_time and start_time >= 8 and end_time < 22):
        log("Wrong time format: Please check the example...")
        valid = False
    print(" ")
    return valid

def get_credentials():
    if sys.stdin.isatty():
        log("Enter credentials")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()

    return username, password

def login(username, password):
    s = requests.session()
    pre_login_response = s.get(
        "https://ntupesc.ntu.edu.tw/facilities/SessionLogin.aspx"
    )
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "https://web2.cc.ntu.edu.tw",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-GPC": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://web2.cc.ntu.edu.tw/p/s/login2/p1.php",
        "Accept-Language": "en-US,en;q=0.9",
    }

    data = {"user": username, "pass": password, "Submit": "\u767B\u5165"}

    login_response = s.post(
        "https://web2.cc.ntu.edu.tw/p/s/login2/p1.php",
        headers=headers,
        data=data,
    )
    if login_response.status_code == 200:
        if "PlaceQuery.aspx" not in login_response.url:
            log("Authentication Failed! Please check your username and password.\n")
            return False, None
        else:
            log("Successfully login with ID: %s\n" % username)
            return True, s
    else:
        log("Login Request Failed: %d" % login_response.status_code)
        return False, None


class Court_Reservation:
    def __init__(self):
        self.password = str()
        self.username = str()
        self.session = requests.Session()
        self.authenticated = False
        self.retry_interval = 0.5
        
        self.date_str = str()
        self.start_time = str()
        self.end_time = str()
        self.place_seq = str()
        self.num = str()        
        self.time_str = str()

        self.data = dict()
        # with open("./data/order.json", "r") as f:
        #     self.template = json.load(f)

        self.rec = recog.recognition()
    
    def get_order_info(self):
        log("Please fill following questions with correct infomation.\n")
        valid = False
        check = False
        while not check:
            while not valid:
                date_str = input("日期(Date, e.g. '2021/10/15')): " )
                start_time = int(input("開始時間(Start Time, e.g. '18'): " ))
                end_time = int(input("結束時間(End Time, e.g. '20'): " ))
                place_seq = int(input("場地(Place, e.g. '2'): "))
                num = int(input("數量(Number, e.g. '4'): " ))
                valid = check_order_info(date_str, start_time, end_time, place_seq, num)
            
            self.date_str = date_str
            self.start_time = start_time
            self.end_time = end_time
            self.place_seq = place_seq
            self.num = num
            self.time_str = "%d:00～%d:00" % (start_time, start_time + 1)
            log("Order information acquired successfully\n")

            check = self.confirm()
            valid = valid and check
        
    def confirm(self):
        date = datetime.strptime(self.date_str, "%Y/%m/%d")
        date_str = date.strftime("%Y-%m-%d %A")
        place_dict = {2:"一樓", 1:"三樓"}
        
        log("Start checking order details.")
        query_yes_no("Please be aware of following questions:")
        print("")
        
        check = True
        check = check and query_yes_no("日期(Date): %s" % date_str)
        check = check and query_yes_no("開始時間(Start Time): %s" % self.start_time)
        check = check and query_yes_no("結束時間(End Time): %s" % self.end_time)
        check = check and query_yes_no("場地(Place): %s" % place_dict[int(self.place_seq)])
        check = check and query_yes_no("數量(Number): %s" % self.num)
        
        if check:
            log("Order infomation confirm successfully.\n")
            return True
        else:
            log("Order infomation not confirmed.\n")
            return False

    def login(self):
        logined = False
        if self.authenticated:
            while not logined:
                logined, s = login(self.username, self.password)
                log(
                    "Trying to login again after %d ms ..."
                    % (self.retry_interval * 1000)
                )
                time.sleep(self.retry_interval)
        else:
            while not logined:
                username, password = get_credentials()
                logined, s = login(username, password)
            self.authenticated = True
            self.username = username
            self.password = password
            log("Successfully Authenticated!")

        self.session = s

    def get_validation_img(self):
        headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Sec-GPC": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "image",
            "Referer": "https://ntupesc.ntu.edu.tw/facilities/PlaceOrderFrm.aspx?buildingSeq=MAA1&placeSeq=MgA1&dateLst=2021/10/04&sTime=OAA1&eTime=OQA1&section=MQA1&date=MgAwADIAMQAvADEAMAAvADAANAA1&week=MQA1",
            "Accept-Language": "en-US,en;q=0.9",
        }

        params = (("ImgID", "Login"),)

        validation_response = self.session.get(
            "https://ntupesc.ntu.edu.tw/facilities/ValidateCode.aspx",
            headers=headers,
            params=params,
            cookies=self.session.cookies,
            stream=True,
        )

        im = Image.open(validation_response.raw)
        print(im.format, im.size, im.mode)

        return im
        # with open("./validation.png", "wb") as f:
        #     validation_response.raw.decode_content = True
        #     shutil.copyfileobj(validation_response.raw, f)

    def get_form_link(self):
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-GPC": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://ntupesc.ntu.edu.tw/facilities/PlaceQuery.aspx",
            "Accept-Language": "en-US,en;q=0.9",
        }

        params = (
            ("buildingSeq", "0"),
            ("placeSeq", self.place_seq),
            ("dateLst", self.date_str),
        )

        response = self.session.get(
            "https://ntupesc.ntu.edu.tw/facilities/PlaceGrd.aspx",
            headers=headers,
            params=params,
            cookies=self.session.cookies,
        )
        soup = BeautifulSoup(response.text, "lxml")
        time_table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_tab1"})

        table_data = [
            [cell for cell in row.find_all("td")] for row in time_table.find_all("tr")
        ]

        row_index = datetime.strptime(self.date_str, "%Y/%m/%d").isoweekday()
        column_index = int(self.start_time) - 7

        td = table_data[column_index][row_index]
        log(td)
        button = td.find("img", {"id": "btnOrder"})
        url = ""

        if button:
            link = button.get("onclick").split("'")[1]
            url = "https://ntupesc.ntu.edu.tw/facilities/%s" % link
            return True, url
        else:
            log(
                "Not Open!(%d) Try again after %d ms..." % (response.status_code, self.retry_interval * 1000)
            )
            time.sleep(self.retry_interval)
            return False, url

    def get_reserve_paylaod(self, form_url):
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-GPC": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = self.session.get(
            form_url, headers=headers, cookies=self.session.cookies
        )
        soup = BeautifulSoup(response.text, "lxml")
        form = soup.find("form", {"name": "aspnetForm", "method": "post"})
        input_tags = form.find_all("input")

        for input_tag in input_tags:
            name = input_tag.get("name")
            value = input_tag.get("value")
            # if name in self.template:
            #     if value:
            #         self.data[name] = value
            #     else:
            #         self.data[name] = ""
            self.data[name] = ""

        self.data["ctl00$ContentPlaceHolder1$DropLstTimeStart"] = self.start_time
        self.data["ctl00$ContentPlaceHolder1$hidsTime"] = self.start_time
        self.data["ctl00$ContentPlaceHolder1$DropLstTimeEnd"] = self.end_time
        self.data["ctl00$ContentPlaceHolder1$hideTime"] = self.end_time
        self.data["ctl00$ContentPlaceHolder1$txtPlaceNum"] = self.num
        self.data["ctl00$ContentPlaceHolder1$DropLstPayMethod"] = "現金"

        log("Successfully obtain payload.")

    def reserve(self):
        t = time.time()

        form_url = ""

        available = False
        while not available:
            available, form_url = self.get_form_link()

        self.get_reserve_paylaod(form_url)

        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://ntupesc.ntu.edu.tw",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-GPC": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://ntupesc.ntu.edu.tw/facilities/PlaceOrderFrm.aspx?buildingSeq=MAA1&placeSeq=MgA1&dateLst=2021/10/04&sTime=OAA1&eTime=OQA1&section=MQA1&date=MgAwADIAMQAvADEAMAAvADAANAA1&week=MQA1",
            "Accept-Language": "en-US,en;q=0.9",
        }

        while True:
            confidence = 0

            while confidence < 0.9:
                im = self.get_validation_img()
                validation_code, confidence = self.rec.recognition(im)
            input()
            self.data["ctl00$ContentPlaceHolder1$txtValidateCode"] = validation_code

            response = requests.post(
                form_url, headers=headers, cookies=self.session.cookies, data=self.data
            )

            if "圖像驗證碼錯誤" not in response.text:
                log("time:", time.time() - t)
                exit()
        check = true
        check = check and query_yes_no("sure to proceed?")
        log("time:", time.time() - t)





if __name__ == "__main__":
    # placeSeq:
    #   2 for 1 樓 (default)
    #   1 for 3 樓
    court_reservation = Court_Reservation()
    
    court_reservation.login()
    court_reservation.get_order_info()
    court_reservation.reserve()
    schedule.every().day.at("07:59").do(court_reservation.login)
    # # court_reservation.login()
    schedule.every().day.at("08:00").do(court_reservation.reserve)

    while True:
        schedule.run_pending()
        time.sleep(1)
    # court_reservation.get_validation_img()
