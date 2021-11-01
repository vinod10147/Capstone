import time
time.sleep(60)
from kafka import KafkaProducer
import csv
import requests
import json
producer = KafkaProducer(bootstrap_servers='kafka:9092',value_serializer=lambda v: v.encode('utf-8'))

def sendRowData(data,topic):
    producer.send(topic, data)

crawlerURL='http://crawler:8355'
mysqlURL = 'http://pymysql:9999'

if __name__ == "__main__":
  print("Kafka Producer Application Started.....")

def getArticle(link:str):
	articleDict = json.loads(requests.post(crawlerURL+'/getArticle',json={'link':link,'image':False,'normalization':True,'title':False}).text)
	return articleDict['article']
print(getArticle('https://www.bbc.com/sport/articles/cylzp1dr3rno'))

def getUnpickedLinks():
	links= json.loads(requests.get(mysqlURL+'/getnewsarticles?isPicked_data=false').text)
	return links.values()

def saveArticle(url:str, category:str, article:str):
	requests.post(mysqlURL+'/updateArticle',json={'url':url,'category':category,'article':article})
	return True

while(True):
	try:
		links=getUnpickedLinks()
		print(links)
		for link in links:
			article=getArticle(link['url'])
			link['article']=article
			print(link['url'])
			sendRowData(str(link),'newsfeed')
			time.sleep(2)
		print('waiting...')
	except Exception as e:
		print()
	time.sleep(10)
 # with open('results.csv', "rt", encoding='utf8') as f:
 #   reader = csv.reader(f,dialect=csv.excel)
 #   for row in reader:
 #      print(row)    	
 #      sendRowData(str(row), 'newsfeed')
 #      time.sleep(4)

producer.flush()
