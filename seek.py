#install these with 'pip install -r requirements.txt'
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
import openpyxl
from datetime import datetime
from urllib.parse import urlparse

from credentials import *
from config import *

def seek_job_search(driver):
    """Runs seek.com.au specific webscraping and then parses the salary text to attempt to normalise it for PA."""
    
    # seek.com.au specific search variables
    job_data = []
    lastpage = False
    minimumSalary = '150000'
    worktypes = ['full-time','contract-temp']
    #daterange = 'daterange=7&'
    daterange = ''
    
    try:
        df = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
    except:
        print("No Historical Data")
        df = pd.DataFrame()

    def listjobs(worktype, search):
        job_listings = driver.find_elements(By.XPATH, '//*[@id="app"]/div/div[4]/div/section/div[2]/div/div/div[1]/div/div/div[3]/div/div/div/div/div')
        for listing in job_listings:
            try:
                date = datetime.today().date()
            except:
                date = ""
            try:
                jobTitle = listing.find_element(By.CSS_SELECTOR, 'h3 a').text
                print(jobTitle)
            except:
                jobTitle = ""
            try:
                company = listing.find_element(By.CSS_SELECTOR, 'span a').text
                print(company)
            except:
                company = ""
            try:
                location = listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > span > a').text
                print(location)
            except:
                location = ""
            try:
                salary = listing.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div > span > span').text
                print(salary)
            except:
                salary = ""
            try:
                url = listing.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                parsed_url = urlparse(url)
                link = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            except:
                link = ""
            try:
                details = (listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(3) > div > span').text + listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(4) > div > span').text)
            except:
                try:
                    details = (listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(3) > div > span').text)
                except:
                    try:
                        details = (listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(4) > div > span').text)
                    except:
                        details = ""
                
            job_data.append({'date': date, 'Work Type': worktype, 'Search Term': search, 'Job Title': jobTitle, 'Company Name': company, 'Location': location, 'Salary': salary, 'Link': link, 'Details': details})

    for search in range(len(SEARCHES)):
        for worktype in worktypes:
            driver.get(f'https://www.seek.com.au/jobs/{worktype}?{daterange}keywords=%22{SEARCHES[search]}%22&salaryrange={minimumSalary}-&salarytype=annual&worktype=243%2C242%2C244')
            time.sleep(0.5)
            lastpage = False
            while lastpage == False:
                try:
                    listjobs(worktype, SEARCHES[search])
                    next = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[4]/div/section/div[2]/div/div/div[1]/div/div/div[6]/nav/ul/li[last()]/a')
                    next.click()
                    time.sleep(0.5)
                except:
                    lastpage = True

        newdata = pd.DataFrame(job_data)
        df_seek = pd.concat([df,newdata], ignore_index=True)
        df_seek = df_seek.drop_duplicates(subset=['Link'])
        df_seek.to_excel("seekjobs.xlsx", index=False)