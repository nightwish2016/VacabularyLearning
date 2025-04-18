from asyncio import Task
import json
import os,sys
from datetime import datetime,timedelta, date
import datetime as dt
from pathlib import Path
from NotionRecurringTask.Notion.Word import Word
from NotionRecurringTask.notion import *
import random

import logging
#logging.basicConfig(encoding='utf-8', level=logging.INFO)
class utilsVacabulary:
    def __init__(self,auth,deltaTime): 
        self.__baseurl="https://api.notion.com" 
        self.__auth=auth
        self.client=NotionAPIClient(self.__baseurl,self.__auth)
        self.deltaTime=deltaTime   
        pass
    
    def updateWordInformation(self,databaseid):
        reviewedToday_list=self.getAllReviewedTodayWords(databaseid)
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=utc_timestamp+dt.timedelta(hours=self.deltaTime)  
        lastDate=now_utc8+dt.timedelta(days=-1)
        print("******The following words status will be update to Done:******")         
        for w in reviewedToday_list:
            learningHistoryStr=""
            if len(w.LearningDateHistory)>0:
                for lHistory in w.LearningDateHistory:
                    learningHistoryStr=learningHistoryStr+lHistory+'\n'
            learningHistoryStr=learningHistoryStr+str(lastDate.date())+"\n"  
           
            print("{0} is updated:Status：{1}， LearningDate:{2},LearningTimes:{3}，LearningDateHistory:{4}".format(w.Word,"Done",str(lastDate.date()),(w.LearningTimes+1),learningHistoryStr.strip('\n')))              
            self.updateWordInfo(w,str(lastDate.date()),learningHistoryStr.strip('\n'),(w.LearningTimes+1),"Done")

    def getAllReviewedTodayWords(self,databaseid):
        result=self.getAllTodayReviewedWords(databaseid)
        words_list=[]
        for w in result['results']:
            w2= Word()
            w2.PageId=w["id"]
            w2.CreatedDate=w["properties"]["CreatedDate"]["created_time"]    
            if w["properties"]["LearningDate"]["date"] is not None:
                learningDateStr=w["properties"]["LearningDate"]["date"]["start"]
                w2.LearningDate=learningDateStr
                dateNow = datetime.now() 
                learningDate = datetime.strptime(learningDateStr, '%Y-%m-%d')  
                duration=(dateNow-learningDate).days
                w2.Duration=duration
            if len(w["properties"]["LearningDateHistory"]['rich_text'])>0:
                LearningDateHistoryList=w["properties"]["LearningDateHistory"]['rich_text'][0]['plain_text'].split()
                w2.LearningDateHistory=LearningDateHistoryList
            w2.LearningTimes=w["properties"]["LearningTimes"]['number'] 
            if w2.LearningTimes is None:
                w2.LearningTimes=0
            if len(w["properties"]["word"]["title"])>0 :                
                w2.Word=w["properties"]["word"]["title"][0]["text"]['content'] 
            if  w["properties"]["Status"]['select'] is not None:  
                w2.Status=w["properties"]["Status"]['select']['name']
            
            if w2.Duration=="":
                w2.Duration=0   
            words_list.append(w2)
        return words_list

    def updateWordStatusToReview(self,reviewWordList):
        for w in reviewWordList:
            self.updateWordStatus(w.PageId,"Review")


    def updateWordStatus(self,pageid,status):
        client=self.client
        body="""
        {"properties": {
 "Status" :{
                "select": {
                    "name": "Done"
                }
            }
}
}
        """
        data=json.loads(body)	
        data["properties"]["Status"]['select']['name']=status
        # data["properties"]['ExpirationDate/DateRange']['date']['start']=expirationDate
        s=client.send_patch("pages/{0}".format(pageid),data) #read all data from databases    
        # print(s)

    def GetSeveralWordsToReview(self,databaseid,wordCount,newWordCount,reviewordCount2):
        allWordsList=self.GetAllWordsNeedToReview(databaseid)
        newWordsList=[w for w in allWordsList if w.Status=="New" and w.ExplanationIsEmpty==False]
        finalWordsList=[]
        reviewWordList=[]
        for w in allWordsList:            
            if w.Duration>=1 and w.LearningTimes<=1:
                reviewWordList.append(w)
            elif w.Duration>=3 and w.LearningTimes==2:
                reviewWordList.append(w)
            elif w.Duration>=4 and w.LearningTimes==3:
                reviewWordList.append(w)
            elif w.Duration>=6 and w.LearningTimes==4:
                reviewWordList.append(w)
            elif w.Duration>=7 and w.LearningTimes==5:
                reviewWordList.append(w)
            elif w.Duration>=10 and w.LearningTimes==6:
                reviewWordList.append(w)
        reviewWordList = sorted(reviewWordList, key=lambda w: w.LearningTimes, reverse=True)
        wordsWithReview_list=self.getWordsWithStatus(databaseid,"Review")       
        if len(wordsWithReview_list["results"])>0:
            wordCount=wordCount-len(wordsWithReview_list["results"])
        size=len(reviewWordList)
        j=0
        
        if wordCount>0 :
            print("******The following words status will update to Review:******" )
        else:
            return finalWordsList
        k=0
        # newWordCount=3
        if len(newWordsList)<newWordCount:
            newWordCount=len(newWordsList)
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=utc_timestamp+dt.timedelta(hours=self.deltaTime) 
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] 
        if days[now_utc8.weekday()]  in ['Saturday', 'Sunday']:
            newWordCount=0
        while k<newWordCount and  days[now_utc8.weekday()] not in ['Saturday', 'Sunday']:
            i=random.randint(0,(newWordCount-1))   
            words = [w for w in finalWordsList if w.Word== newWordsList[i].Word]  
            if len(words)==0:
                print(newWordsList[i].Word)
                finalWordsList.append(newWordsList[i])  
                k=k+1 
        #获取前x条已经学习过最多次的记录
        k=0
        # reviewordCount2=6
        if wordCount<=reviewordCount2:
            reviewordCount2=wordCount       
        reviewListsize=len(reviewWordList)    
        if reviewListsize>reviewordCount2 :  
            while k<reviewordCount2 :
                finalWordsList.append(reviewWordList[k])
                k=k+1
                j=j+1            
        else:
            while k<reviewListsize :
                finalWordsList.append(reviewWordList[k])
                k=k+1
                j=j+1
        #获取剩下的需要review的单词
        wordCount2=0
        if wordCount>size:
            wordCount2=size
        else:
            wordCount2=wordCount
        for i in range(reviewordCount2, wordCount2-newWordCount):
            print(reviewWordList[i].Word)
            finalWordsList.append(reviewWordList[i])                               
        return finalWordsList
                   
    def GetAllWordsNeedToReview(self,databaseid):
        allNeedToReviewWords_list=[]  
        wordList=self.getAllWordsForReview(databaseid)    
        
        if wordList is not None:
             for w in wordList:
                w2= Word()
                w2.PageId=w["id"]
                
                if len(w["properties"]["Explanation"]["rich_text"])==0:
                    w2.ExplanationIsEmpty=True
                w2.CreatedDate=w["properties"]["CreatedDate"]["created_time"]    
                if w["properties"]["LearningDate"]["date"] is not None:
                    learningDateStr=w["properties"]["LearningDate"]["date"]["start"]
                    w2.LearningDate=learningDateStr
                    dateNow = datetime.now()+dt.timedelta(hours=self.deltaTime)   
                    learningDate = datetime.strptime(learningDateStr, '%Y-%m-%d')  
                    duration=(dateNow-learningDate).days
                    w2.Duration=duration
                if len(w["properties"]["LearningDateHistory"]['rich_text'])>0:
                    LearningDateHistoryList=w["properties"]["LearningDateHistory"]['rich_text'][0]['plain_text'].split()
                    w2.LearningDateHistory=LearningDateHistoryList
                w2.LearningTimes=w["properties"]["LearningTimes"]['number'] 
                if w2.LearningTimes is None:
                    w2.LearningTimes=0
                if len(w["properties"]["word"]["title"])>0 :                
                    w2.Word=w["properties"]["word"]["title"][0]["text"]['content'] 
                if  w["properties"]["Status"]['select'] is not None:  
                    w2.Status=w["properties"]["Status"]['select']['name']
                
                if w2.Duration=="":
                    w2.Duration=0   
                allNeedToReviewWords_list.append(w2)       

        
        
        return allNeedToReviewWords_list

   


    def getAllTodayReviewedWords(self,databaseid):
        client=self.client
        body="""
                {
            "filter": {
                
                   
                        "property": "Status",
                        "select": {
                            "equals": "ReviewedToday"
                        }
                    
                
            }
        }
        """   
        data=json.loads(body)	      
        s=client.send_post("databases/{0}/query".format(databaseid),data) 
        # print(s)
        return s 

    def getAllWordsForReview(self,databaseid):
        client=self.client
        body="""
        {
  	"filter": {
  		"or": [{
  				"property": "Status",
  				"select": {
  					"is_empty": true
  				}

  			},
  			{
  				"property": "Status",
  				"select": {
  					"equals": "New"
  				}
  			},
            {
  				"property": "Status",
  				"select": {
  					"equals": "Done"
  				}
  			}
  		]
  	}
  }
        """   
        
        data = json.loads(body)
        all_results = []
        has_more = True
        next_cursor = None

        # 循环分页获取所有数据
        while has_more:
            # 添加分页参数
            if next_cursor:
                data["start_cursor"] = next_cursor
            
            # 发送请求
            response = client.send_post(f"databases/{databaseid}/query", data)
            
            # 处理结果
            if "results" in response:
                all_results.extend(response["results"])
            
            # 更新分页状态
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")

    
        return all_results
    
    def getWordsWithStatus(self,databaseid,status):
            client=self.client
            body="""
            {
        "filter": 
            
                {
                    "property": "Status",
                    "select": {
                        "equals": "New"
                    }
                }
            
        
    }
            """   
            
            data=json.loads(body)	  
            data["filter"]['select']['equals']=status
            s=client.send_post("databases/{0}/query".format(databaseid),data) 
            # print(s)
            return s


    def updateWordInfo(self,word,LearningDate,LearningHistory,LearnTimes,status):
        client=self.client
        body="""
            {"properties": {       
                    "LearningDate" : {
                    "date": {
                    "start": "2021-04-26"       
                    }
                },
                "Status" :{
                "select": {
                    "name": "Done"
                    }
                },
                "LearningTimes" :{
                "number": 0
                },
                "LearningDateHistory": {
			"rich_text": [{
					"type": "text",
					"text": {
						"content": "There is some ",
						"link": null
					},
					"annotations": {
						"bold": false,
						"italic": false,
						"strikethrough": false,
						"underline": false,
						"code": false,
						"color": "default"
					},
					"plain_text": "There is some ",
					"href": null
				}						
			]
		}

        }
        }
        """
        data=json.loads(body)	
        data["properties"]['LearningDate']['date']['start']=LearningDate        
        data["properties"]["Status"]['select']['name']=status
        data["properties"]["LearningTimes"]['number']=LearnTimes
        data["properties"]["LearningDateHistory"]['rich_text'][0]['text']['content']=LearningHistory
        data["properties"]["LearningDateHistory"]['rich_text'][0]['plain_text']=LearningHistory
        s=client.send_patch("pages/{0}".format(word.PageId),data) #read all data from databases
        # print(s)
        

    def getAllAlreadyReviewedWords(self,databaseid):
        client=self.client
        body="""
        {
  	"filter": {
  		"and": [

  			{
  				"property": "LearningDate",
  				"date": {
  					"is_not_empty": true
  				}


  			},
  			{
  				"property": "Status",
  				"select": {
  					"equals": "Done"
  				}
  			}
  		]
  	}
  }
        """   
        
        data=json.loads(body)	      
        s=client.send_post("databases/{0}/query".format(databaseid),data) 
        # print(s)
        return s
#*************
   
        
class JSONObject:
    def __init__(self, d):
        self.__dict__ = d
