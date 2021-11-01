#!/usr/bin/env python
# coding: utf-8

# In[225]:


from bs4 import BeautifulSoup
import requests
import time
import nltk.corpus
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.stem.porter import PorterStemmer
from fastapi import FastAPI,Request
from pydantic import BaseModel
from typing import Optional 
import uvicorn
import schedule
import threading


# In[229]:

def job():
    crawl(1)



def scheduler():
    schedule.every(1).days.do(job)
    while 1:
        schedule.run_pending()
        time.sleep(1) 

thread= threading.Thread(target=scheduler)
thread.start()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# In[241]:




# In[42]:


import pycountry
pycountry.countries
country_codes=[]
for country in list(pycountry.countries):
    country_codes.append(country.alpha_2)


# In[197]:


def getLinks(soup,source):
    links=set()
    for link in soup.find_all('a'):
        if link.get('href').find(source+".com")>0:
            links.add(link.get('href').split('&')[0].lstrip('/url?q='))
    return links


# In[196]:

mysqlURL = 'http://pymysql:9999'

def saveArticle(url:str, category:str, article:str):
    requests.post(mysqlURL+'/updatearticle',json={'url':url,'category':category,'article':article})
    return True

def crawl(numpages=3):
    categories=['technology', 'lifestyle','computers','health','covid','sport','entertainment','travel','science','politics' ,'trade','business']
    country_codes=['IN','NG','BD','RU','BR','CN','PK','US','ID']
    source = 'cnn'
    for category in categories:
        print(category)
        for region in country_codes:
            print(region)
            final_links=set()
            for i in range(0,numpages):
                time.sleep(2)
                r = requests.get('https://www.google.com/search?q='+ category +'+' + source+'&biw=1680&bih=857&tbm=nws&start='+str(i*10)+'&gl='+region)
                soup=BeautifulSoup(r.text, 'html.parser')
                links=getLinks(soup,source)
                #final_links = final_links.union(links)
                #print(soup.prettify())
                if len(links)==0:
                    break
                for link in links:
                    saveArticle(link,category,None)
            # if len(final_links)>0:
            #     file=open('cnnlinks/'+source+'_'+category+'_'+region,'a')
            #     for link in final_links:
            #         print(link)
            #         file.write(link+'\n')
            #     file.close()


# In[211]:

class QueryIn(BaseModel):
    link: str
    title: Optional[bool] = True
    normalization: Optional[bool] = False
    image: Optional[bool] = True

class QueryOut(BaseModel):
    article: str
    title : str
    image : str


@app.post("/getArticle", response_model=QueryOut, status_code=200)

def getArticle(query_data:QueryIn):
    r = requests.get(query_data.link)
    soup=BeautifulSoup(r.text, 'html.parser')
    article=""
    title ="" 
    image = ""
    if query_data.image:
        img= soup.find('div',{'data-component':'image-block'}).find('img')
        image = img['src']
    #print(soup.prettify())
    for articleTag in soup.find_all('article'):
        for head in articleTag.find_all('header'):
            if head.find('h1'):
                if query_data.title:
                    title = " " +head.find('h1').text
                else:
                    article += " " +head.find('h1').text
    for block in soup.find('article').find_all('div', {'data-component':'text-block'}):
        article += " "+ block.text
    for para in soup.find('article').find_all('p'):
        article += " "+ para.text
    if query_data.normalization:
        article = clean(article)
        title = clean(title)
    output = {"article": article ,"title":title,'image':image}
    return output
#print(getBBCArticle('https://www.bbc.com/news/world-asia-india-58778273'))


class CleanQueryIn(BaseModel):
    article: str


@app.post("/cleanArticle",status_code=200)

def cleanArticle(query_data:CleanQueryIn):
    return {'article':clean(query_data.article)}

def clean(text):
    
    text= text.lower()
    
    text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
    
    stop = stopwords.words('english')
    text = " ".join([word for word in text.split() if word not in (stop)])
    tokens = word_tokenize(text)
    
    stemmer = PorterStemmer()
    cleanTokens=[]
    for token in tokens:
        ct = stemmer.stem(token)
        if len(ct)>1:
            cleanTokens.append(ct)
    return ' '.join(cleanTokens)
#     lemmatizer = WordNetLemmatizer()
#     for token,tag in pos_tag(tokens):
#         wntag = tag[0].lower()
#         wntag = wntag if wntag in ['a', 'r', 'n', 'v'] else None
#         if not wntag:
#             lemma = token
#         else:
#             lemma = lemmatizer.lemmatize(token, wntag)
#         print(lemma)
#' '.join(clean(getArticle('https://www.bbc.com/news/business-58847328')))


# In[160]:


# from os import listdir
# from os.path import isfile, join
# path = "./links/"
# files = [f for f in listdir(path) if isfile(join(path, f))]
# print(files)


# # In[162]:


# of = open('all_links/links.csv','w')
# for file in files:
#     if file.startswith('.'):
#         continue
#     inf = open('links/'+file,'r',encoding="ISO-8859-1")
#     links = inf.readlines()
#     parts=file.split('_')
#     for link in links:
#         of.write(parts[0]+','+parts[1]+','+parts[2] + ',' + link)
#     inf.close()
# of.close()


# # In[190]:


# file = open('all_links/links.csv','r')
# op = open('articles.csv','w')
# lines= file.readlines()
# links=set()
# for line in lines:
#     link = line.split(",")[3].strip()
#     links.add(link)
# print(len(links))
# for link in links:
#     print(link)
#     try:
#         article= ' '.join(clean(getBBCArticle(link)))
#         op.write(link+","+article+"\n")
#         time.sleep(1)
#         print(link)
#     except:
#         print("-----"+link)
#         pass
# op.close()


# # In[174]:


# a=['1','2','3']
# ' '.join(a)


# # In[210]:


# links_file = open('all_links/links.csv','r')
# articles_file = open('articles.csv','r')
# links_set=set()
# links = links_file.readlines()
# for link in links:
#     parts = link.split(",")
#     row = (parts[0],parts[1],parts[3].strip())
#     links_set.add(row)
# #print(links_set)

# articles = articles_file.readlines()

# article_map={}
# for article in articles:
#     parts= article.split(",")
#     article_map[parts[0]]=parts[1]
# print(article_map)

# final_file = open('final.csv','w')

# for item in links_set:
#     if item[2].strip() in article_map:
#         final_file.write(','.join(item)+","+article_map[item[2].strip()])


# In[ ]:

if __name__ == "__main__":

    uvicorn.run("Crawler:app", host="0.0.0.0", port=8355, reload=False)



