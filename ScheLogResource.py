 # !/usr/bin/python  
# -*- coding:utf-8 -*-
from apscheduler.scheduler import Scheduler
import datetime
import PullLogResource
schedudler = Scheduler(daemonic = False)
@schedudler.interval_schedule(minutes=1)
#@schedudler.cron_schedule(second='15', day_of_week='0-7', hour='1-23')
def quote_send_sh_job():
    #print 'a simple cron job start at', datetime.datetime.now()
    work_manager =  PullLogResource.WorkManager(2)
    work_manager.wait_allcomplete()

#schedudler.start() 
if __name__=='__main__':
  schedudler.start()
