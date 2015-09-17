#!/usr/bin/python
#coding:utf-8

import sys
import time
import psutil


PROCNAMES = ["brisquequality.exe","WerFault.exe"]
pids = []

while True:
    new_pids = []
    for proc in psutil.process_iter():
        try:
            if proc.name() in PROCNAMES:
                if proc.pid in pids:
                    try:
                        print 'terminate process pid: %d' %  proc.pid
                        proc.terminate() 
                    except Exception, e2:
                        print e2
                new_pids.append(proc.pid)
        except:
            pass

    pids = new_pids
    print 'sleeping'
    time.sleep(5)