#!/bin/bash
# bash start.sh启动
git pull
cd  /root/mytools/VacabularyLearning/.ven/bin
source activate
python3  /root/mytools/VacabularyLearning/Src/mainLocalyVacabulary.py
deactivate
