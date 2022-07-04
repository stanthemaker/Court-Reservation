# court-reservation
## Brief Intro:
This project is designed to automate court reservation with this website: https://sports.tms.gov.tw/
Since this project uses selenium, it's suggested not to use WSL due to complex GUI settings. 
## Install packages
``` bash
# if you use cuda, please go to requirements.txt and follow the instruction
for Linux:
$ pip3 install -r requirements.txt
for Windows:
$ pip install -r requirements.txt
```
## Download Model
```bash
for Linux:
$ python3 downloadModel.py
for Windows:
$ python downloadModel.py
``` 
* If the script does not work, go to the following link, download the file and put it under the current directory
* https://drive.google.com/file/d/1MtzZ9HDfaa9205bhz7yWBQVZaAZuVvwb/view

## How to run
```bash
for Linux:
$ python main.py
for Windows:
$ python main.py
```
## Environment
* python 3.8.10
