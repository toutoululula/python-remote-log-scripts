#!/usr/bin/python
#coding:utf-8
import commands
import sys
import threading
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
def init_log(userdict):
  try:
        remoteCmd="expect -f InitLogin.exp "+userdict['ip']+" "+userdict['name']+" "+userdict['pwd']
        data=commands.getoutput(remoteCmd)
       	print data
  except Exception as msg:
        print msg

if __name__=='__main__':
    threads=[]
    userdicts=getUserDicts()
    for userdict in userdicts:
      #set_log_len(userdict);
      threads.append(threading.Thread(target=init_log,args=(userdict,)))
    for t in threads:
     t.start()
     t.join()
  

