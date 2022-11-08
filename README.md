# court-reservation

## Brief Intro:

This project is designed to automate court reservation with this website: https://sports.tms.gov.tw/

Since selenium is used and therefore GUI is needed, it is suggested not to develop under WSL.

## Install Homebrew on Linux:

Refer: https://www.how2shout.com/linux/how-to-install-brew-ubuntu-20-04-lts-linux/

```bash
$ sudo apt update
$ sudo apt-get install build-essential
$ sudo apt install git -y
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
$ eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
$ brew -v
$ brew install tesseract
$ pip3 install pytesseract
```

## Install packages

```bash
# if you use cuda, please go to requirements.txt and follow the instruction
$ pip3 install -r requirements.txt
```

## How to run

```bash
$ python3 main.py
```

## Environment

- Unbuntu 20.04
- python 3.8.10
