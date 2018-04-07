# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 16:26:30 2018

@author: Lite
"""
import os
import time
def checkout_lock_file(filename, checkloops='', throwerror=''):
    # CHECKOUT_LOCK_FILE Try to establish control of a lock file
    loops = 30
    makeanerror = 0
    if checkloops:
        loops=checkloops
    if throwerror:
        makeanerror=throwerror
    loop=0
    while loop < loops and os.path.isfile(filename):
        time.sleep(1)
        loop+=1
    if loop<loops:
        try:
            fid=open(filename,'w')
        except Exception:
            fid=-1
    else:
        fid=-1
    if fid==-1:
        if makeanerror:
            raise Exception('Unable to obtain lock with file '+ filename +'.  If you believe a program that has crashed created this file then you should manually delete it.')
    return fid