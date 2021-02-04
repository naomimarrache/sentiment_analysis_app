# -*- coding: utf-8 -*-
"""
Created on Tue May 26 19:30:39 2020

@author: JRIBI
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
# The ActionChain class to avoid the "Element is not clickable" issue
from selenium.webdriver.common.action_chains import ActionChains

import time
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

#################################################################################################################
#####################                              Functions' Definition                    #####################
#################################################################################################################

"""
Function to check if an Xpath Element is presnet on the Web page, to avoid miss-click problem
"""
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True
    
""" 
Function to scrap all Reviews of a particular Restaurant in a particular language
"""
def get_restau_reviews(url_restau) : 
    
    # Launch the url page 
    driver.get(url_restau)

    # Get all the reviews of the corresponding restaurant
    while True :  
        # Click on all the more button :
        time.sleep(4)
        more_buttons = driver.find_elements_by_xpath("//span[@class='taLnk ulBlueLinks']")
        if len(more_buttons) > 0 : # there are "... Plus" buttons that should be clicked
            try : 
                print("Click '...Plus' button" )
                driver.find_element_by_xpath("//span[@class='taLnk ulBlueLinks']").click()
            except (ElementClickInterceptedException,StaleElementReferenceException) : 
                print("Intercept Click Exceptions when click '... Plus'" )
                # wait for the "...Plus" button to be Clickable 
                wait = WebDriverWait(driver, 60)
                wait.until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[@class='taLnk ulBlueLinks']")))
                # Click the "...Plus" button as soon as it will be Clickable
                ActionChains(driver).move_to_element(driver.find_element_by_xpath("//span[@class='taLnk ulBlueLinks']")).click().perform()
       
            
        # A pause time to be sure that the page is completely loaded 
        time.sleep(7)
        # hand off the manipulated page source to Beautiful Soup.
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # Get the review zone 
        reviews_selector = soup.find_all('div', attrs={'class':'rev_wrap ui_columns is-multiline'})
        for review in reviews_selector : 
            #Title
            title = review.find ('span', attrs={'class' : 'noQuotes'})
            title_array.append(title.text.strip().replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace(";", "."))  
            #Note
            note_box = review.find('span', attrs = {'class': 'ui_bubble_rating'}) 
            note = int(note_box.get("class")[1][7:9])/10
            note_array.append(note)
            #Comment
            comment = review.find('p', attrs={'class':'partial_entry'})
            comment_array.append(comment.text.strip().replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace(";", "."))
            # Date
            date_visit = review.find('div', class_='prw_rup prw_reviews_stay_date_hsx')
            date_post = review.find('span', class_='ratingDate')
            try: 
                date_array.append(date_visit.text.strip().split(": ")[1])
            except IndexError:
                # If the visit date does not exist, we record the publication date
                date_array.append(date_post.text.strip().split(" ")[4] + " " + date_post.text.strip().split(" ")[5])
        
        # Test if there is a next page of reviews
        if (check_exists_by_xpath('//a[@class="nav next ui_button primary  cx_brand_refresh_phase2"]')):
            # Go to the next page 
            try : 
                print("there is a next page")
                # Change to the next page 
                driver.find_element_by_xpath('//a[@class="nav next ui_button primary  cx_brand_refresh_phase2"]').click()
                time.sleep(3)
                
            #except(StaleElementReferenceException, ElementClickInterceptedException):
            except : # catch all exceptions 
                # wait for the "next" button to be Clickable 
                print("in the Except Next")
                wait = WebDriverWait(driver, 60)
                wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '//a[@class="nav next ui_button primary  cx_brand_refresh_phase2"]')))
                # Click the "next" button as soon as it will be Clickable
                #driver.find_element_by_xpath('//a[@class="nav next ui_button primary  cx_brand_refresh_phase2"]').click()
                ActionChains(driver).move_to_element(driver.find_element_by_xpath('//a[@class="nav next ui_button primary  cx_brand_refresh_phase2"]')).click().perform()
                time.sleep(3)
        else : 
            print("there is no next page")
            # Stop the loop 
            break 
   
    
    
###################################################################################################################
########################              Crawling the reviews of all restaurants             #########################
###################################################################################################################


# Check the presence of the reviews' file ('all_restau_reviews_fr') 
# & Get the index of the last handled restaurant 
reviews_file =Path.cwd()/'all_restau_reviews_fr.csv'
print(reviews_file)
if reviews_file.is_file():
    # Parse the file and get the ID of the last restaurant
    df_reviews = pd.read_csv(reviews_file, sep=';')
    try : 
        restau_index = df_reviews.iloc[-1, 0] # last line, first column (restau_ID)
    except: 
        restau_index = 0 # in case of error, initialization to 0 
    print(restau_index)
    
else:
    # The scraping of reviews has not yet started
    # the file is created with the appropriated header and the restaurant index is initialized to 0 
    df = pd.DataFrame(columns =[ 'restau_ID','Titre',  'Note', 'DateVisite' , 'Commentaire','restaurant'] )
    df.to_csv(reviews_file, header=True, index = False,mode='a', encoding='utf-8-sig', sep=';')
    restau_index = 0
    print(restau_index)

####################### Get Reviews of the remaining restaurant 

# Initialize a FireFox WebDriver with some particular options 
options = Options()
#options.headless = True  # to access the page source without opening a browser window
profile = webdriver.FirefoxProfile()
profile.accept_untrusted_certs = True # To automate the acceptance of a website's certificate when launching the browser
driver = webdriver.Firefox(firefox_profile=profile, options=options)


# DataFrame containing the Restaurant's URLs and IDs
df_url=pd.read_csv('all_restaurant_url.csv')
last_RestauID = df_url.iloc[-1, 0]
stop_flag=False
# If you want to scrap from a certain reaturant ID, uncomment the following line
# restau_index = 1000

# Scraping of all the remaining URLs in the file
while ((restau_index < last_RestauID) and (not stop_flag)): 

    if(int(df_url['nombre_avis'][restau_index]) != 0) :  # Scrap all reviews  of the restaurant
        # Initialize variables for recording Data 
        title_array = []
        note_array = []
        comment_array = []
        date_array = []
        restau_Name = df_url['restaurant'][restau_index]
        restau_ID = restau_index+1
        try :         
            # Scrap all reviews  of the restaurant
            get_restau_reviews(df_url['url'][restau_index]) 
        except : # catch all other exceptions 
            print("Exception in the function get_review")
            print(" ---> record scaraped data and stop the script :( ")
            stop_flag = True
            pass
        
    else : 
        # Nothing to Do, pass to the next URL 
        restau_index +=1
        continue
    
    # Add scraped data to a pandans DataFrame 
    restau_data ={'restau_ID' : restau_ID, 
                  'Titre' :  title_array, 
                  'Note' : note_array,
                  'DateVisite' : date_array, 
                  'Commentaire' : comment_array, 
                  'restaurant': restau_Name
                  }
    
    df = pd.DataFrame(restau_data,columns =[ 'restau_ID','Titre',  'Note', 'DateVisite' , 'Commentaire','restaurant'] )
    print(df)
    # Add the DataFrame at the end of the reviews' file
    df.to_csv(reviews_file, header=False, index = False, mode='a', encoding='utf-8-sig',sep =';' )

    # Close the csv file and Iterate the to next restaurant   
    restau_index +=1
    

# Close the driver 
driver.quit()



    
