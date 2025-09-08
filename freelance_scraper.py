from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import os
import time
import pandas as pd
from pandas import DataFrame
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import pickle
from classifier import JFINclassifier
from dotenv import load_dotenv

load_dotenv()

# requirements
# pip install selenium==4.0.0 
# pip install webdriver_manager==4.0.1

# driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

# Create a fake user-agent
ua = UserAgent()
fake_user_agent = ua.random  # Get a random user-agent

# Set up undetected-chromedriver
options = uc.ChromeOptions()
options.add_argument(f"user-agent={fake_user_agent}") 
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-cache")
options.add_argument("--aggressive-cache-discard")
options.add_argument("--disable-application-cache")
options.add_argument("--disable-offline-load-stale-cache")
options.add_argument("--disk-cache-size=0")
# Uncomment if you want headless mode
options.add_argument("--headless=new")

# Initialize undetected-chromedriver
driver = uc.Chrome(version_main=138, options=options)

# Credentials 
linkedin_username = os.getenv("USERNAME2")
linkedin_password = os.getenv("PASSWORD")
# '("Hiring" AND "Looking for") AND (legal OR Law) AND ("intern")'
# '("Hiring" AND "Looking for") AND ("Intellectual property" OR "IPR") AND ("intern")'
# '("Hiring" OR "Looking for") AND ("Legal" OR "Law" OR "Corporate Law" OR "legal Drafting")'
# '("Hiring" OR "Looking for") AND ("IPR" OR "intellectual property rights" OR "M&A" OR "mergers and acquisitions")'

keywords = '("Hiring" AND "Looking for") AND (legal OR Law) AND ("intern")'
to_post_number = 100

# conda activate "C:\Users\Utkarsh\Downloads\Coding\Gen_AI\sytem_setup\tut\nvenv"

# Define LinkedIn URL and cookies file
# linkedin_url = "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin" 
linkedin_url = "https://www.linkedin.com/feed/" 
cookies_file = f"cookies\{linkedin_username}_cookies.pkl"

# Function to save cookies to a file
def save_cookies(driver, file_path):
    with open(file_path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

# Function to load cookies from a file  ``
def load_cookies(driver, file_path):
    try:
        with open(file_path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except (EOFError, pickle.UnpicklingError) as e:
        print(f"Error loading cookies: {e}. Deleting corrupted file.")
        os.remove(file_path)  # Remove the corrupted file

try:
    # Navigate to LinkedIn
    driver.get(linkedin_url)
    time.sleep(5)  # Wait for page to load

    # Check if cookies exist
    try:
        load_cookies(driver, cookies_file)
        print("Cookies loaded successfully.")
        
        driver.refresh()  # Refresh to apply cookies

        # enter_username = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"//button[@class='member-profile__details']")))
        # enter_username.click()
    except FileNotFoundError:
        print("Cookies not found. Logging in manually.")

        enter_username = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"//input[@id='username']")))
        enter_username.send_keys(linkedin_username)
        
        enter_password = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"//input[@id='password']")))
        enter_password.send_keys(linkedin_password)
        
        enter_password.send_keys(Keys.RETURN)
        time.sleep(10)  # Wait for login to complete

        # Save cookies after successful login
        save_cookies(driver, cookies_file)
        print("Cookies saved successfully.")

finally:
    print("done")

try:
    # Check if the first button is present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='artdeco-tab active artdeco-tab--selected ember-view']")))
    
    # Check for either of the XPaths for the second button
    try:
        # If the first XPath is present, click it
        second_button_xpath_1 = "//button[@class='msg-overlay-bubble-header__control msg-overlay-bubble-header__control--new-convo-btn artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view'][2]"
        second_button_xpath_2 = "//button[@class='msg-overlay-bubble-header__control msg-overlay-bubble-header__control--new-convo-btn artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view'][2]"
        
        second_button = driver.find_element(By.XPATH, second_button_xpath_1)
        second_button.click()
    except NoSuchElementException:
        # If the second XPath is not found, try the other one
        second_button = driver.find_element(By.XPATH, second_button_xpath_2)
        second_button.click()

except TimeoutException:
    # If the first button is not present, don't press
    pass

search = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH,"//input[@placeholder='Search']")))
search.send_keys(keywords)
search.send_keys(Keys.RETURN)

jobs_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"//button[@aria-pressed='false'][normalize-space()='Posts']")))
jobs_button.click()

date_posted= "4"

date_posted_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[@id='searchFilter_datePosted']")))
date_posted_button.click()

time.sleep(2)

date_posted_mapping = {
    "1": "(//label[@for='timePostedRange-'])[1]",  # XPATH for "Any time"
    "2": "(//label[@for='timePostedRange-r2592000'])[1]",  # XPATH for "Past month"
    "3": "(//label[@for='timePostedRange-r604800'])[1]",  # XPATH for "Past week"
    "4": "//label[@for='datePosted-past-24h']"  # XPATH for "Past 24 hours"
}

date_posted_xpath = date_posted_mapping.get(date_posted, "")
if date_posted_xpath:
    tf_hours = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, date_posted_xpath)))
    tf_hours.click()

time.sleep(2)

filter_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "(//span[@class='artdeco-button__text'][normalize-space()='Show results'])[2]")))
filter_button.click()

# Google Sheets configuration
gc = gspread.service_account(filename='credentials.json')  # Replace with the path to your credentials.json file
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1sJfiwSRHBwvzGhfizvpecZugmKV-2wzu-P4G5YtU6GY/edit?gid=0#gid=0'  # Replace with the URL of your Google Sheet

# Open the Google Sheet by URL
sh = gc.open_by_url(spreadsheet_url)

# Identify the subsheet by title
subsheet_title = 'Sheet1'  # Replace with the title of your subsheet
worksheet = sh.worksheet(subsheet_title)

data_list = []

nest_post = to_post_number
# Iterate over the found job post elements
for post_number in range(1, nest_post+1):
    time.sleep(2)
    profile_cards_xpath = f"(//div[@class='full-height'])[{post_number*2-1}]"
    profile_card = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, profile_cards_xpath)))
    # print(profile_cards_xpath)

    # Extract person's name
    try:
        person_name = profile_card.find_element(By.XPATH, "(.//span[contains(@class, 'visually-hidden')])[1]").text
    except:
        person_name = 'Name not found'

    # Extract person's name
    try:
        profile_link = profile_card.find_element(By.XPATH, f"(.//a[contains(@aria-label, 'View: {person_name }')])").get_attribute("href")
    except:
        profile_link = 'Profile Link not found'

    # Extract caption
    try:
        caption = profile_card.find_element(By.XPATH, ".//div[contains(@class, 'update-components-text relative')]").text
    except:
        caption = 'Caption not found'

    try:
        classifier = JFINclassifier(caption)
        chain = classifier.chain()
    except:
        chain = 'not found'

    for _ in range(2):
        # time.sleep(2)
        enter_password = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        enter_password.send_keys(Keys.PAGE_DOWN)    

    # Get the current date and time
    current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S') 

    print("Person's Name:", person_name)
    print("Profile Link:", profile_link)
    print("Caption:", "caption")
    print("result:", chain.field)
    print("result:", chain.keyword)
    print("*" * 150)

    # Append data to the DataFrame
    data_dict = {'Date': current_datetime,
                'Persons Name': person_name,
                'Profile Link': profile_link,
                'Caption': caption,
                'Class': ', '.join(chain.field) if isinstance(chain.field, list) else chain.field,
                'AI Keywords': ', '.join(chain.keyword) if isinstance(chain.keyword, list) else chain.keyword,
                'Keyword': keywords}

    # Append the dictionary to the list
    data_list.append(data_dict)

    # Append data to the Google Sheet
    worksheet.append_rows([list(data_dict.values())], value_input_option="RAW")