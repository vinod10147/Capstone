from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
import requests,json

cat_map={1:'Business',2:'Computers',3:'Covid',4:'Entertainment',5:'Health',6:'Lifestyle',7:'Politics',8:'Science',9:'Sport',10:'Technology',11:'Trade',12:'Travel'}

def index(request):
	article = ""
	news_url = request.GET.get('news_url')
	articleDict={}
	if news_url is not None:
		if news_url.find("https:")>=0:
			print({'link':news_url})
			article= requests.post("http://crawler:8355/getArticle",json={'link':request.GET.get('news_url'),'normalization':False , 'image':True}).text
			articleDict = json.loads(article)
		else:
			articleDict["article"]=news_url
		articleDict["news_url"]= news_url

		predictions= requests.post("http://predictor:8818/predict_category",json={'article':cleanArticle(articleDict["article"])}).text
		articleDict["category"]=cat_map[int(json.loads(predictions)['predictions'][1:-1])]

		# l=[float(x) for x in predictions.split('[[')[1].strip(']').strip(' ').split(' ')]
		# cat_index = l.index(max(l)+1)
		#articleDict["category"] = cat_map[cat_index]
	return render(request, 'categoryPrediction/index.html' ,articleDict)

def cleanArticle(article: str):
	article= requests.post("http://crawler:8355/cleanArticle",json={'article':article}).text
	return json.loads(article)['article']