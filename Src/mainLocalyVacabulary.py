from NotionRecurringTask.VacabularyLearning import VacabularyLearning
import datetime as dt
if __name__ == "__main__":
    auth="secret_Y6RG2tlin3I8fIK5G4LDioYFqiZYS4oPfCBuc0K75vG"
    databaseid='8bf970e295764a2da8af72ef76a81f86'
    timeDeltaWithUTC=8
    wordsCount=15
    newWordCount=1
    knotion=VacabularyLearning()
    knotion.process(auth,databaseid,timeDeltaWithUTC,wordsCount,newWordCount)
