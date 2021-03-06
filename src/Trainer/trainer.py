# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y-6QGykOYPPbph-MH0rFxbZVw3qgiUc7
"""

import pandas as pd
import requests,json
import time
from fastapi import FastAPI,Request
from pydantic import BaseModel
#import pyspark

time.sleep(40)

predictorURL = 'http://predictor:8818'

app = FastAPI(title="trainer", docs_url="/")


@app.get("/train", status_code=200)
def train():
	mysqlURL = 'http://pymysql:9999'
	def getArticles():
		articleDict = json.loads(requests.get(mysqlURL+'/getnewsarticles?isPicked_data=1').text)
		return articleDict

	articleDict=getArticles()

	news_df = pd.DataFrame(columns=['source','category','url','article'])
	for article in articleDict.values():
		news_df = news_df.append(article,ignore_index=True)

	# news_df.CATEGORY.unique()

	import string
	import pickle

	news_df['category'] = news_df.category.map({'business':1,'computers':2,'covid':3,'entertainment':4,'health':5,'lifestyle':6,'politics':7,'science':8,'sport':9,'technology':10,'trade':11,'travel':12})
	news_df['article'] = news_df.article.map(
	    lambda x: x.lower().translate(str.maketrans('','', string.punctuation))
	)

	news_df.head()

	from sklearn.model_selection import train_test_split

	X_train, X_test, y_train, y_test = train_test_split(
	    news_df['article'], 
	    news_df['category'], 
	    random_state = 1
	)

	print("Training dataset: ", X_train.shape[0])
	print("Test dataset: ", X_test.shape[0])

	from sklearn.feature_extraction.text import CountVectorizer

	#count_vector = CountVectorizer(stop_words = 'english')
	count_vector = CountVectorizer()
	training_data = count_vector.fit_transform(X_train)
	pickle.dump(count_vector, open("/home/model/vector.pickel", "wb"))
	testing_data = count_vector.transform(X_test)


	from sklearn.naive_bayes import MultinomialNB

	naive_bayes = MultinomialNB()
	naive_bayes.fit(training_data, y_train)

	#pip install pickle

	newsfeedfile = open("/home/model/naivebayes.pickle","wb")
	pickle.dump(naive_bayes, newsfeedfile)
	newsfeedfile.close()


@app.get("/retrain", status_code=200)

def retrain():
	train()
	res = requests.get(predictorURL+'/reload')
	if res.status_code == 200:
		return {'success':True}
	else:
		return {'success':False, 'error': 'Something went wrong'}
#testing_data = count_vector.transform(['nation agre 15 minimum corpor tax rate world nation sign histor deal ensur big compani pay fairer share tax 136 countri agre enforc corpor tax rate least 15 well fairer system tax profit earn follow concern multin compani rerout profit low tax jurisdict cut bill yet critic say 15 rate low firm get around rule uk chancellor rishi sunak said deal would upgrad global tax system modern age clear path fairer tax system larg global player pay fair share wherev busi said organis econom cooper develop oecd intergovernment organis led talk minimum rate decad said deal could bring extra 150bn 108bn tax year bolster economi recov covid yet also said seek elimin tax competit countri limit floor corpor tax come 2023 countri also scope tax multin compani oper within border even dont physic presenc move expect hit digit giant like amazon facebook affect firm global sale 20 billion euro 17bn profit margin 10 quarter profit make 10 threshold realloc countri earn tax farreach agreement ensur intern tax system fit purpos digitalis globalis world economi said oecd secretarygener mathia cormann must work swiftli dilig ensur effect implement major reform deal mark sweep chang approach come tax big global compani past countri would frequent compet one anoth offer attract deal multin made sens compani might come set factori creat job could say give someth back new digit era giant becom adept simpli move profit around region busi pay lowest tax good news tax haven bad news everyon els new system meant minimis opportun profit shift ensur largest busi pay least tax busi rather choos headquart 136 countri sign achiev inevit loser well winner 100 countri support initi oecd propos announc juli ireland hungari estonia corpor tax rate 15 first resist board howev kenya nigeria pakistan sri lanka yet join agreement pact also resolv spat us countri uk franc threaten digit tax big mainli american tech firm us treasuri secretari janet yellen said morn virtual entir global economi decid end race bottom corpor taxat rather compet abil offer low corpor rate america compet skill worker capac innov race win oxfam said 15 tax rate low would littl noth end harm tax competit believ firm pay least 25 wherev base juli intern execut director gabriela bucher said 15 rate alreadi seen australia denmark excus lower domest corpor tax rate risk new race bottom daniel thomasbusi report bbc news world nation sign histor deal ensur big compani pay fairer share tax 136 countri agre enforc corpor tax rate least 15 well fairer system tax profit earn follow concern multin compani rerout profit low tax jurisdict cut bill yet critic say 15 rate low firm get around rule uk chancellor rishi sunak said deal would upgrad global tax system modern age clear path fairer tax system larg global player pay fair share wherev busi said organis econom cooper develop oecd intergovernment organis led talk minimum rate decad said deal could bring extra 150bn 108bn tax year bolster economi recov covid yet also said seek elimin tax competit countri limit floor corpor tax come 2023 countri also scope tax multin compani oper within border even dont physic presenc move expect hit digit giant like amazon facebook affect firm global sale 20 billion euro 17bn profit margin 10 quarter profit make 10 threshold realloc countri earn tax farreach agreement ensur intern tax system fit purpos digitalis globalis world economi said oecd secretarygener mathia cormann must work swiftli dilig ensur effect implement major reform deal mark sweep chang approach come tax big global compani past countri would frequent compet one anoth offer attract deal multin made sens compani might come set factori creat job could say give someth back new digit era giant becom adept simpli move profit around region busi pay lowest tax good news tax haven bad news everyon els new system meant minimis opportun profit shift ensur largest busi pay least tax busi rather choos headquart 136 countri sign achiev inevit loser well winner 100 countri support initi oecd propos announc juli ireland hungari estonia corpor tax rate 15 first resist board howev kenya nigeria pakistan sri lanka yet join agreement pact also resolv spat us countri uk franc threaten digit tax big mainli american tech firm us treasuri secretari janet yellen said morn virtual entir global economi decid end race bottom corpor taxat rather compet abil offer low corpor rate america compet skill worker capac innov race win oxfam said 15 tax rate low would littl noth end harm tax competit believ firm pay least 25 wherev base juli intern execut director gabriela bucher said 15 rate alreadi seen australia denmark excus lower domest corpor tax rate risk new race bottom ireland increas corpor tax rate 15 global tax overhaul back 130 countri us delay tariff tech tax row'])
#predictions = naive_bayes.predict(testing_data)
#predictions = naive_bayes.predict_log_proba(testing_data)
#predictions

#from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

#print("Accuracy score: ", accuracy_score(y_test, predictions))
#print("Recall score: ", recall_score(y_test, predictions, average = 'weighted'))
#print("Precision score: ", precision_score(y_test, predictions, average = 'weighted'))
#print("F1 score: ", f1_score(y_test, predictions, average = 'weighted'))

if __name__ == "__main__":

    uvicorn.run("trainer:app", host="0.0.0.0", port=8354, reload=False)






