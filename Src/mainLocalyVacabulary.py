from NotionRecurringTask.VacabularyLearning import VacabularyLearning
import datetime as dt
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    auth=os.getenv('AUTH')
    databaseid=os.getenv('NOTION_DB')
    timeDeltaWithUTC=8
    wordsCount=12
    newWordCount=2
    oldWordCount=6
    knotion=VacabularyLearning()
    knotion.process(auth,databaseid,timeDeltaWithUTC,wordsCount,newWordCount,oldWordCount)
