#!/usr/bin/python
#coding:utf-8
import redis
import commands
import sys
import threading,Queue,time
def getUserList():
  file_obj=open("./loginInfo.txt")
  userList=[]
  try:
   for line in file_obj:
       userList.append(line.strip())
  except:
    userList=[]
  finally:
    file_obj.close()
    return userList
def remote_host_job(remote_host):
  logfile=open('./scheLogResource.log','a+')
  remote_host_array=remote_host.split(":")
  remote_host_name=remote_host_array[1].split(",")[0]
  remote_host_pwd=remote_host_array[2].split(",")[0]
  remote_host_ip=remote_host_array[0]
  instance = redis.StrictRedis(host='127.0.0.1', port=6379)
  rs_log_len=instance.get(remote_host_ip)
  log_info=get_log_info(remote_host_ip,remote_host_name,remote_host_pwd)
  log_len=log_info[1]
  datas=log_info[0]
  #print datas
  if log_len==-1:
	print >>logfile,str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))+":"+datas
	logfile.close()
	return
  #print >>logfile,log_info
  #logfile.close()
  #print "redis:"+str(rs_log_len)+" info:"+str(log_len)
  diff=int(log_len)-int(rs_log_len)
  #print diff
  if diff==1:
    print >>logfile,str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))+":"+remote_host_ip+':no other user login'
  elif diff>1:
    for i in range(diff):
      if i==0:
	continue
      else:
	#print datas[i].split()[0]
	if datas[i].split()[0]!=remote_host_name:
	  print >>logfile,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+":"+remote_host_ip+":other user "+datas[i].split()[0]+' do login'
  else:
    print >>logfile,'some except exit'
  try:
    instance = redis.StrictRedis(host='127.0.0.1', port=6379)
    instance.set(remote_host_ip, log_len)
  except Exception as msg:
    print >>logfile,msg 
  logfile.close()
def getUserDicts():
  userdicts=[]
  file_obj=open("./loginInfo.txt")
  try:
   for line in file_obj:
       userdict={}
       line=line.strip()
       #print line 
       line_array=line.split(":")
       #print line_array[0]
       line_array_name=line_array[1].split(",")[0]
       #print line_array_name
       line_array_pwd=line_array[2].split(",")[0]
       userdict['ip']=line_array[0]
       userdict['name']=line_array_name
       #print userdict['name']
       userdict['pwd']=line_array_pwd
       userdicts.append(userdict)
  except:
    userdicts=[]
  finally:
    file_obj.close()
  return userdicts
def set_log_len(userdict):
  #userdicts=getUserDicts()
  #print userdicts
  #for userdict in userdIcts:
    #print userdict['ip'] 
    log_len=get_log_info(userdict['ip'],userdict['name'],userdict['pwd'])[1]
    instance = redis.StrictRedis(host='127.0.0.1', port=6379)
    instance.set(userdict['ip'], log_len)
    rs=instance.get(userdict['ip'])
    #print 111
    print rs
def get_log_info(ip,name,pwd,cmd=' last'):
  try:
        remoteCmd="sshpass -p "+pwd+" ssh -t -p 22 "+name+"@"+ip+cmd
        data=commands.getoutput(remoteCmd)
        datas=data.split('\r\n')
	dataLen=len(data.split('\r\n'))
	dataflag=datas[dataLen-1]
	dataflags=dataflag.split()
	dataflags_len=len(dataflags)
        if dataflags_len!=4 or dataflags[0]!='Connection' or dataflags[3]!='closed.':
		print "diff:"+dataflag
		return (dataflag,-1)
	#print 'logInfo:'+str(dataLen)
        return (datas,dataLen)
  except Exception as msg:
        #print msg
        return (msg,-1)
class WorkManager(object):
  def  __init__(self,thread_num=2):
	self.threads=[]
	self.work_queue=Queue.Queue();
	self.remote_host_list=getUserList()
	self.__init_work_queue(self.remote_host_list)
        self.__init_thread_pool(thread_num)
  def __init_thread_pool(self,thread_num):  
        for i in range(thread_num):  
            self.threads.append(Work(self.work_queue))
  def __init_work_queue(self,args):  
        for arg in args:  
            self.add_job(remote_host_job(arg)) 
  def add_job(self, func, *args):  
        self.work_queue.put((func))#任务入队，Queue内部实现了同步机制  
       
  def wait_allcomplete(self):  
        for item in self.threads:  
            if item.isAlive():item.join() 
class Work(threading.Thread):  
    def __init__(self, work_queue):  
        threading.Thread.__init__(self)  
        self.work_queue = work_queue  
        self.start()  
  
    def run(self):  
        #死循环，从而让创建的线程在一定条件下关闭退出  
        while True:  
            try:  
                do, args = self.work_queue.get(block=False)#任务异步出队，Queue内部实现了同步机制  
                do(args)  
                self.work_queue.task_done()#通知系统任务完成  
            except:  
                break  
if __name__=='__main__':
  if sys.argv[1]=='remote_host_job':
	work_manager =  WorkManager(2)
	work_manager.wait_allcomplete()
  if sys.argv[1]=='init':
    threads=[]
    userdicts=getUserDicts()
    for userdict in userdicts:
      #set_log_len(userdict);
      threads.append(threading.Thread(target=set_log_len,args=(userdict,)))
    for t in threads:
     t.start()
     t.join()
  

