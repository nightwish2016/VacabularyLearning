from NotionRecurringTask.VacabularyLearning import VacabularyLearning
import datetime as dt
import os
if __name__ == "__main__":
    auth=os.getenv('AUTH')
    databaseid=os.getenv('NOTION_DB')
    timeDeltaWithUTC=8
    wordsCount=15
    newWordCount=1
    oldWordCount=6
    knotion=VacabularyLearning()
    knotion.process(auth,databaseid,timeDeltaWithUTC,wordsCount,newWordCount,oldWordCount)
