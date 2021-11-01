import time
time.sleep(10)
import uvicorn
from fastapi import FastAPI
import mysql.connector 
from mysql.connector import Error
from os.path import abspath
from pydantic import BaseModel,ValidationError,validator
import json



def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


def createConn():
	try:
		global conn
		conn = mysql.connector.connect(host='mysql',database='newsdb',user='root',password='Murthy@007')
		if conn.is_connected():
			print("Connection created successfully")
	except Error as e:
		print("Not able to connect",e)

createConn()

def loadData():
	sql_query = "load data local infile '/docker-entrypoint-initdb.d/article.csv' into table newsdb.article fields terminated by ',' lines terminated by '\n' (source,category,url,article,is_picked);"
	cursor = conn.cursor()
	res=cursor.execute(sql_query)
	conn.commit()
	cursor.close()
def loadFromFile():
	file = open('/home/article.csv','r')
	records = file.readlines()
	for record in records:
		values= record.strip('\n').split(',')
		print(len(values[3]))
		sqlinsert = """insert into newsdb.article(source, category, url, article,is_picked) values('%s','%s','%s','%s',true)""" %(values[0],values[1],values[2],values[3])
		cursor = conn.cursor()
		res=cursor.execute(sqlinsert)
		conn.commit()
		cursor.close()

def dropTable():
	sqlquery = "drop table if exists article;"
	cursor = conn.cursor()
	res=cursor.execute(sqlquery)
	conn.commit()
	cursor.close()
dropTable()

def createTable():
	
	try:
		if conn.is_connected() and not checkTableExists(conn,'article'):
			sqlquery = "create table if not exists article(id int not null auto_increment,source varchar(100), category varchar(150), url varchar(255), article text, is_picked boolean not null default false, primary key(id));"
			cursor = conn.cursor()
			res=cursor.execute(sqlquery)
			conn.commit()
			cursor.close()
			loadFromFile()
	except Error as e:
		print("Error While Connecting to MySQL ", e)

createTable()


class StatusOut(BaseModel):
      status: str

      @validator('status')
      def status_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('Status must contain value')
        return v.title()


class CategoryUrl(BaseModel):
      news_source: str
      news_category: str
      news_url: str
      @validator('news_source')
      def news_source_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_source must contain value')
        return v.title()

      @validator('news_category')
      def news_category_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_category must contain value')
        return v.title()

      @validator('news_url')
      def news_url_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_url must contain value')
        return v.title()

class UpdateArticle(BaseModel):
      category: str
      url: str
      article: str
      
      @validator('category')
      def news_category_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_category1 must contain value')
        return v.title()

      @validator('url')
      def news_url_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_url1 must contain value')
        return v.title()

      @validator('article')
      def news_article_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_article must contain value')
        return v.title()


class UpdatePicked(BaseModel):
      news_category2: str
      news_url2: str
      news_picked: bool
      
      @validator('news_category2')
      def news_category_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_category2 must contain value')
        return v.title()

      @validator('news_url2')
      def news_url_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_url2 must contain value')
        return v.title()

      @validator('news_picked')
      def news_article_must_contain_value(cls, v):
        if isinstance(v,bool) and v == False and v == True:
          raise ValueError('news_picked must contain value true or false')
        return v


class GetIsPicked(BaseModel):
      news_picked1: bool
      
      @validator('news_picked1')
      def news_picked1_must_contain_value(cls, v):
        if len(v) == 0:
          raise ValueError('news_picked1 must contain value')
        return v





class CreateDict(dict):
	#init function
	def __init__(self):
		self = dict()

	#add key value
	def add(self,key,value):
		self[key]=value




# defining the main app
app = FastAPI(title="testapi", docs_url="/")

# Route definitions
@app.get("/ping")
# Healthcheck route to ensure that the API is up and running
def ping():
    return {"ping": "pong"}


# Inserting  URL and Category 
@app.post("/addurlcategory", response_model=StatusOut, status_code=200)
async def addurlcategory(urlcat_data: CategoryUrl):
	if len(urlcat_data.news_url) != 0 and len(urlcat_data.news_category) !=0 and len(urlcat_data.news_source) !=0:
		try:
			if conn.is_connected():
				sqlquery = """select id from newsdb.article where url = '%s' and category = '%s'""" %(urlcat_data.news_url, urlcat_data.news_category)
			   	#print(str(sqlquery).lower())
				cursor = conn.cursor()
				cursor.execute(str(sqlquery).lower())
				record = cursor.fetchone()
				print(str(sqlquery).lower())
				print(record)
				if record == None:
					# if does not eist then insert record
					sqlinsert = """insert into newsdb.article(source, category, url, article,is_picked) values('%s','%s','%s',NULL,false)""" %(urlcat_data.news_source,urlcat_data.news_category,urlcat_data.news_url)
					print(str(sqlinsert).lower())
					cursor.execute(str(sqlinsert).lower())
					conn.commit()
					print("Record Inserted Successfully")
					cursor.close()
				else:
					return {"status": "Record Exists"}
			else:
				print("Problem on connecting to MySQL Database")
		except Error as e:
			print("Error While Connecting to MySQL ", e)
		finally:
			if conn.is_connected():
				cursor.close()
				print("MySQL connection is closed")
	else:
		return {"status": "The Fields URL or Category is Null - Failure"}
	
	return {"status": "Record Inserted - Success"}




# update article 
@app.post("/updatearticle", response_model=StatusOut, status_code=200)
async def updatearticle(urlcat_data: UpdateArticle):
	if len(urlcat_data.url) != 0 and len(urlcat_data.category) !=0 and len(urlcat_data.article) !=0:
		try:
			if conn.is_connected():
				sqlupdate = """update newsdb.article set article = '%s' , is_picked = 1 where category = '%s' and url = '%s'""" %(urlcat_data.article,urlcat_data.category,urlcat_data.url)
				print(str(sqlupdate).lower())
				cursor = conn.cursor()
				cursor.execute(str(sqlupdate).lower())
				conn.commit()
				print("Record Updated Successfully")
				cursor.close()
			else:
				return {"status": "Problem on connecting to MySQL database"}
		except Error as e:
			print("Error While Connecting to MySQL ", e)
	else:
		return {"status": "URL or Article or Category is Null - Failure"}
	
	return {"status": "Record Updated - Success"}


# update is_picked 
@app.post("/updateispicked", response_model=StatusOut, status_code=200)
async def updateispicked(urlcat_data: UpdatePicked):
	if len(urlcat_data.news_url2) != 0 and len(urlcat_data.news_category2) !=0:
		try:
			if conn.is_connected():
				sqlupdate = """update newsdb.article set is_picked = %d where category = '%s' and url = '%s'""" %(urlcat_data.news_picked,urlcat_data.news_category2,urlcat_data.news_url2)
				print(str(sqlupdate).lower())
				cursor = conn.cursor()
				cursor.execute(str(sqlupdate).lower())
				conn.commit()
				print("Is Picked Record Updated Successfully")
				cursor.close()
			else:
				return {"status": "Problem on connecting to MySQL database"}
		except Error as e:
			print("Error While Connecting to MySQL ", e)
	else:
		return {"status": "URL or Picked or Category is Null - Failure"}
	
	return {"status": "Record Updated - Success"}



#Returns the news articles 
#@app.get("/getnewsarticles", response_model=json, status_code=200)
#async def getnewsarticles():
#async def getnewsarticles():
@app.get("/getnewsarticles", status_code=200)
async def getnewsarticles(isPicked_data: bool):
		newsdict = CreateDict()
		try:
			if conn.is_connected():
				sqlselect = """select id,source,category,url,article,is_picked from article where is_picked = %d """ %(1 if isPicked_data else 0)
				#sqlselect = """select id,source,category,url,article,is_picked from article"""
				print(str(sqlselect).lower())
				cursor = conn.cursor()
				cursor.execute(str(sqlselect).lower())
				results = cursor.fetchall()
				print("Get Records Successfull")
				for row in results:
					newsdict.add(row[0],({"source":row[1],"category":row[2],"url":row[3],"article":row[4],"is_picked":row[5]}))
				
				article_json = json.dumps(newsdict,indent=2,sort_keys=True)
				# print("**********************************")
				# print(article_json)
				# print("**********************************")
				cursor.close()
				
			else:
				return {"status": "Problem on connecting to MySQL database"}
		except Error as e:
			print("Error While Connecting to MySQL ", e)
	
		return newsdict



#Main function to start the app when main.py is called
if __name__ == "__main__":
    # Uvicorn is used to run the server and listen for incoming API requests on 0.0.0.0:8888
    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)	

