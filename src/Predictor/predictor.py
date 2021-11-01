import pandas as pd
import string
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Category Predictor", docs_url="/")

class QueryIn(BaseModel):
    article: str

class QueryOut(BaseModel):
    predictions: str

newsfeedfile = open("/home/model/naivebayes.pickle","rb")
naive_bayes = pickle.load(newsfeedfile)
newsfeedfile.close()

count_vector = pickle.load(open("/home/model/vector.pickel", "rb"))

@app.post("/predict_category", response_model=QueryOut, status_code=200)
# Route to do the prediction using the ML model defined.
# Payload: QueryIn containing the parameters
# Response: QueryOut containing the flower_class predicted (200)
def predict_category(query_data: QueryIn):

	testing_data = count_vector.transform([query_data.article])
	predictions = naive_bayes.predict(testing_data)
	#predictions = naive_bayes.predict_log_proba(testing_data)
	return {"predictions":str(predictions)}

if __name__ == "__main__":
    # Uvicorn is used to run the server and listen for incoming API requests on 0.0.0.0:8888
   
    uvicorn.run("predictor:app", host="0.0.0.0", port=8818, reload=True)