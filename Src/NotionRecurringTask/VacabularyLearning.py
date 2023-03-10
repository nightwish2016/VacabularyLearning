from NotionRecurringTask.Notion.utilsVacabulary import *
import argparse
import logging 

class VacabularyLearning:
    def __init__(self):       
        pass
    def process(self,auth,databaseid,deltaTimeWithUTC,wordsCount):            
        u=utilsVacabulary(auth,deltaTimeWithUTC)		
        # days=0
        # u.createDailyTask(taskConfiguration_dabaseid,offDayDatabaseId,databaseid)
        # u.UpdateTaskStatus(databaseid,days)


        # get all words that need to review from table,fetch random 10 words each day,               
        # update status to review

          #如果已经有8个是Review状态，那么只更新2个word成Review状态*******
        #old word,new word 优化成一个notion request

        reviewwordlist=u.GetSeveralWordsToReview(databaseid,wordsCount)    
        u.updateWordStatusToReview(reviewwordlist)


        # u.getAllReviewedTodayWords(databaseid)
        # Update record from last date , Task with reviewCompleteToday=> ge          
        #  update lastlearningdate to yesterday, Add learningDateshistory,Update learning times to 1
        # update tasks with status Done
        u.updateWordInformation(databaseid)