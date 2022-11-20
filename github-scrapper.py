
import os
import time
import json
import pandas as pd
from datetime  import datetime
from bs4 import BeautifulSoup as bs
from lxml import etree
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class get_github():

    def __init__(self,repo_link=None,output_folder=None,visible=False):

        self.visible = visible
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.file = os.path.join(self.directory,'data.json')
        self.data = {}

        self.browser = self.get_browser()
        self.dbrowser = self.get_browser()

        self.repo_link = repo_link
        if repo_link == None:
            print("reminder - set repo_link before scrapping")

        self.output_folder = output_folder
        if output_folder == None:
            self.output_folder = self.directory
            print("the output file will be at: ",self.output_folder)

    def get_browser(self):
        #options
        options = webdriver.ChromeOptions()
        options.add_argument('test-type')
        options.add_argument('--js-flags=--expose-gc')
        options.add_argument('--enable-precise-memory-info')
        options.add_argument('--disable-popups-blocking')
        options.add_argument('--disable-default-apps')
        options.add_argument('test-type=browser')
        options.add_argument('disable-infobars')
        options.add_argument('window-size=800x600')
        options.add_argument('log-level=3')

        if self.visible == False:
            options.add_argument('headless')
        
        return webdriver.Chrome(executable_path=os.path.join(self.directory,'chromedriver.exe'),options=options)
    

    

    def scrape(self):
        self.browser.get(self.repo_link)

        time.sleep(1.0)

        data = []


        div_list = self.browser.find_elements(By.XPATH,"//*[@id='user-list-repositories']/div[*]/div[1]/h3")

        

        for d in div_list:

            # print(d.get_attribute("innerHTML"))
            try:
                # print(li.get_attribute("innerHTML"))
                # print("#" * 20)

                # lets get the name and link
                html1 = bs(d.get_attribute("innerHTML"),'html.parser')
                # print(html1)

                item = {}
                item['link'] = 'https://github.com' + html1.find_all('a',href=True)[0]['href']
                item['name'] = item['link'].split('/')[-1]

                print(item["name"])

                response = requests.get(url=item['link'], headers={
                    "accept":"text/html, application/xhtml+xml",
                    "Accept-Encoding":"gzip, deflate, br",
                    "scheme": "https"
                    })
                # print(response.status_code)

                # lets get description and tags

                html2 = bs(response.text,"html.parser")
                tags = html2.find_all('a',attrs={'class':'topic-tag'})

                item['tags'] = []
                for  i in tags:
                    # print(i.text)
                    item['tags'].append(i.text.replace("\n","").strip())

                item["desc"] = html2.find_all('p',attrs={'class':'f4', 'class':'mb-3'})[0].text.replace("\n","").strip()
                print(item["desc"])

                # print(item)
                data.append(item)


            except Exception as e:
                print(str(e))
            
            # self.browser.find_element(By.CLASS_NAME,"next_page").click()
            
            # elem = WebDriverWait(self.browser, 30).until(
            #     EC.presence_of_element_located((By.XPATH,"//*[@id='user-repositories-list']/ul"))
            #     )

            # elem = WebDriverWait(self.browser, 30).until(
            #     EC.presence_of_element_located((By.CLASS_NAME,"paginate-container"))
            #     )
            
            # li_list = self.browser.find_elements(By.XPATH,"//*[@id='user-repositories-list']/ul/li")
        

        # return result

        file = os.path.join(self.directory,"output.json")
        with open(file, 'w',encoding="utf-8") as f:
            json.dump(data, f, indent = 6)

        file = os.path.join(self.directory,"output.csv")
        pd.DataFrame(data).to_csv(file)
        print("saved: ", file)

    


if __name__ == "__main__":
    # ggh = get_github(repo_link="https://github.com/jgarza9788?tab=repositories",visible=False)
    ggh = get_github(repo_link="https://github.com/stars/jgarza9788/lists/portfolio",visible=False)
    ggh.scrape()

    