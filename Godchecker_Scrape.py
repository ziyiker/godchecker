import requests
import time
import re
import pandas as pd
from bs4 import BeautifulSoup

def remove_tags(text):
    """Remove html tags from a string"""
    text =  re.sub('<.*?>', '', text)
    text = re.sub('\[','',text)
    text = re.sub('\]','',text)
    text = re.sub(',','',text)
    return text

def text_to_list(text):
    """Cleaning the text and changing it to a list"""
    text = [x.split(': ') for x in text.split('\n')]
    text = [s for s in text if (s != [''] and s != [' '])]
    return text

#The website which we are retrieving the data from
url = 'https://www.godchecker.com/' 

#Connect to the URL and parse HTM
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
response.close()

#Retrieving from the box with all mythologies
a_tag = soup.find(id="drop-panel-pantheons").find_all('a') 
url_list = str(a_tag).split(',')

#Creating the list of urls for all mythology
mythology_url = [] 
for i in url_list:
    myth = i.split('"><span class=')[0].split('godchecker.com/')[1]
    temp_url = f"https://www.godchecker.com/{myth}list-of-names/"
    mythology_url.append(temp_url)

#Creating the list for each individual god's url
indiv_urls = []
for i in mythology_url[:1]:
    index = requests.get(i)
    index_soup = BeautifulSoup(index.text, "html.parser")
    index.close()
    index_links = index_soup.find(id="index-links").find_all('a')
    for j in index_links:
        links = j['href']
        indiv_urls.append(links)
    time.sleep(0.5) #To prevent overloading the website
    
# Removing the duplicates
indiv_urls = list(dict.fromkeys(indiv_urls)) 

#Retrieving actual data from individual God's site
df_list = []
for site in indiv_urls:
    response_site = requests.get(site)
    response_soup = BeautifulSoup(response_site.text, "html.parser")
    box = response_soup.find(class_= "vitalsbox")
    if box is not None:
        facts = str(box.find_all('p'))
        text = remove_tags(facts)
        text = text_to_list(text)
        dic = {}
        for k,v in (text):
            dic[k] = v
        cat = str(response_soup.find(id="section_header").find('h1'))
        dic['Origin'] = remove_tags(cat)
        df = pd.DataFrame([dic])
        df_list.append(df)
        df = df[0:0]
        time.sleep(0.1) #Prevent overloading the site

#Converting the data into DataFrame
data = pd.concat(df_list,sort=False, ignore_index=True) 

#Export data as CSV file
data.to_csv('Godchecker_data.csv',index=False) 