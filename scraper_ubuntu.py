# ssh -i "scraper_e2_key_pair.pem" ubuntu@ec-54-152-4-227.compute-1.amazonaws.com
import os
os.system("sudo apt install python-pip")
os.system('wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -')
os.system("sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'")
os.system("apt-get -y update")
os.system("apt-get install -y google-chrome-stable")
# install chromedriver
os.system("sudo apt-get install unzip")
os.system("apt-get install -yqq unzip")
os.system("wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip")
os.system("unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/")
os.system("sudo apt-get install -y chromium-browser")

# Install xlsx
os.system("pip3 install xlsxwriter")
os.system("pip3 install selenium")
os.system("pip3 install pandas")

from selenium import webdriver
import xlsxwriter
import os
import time
import collections
import random
import pandas as pd


data_header = ['ADDRESS','CITY','STATE',
            'ZIP','PRICE','BEDS','BATHS','LOCATION','SQUARE FEET','LOT SIZE','URL']
average_header = {'Median List Price':1,'Avg. Sale / List':2, 'Median List $/Sq Ft':3,
                  'Avg. Number of Offers':4, 'Median Sale Price':5, 'Avg. Down Payment':6,
                  'Median Sale $/Sq Ft':7, 'Number of Homes Sold':8}
download_file_path = "."

options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.getcwd()}
options.add_experimental_option("prefs",prefs)
options.add_argument("--no-sandbox")
options.add_argument('--headless')
options.add_argument('--disalbe-gpu')
current_path = os.getcwd()
download_path = current_path

class DataCollector():
    def __init__(self, start_zip):
        self.start_zip = start_zip
        self.url = "https://www.redfin.com/zipcode/"+str(start_zip)
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(10)
        self.filename = "average_price1.xlsx"
        self.workbook = xlsxwriter.Workbook(self.filename)
        self.worksheet1 = self.workbook.add_worksheet("Average Price")
        self.visited_zips = set()
        self.to_be_visited = collections.deque([11702])
        self.file_num = 1
        self.count_average = 0
        self.init_average_worksheet()
        self.setup_download()
    def init_average_worksheet(self):
        for item in average_header.items():
            self.worksheet1.write(0, item[1], item[0])

    def setup_download(self):
        self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
        command_result = self.driver.execute("send_command", params)

    def singleloop(self, zip):
        self.url = "https://www.redfin.com/zipcode/"+str(zip)
        self.driver.get(self.url)

        '''
        get average
        '''
        self.worksheet1.write(self.count_average, 0, zip)
        trend_table = self.driver.find_element_by_class_name("trends")
        rows = trend_table.find_elements_by_tag_name("div")
        for rowIndex in range(len(rows)):
            row = rows[rowIndex]
            label = row.find_element_by_class_name("label").text
            value = row.find_element_by_class_name("value").text
            self.worksheet1.write(self.count_average, average_header[label],value)
        self.count_average += 1
        self.get_nearby_zip()
        '''
        download files with house information
        '''
        e = self.driver.find_element_by_partial_link_text("Download All")
        url = (e.get_attribute("href"))
        self.driver.get(url)
        time.sleep(2)

        for dpaths, dnames, fnames in os.walk(download_path):
            os.chdir(dpaths)
            for f in fnames:
                if ('redfin') in f:
                    filename = str(zip)+".csv"
                    os.rename(f, filename)
                    self.output_pandas(filename)
                    break
        os.chdir(current_path)

    def output_pandas(self,filename):
        df = pd.read_csv(current_path+"/"+filename)
        print(filename)
        print(df)


    def get_nearby_zip(self):
        table = self.driver.find_element_by_xpath("//*[text() = 'Nearby Zip Codes']//following-sibling::table[1]")
        zip_elements = table.find_elements_by_class_name("link-text")
        for zip_element in zip_elements:
            if zip_element.text != '':
                zip =zip_element.text
                if zip not in self.visited_zips:
                    self.to_be_visited.append(zip)


def main():
    d = DataCollector(11729)
    try:
        while d.to_be_visited:
            visit = d.to_be_visited.popleft()
            d.visited_zips.add(visit)
            d.singleloop(visit)
            time.sleep(random.randint(1,6))
            if d.count_average == 5:
                d.file_num += 1
                d.workbook.close()
                d.workbook = xlsxwriter.Workbook("average_price"+str(d.file_num)+".xlsx")
                d.worksheet1 = d.workbook.add_worksheet("Average Price")
                d.count_average = 0
                break
    except:
        print("here")
        # d.workbook.close()
        # d.driver.close()

    d.workbook.close()
    d.driver.close()

main()