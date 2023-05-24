from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import pandas as pd
import time
import unidecode
import csv
import sys
import numpy as np

def initialize_bot():

    # Setting up chrome driver for the bot
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # installing the chrome driver
    driver_path = ChromeDriverManager().install()
    chrome_service = ChromeService(driver_path)
    # configuring the driver
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    ver = int(driver.capabilities['chrome']['chromedriverVersion'].split('.')[0])
    driver.quit()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument("--disable-notifications")
    # disable location prompts & disable images loading
    prefs = {"profile.default_content_setting_values.geolocation": 2, "profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.cookies": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(version_main = ver, options=chrome_options) 
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    driver.set_page_load_timeout(300)

    return driver


def scrape_bookcompanion(path):

    start = time.time()
    print('-'*75)
    print('Scraping bookcompanion.com ...')
    print('-'*75)
    # initialize the web driver
    driver = initialize_bot()

    # initializing the dataframe
    data = pd.DataFrame()

    # if no books links provided then get the links
    if path == '':
        name = 'bookcompanion_data.csv'   
        links = []
        # scraping books urls
        driver.get('https://www.bookcompanion.com/book_list.html')
        

    # scraping books details
    print('-'*75)
    print('Scraping Books Info...')
    n = 0
    table = wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.style55")))
    books = wait(table, 2).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))[1:]
    for i, book in enumerate(books):
        try:                 
            details = {}

            title, title_link = '', ''
            try:
                td = wait(book, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.style57")))
                a = wait(td, 2).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
                title_link = a.get_attribute('href')
                if title_link == None: continue
                title = a.get_attribute('textContent').strip()             
            except Exception as err:
                continue

            details['Title'] = title
            details['Title Link'] = title_link

            print(f'Scraping the info for book {n+1}')
            n += 1

            author, author_link = '', ''
            try:
                td = wait(book, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.style56")))
                a = wait(td, 2).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
                author = a.get_attribute('textContent') 
                author_link = a.get_attribute('href') 
            except:
                try:
                    author = td.get_attribute('textContent')
                except:
                    continue

            details['Author'] = author
            details['Author Link'] = author_link
     
            # appending the output to the datafame            
            data = data.append([details.copy()])
            # saving data to csv file each 100 links
            if np.mod(i+1, 100) == 0:
                print('Outputting scraped data to Excel sheet ...')
                data.to_excel(name, index=False)
        except:
            pass

    # optional output to Excel
    data.to_excel('Bookcompanion.xlsx', index=False)
    elapsed = round((time.time() - start)/60, 2)
    print('-'*75)
    print(f'bookcompanion.com scraping process completed successfully! Elapsed time {elapsed} mins')
    print('-'*75)
    driver.quit()

    return data

if __name__ == "__main__":
    
    path = ''
    if len(sys.argv) == 2:
        path = sys.argv[1]
    data = scrape_bookcompanion(path)

