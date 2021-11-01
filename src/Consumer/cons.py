import time
time.sleep(30)
from kafka import KafkaConsumer
import json
# Import sys module
import sys
import requests

def saveArticle(url:str, category:str, article:str):
	requests.post(mysqlURL+'/updatearticle',json={'url':url,'category':category,'article':article})
	return True

mysqlURL = 'http://pymysql:9999'
bootstrap_servers = ['kafka:9092']

topicName = 'newsfeed'

consumer = KafkaConsumer (topicName, group_id ='group1',bootstrap_servers = bootstrap_servers)

print("Consumer Started....")
# Read and print message from consumer
for news in consumer:
	newsString=news.value.decode('utf-8').replace("\'", "\"")
	newsDict=json.loads(newsString)
	saveArticle(newsDict['url'],newsDict['category'],newsDict['article'])
	print("%s"%(news.value))
	
sys.exit()
