# -*- coding: utf-8 -*-
"""
Created on Wed June 22 16:57:32 2020

@author: JRIBI
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
# The ActionChain class to avoid the "Element is not clickable" issue
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# function to check if the button is presnent on the page, to avoid miss-click problem
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True
    
#############################################################################
####                   Scraping the restaurant URLs                      ####
#############################################################################


# Add Some options to the driver 
options = Options()
#options.headless = True  # to access the page source without opening a browser window
profile = webdriver.FirefoxProfile()
profile.accept_untrusted_certs = True # To automate the acceptance of a website's certificate when launching the browser

# List of all "French cuisine" establishments (restaurant/cafe/street-Food....)
page_link="https://www.tripadvisor.fr/Restaurants-g187147-c20-Paris_Ile_de_France.html"

# create a new Firefox session
driver = webdriver.Firefox(firefox_profile=profile, options=options)
driver.get(page_link)

# Arrays to record scrapped Data 
restaurant_IDs=[]
restaurant_names = []
reviews_url = []
total_nb_reviews = []
global_score= []

# Prefix to add to the restaurant's reviews URL
prefix_url_resto = "https://www.tripadvisor.fr"

while True : 
    # A pause time, to wait the new page to be loaded 
    time.sleep(7)
    # hands off the manipulated page source to BeautifulSoup.
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Get the restaurant div containing all information 
    restaurant_selector = soup.find_all('div', attrs={'data-test' :re.compile(r"\d+_list_item"), 'class':'_1llCuDZj'})
    for restaurant in restaurant_selector : 
        # Extract Data
        # The ID, name and url of the restaurant
        div = restaurant.find('div', attrs={'class' : 'wQjYiB7z'})
        idR =div.find('a').get_text().split('.')[0]
        name = div.find('a').get_text().split('.')[1].strip()
        url = prefix_url_resto + div.find('a')['href']
        
        # The total number of reviews and the global rating score 
        div_review = restaurant.find('div', attrs={'class' : '_2rmp5aUK'}) 
        nb_review_span = div_review.find('span', attrs = {'class': 'w726Ki5B'})
        score_span = div_review.find('span', attrs = {'class': '_3KcXyP0F'})
        try : 
            nb_review = int(nb_review_span.text.strip('avis').replace(u'\xa0', u''))
            score = float(score_span['title'].split(" ")[0].replace(',', '.'))
        except : 
            nb_review = 0
            score = 0
        
        # Append Data to the associted array
        restaurant_IDs.append(idR)
        restaurant_names.append(name)
        reviews_url.append(url)
        total_nb_reviews.append(nb_review)
        global_score.append(score)
                 
    # Test if there is a next page of restaurants
    if (check_exists_by_xpath('//a[@class="nav next rndBtn ui_button primary taLnk"]')):      
        # Go to the next page 
        try : 
            driver.find_element_by_xpath('//a[@class="nav next rndBtn ui_button primary taLnk"]').click()
            
        except(StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException):
            # wait for the "next" button to be Clickable 
            print("in the Except : ")
            wait = WebDriverWait(driver, 60)
            wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '//a[@class="nav next rndBtn ui_button primary taLnk"]')))
            # Click the "next" button as soon as it will be Clickable   
            #driver.find_element_by_xpath('//a[@class="nav next rndBtn ui_button primary taLnk"]').click()
            ActionChains(driver).move_to_element(driver.find_element_by_xpath('//a[@class="nav next rndBtn ui_button primary taLnk"]')).click().perform()
            
    else : 
        # Stop the loop 
        break 
 
# record Scraped Data in a csv file 
data ={'restau_ID' : restaurant_IDs,
       'restaurant': restaurant_names, 
       'url' : reviews_url, 
       'nombre_avis' : total_nb_reviews, 
       'score_general' : global_score}
       
df = pd.DataFrame(data,columns =[ 'restau_ID', 'restaurant', 'url', 'nombre_avis', 'score_general'] )
df.to_csv ('all_restaurant_url.csv', index = False, header=True,encoding='utf-8-sig')
       
# close the driver 
driver.quit()

