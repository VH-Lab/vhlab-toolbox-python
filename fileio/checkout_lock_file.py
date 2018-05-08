# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 16:26:30 2018

@author: Lite
"""
import os
import time
def checkout_lock_file(filename, checkloops='', throwerror=''):
    '''CHECKOUT_LOCK_FILE Try to establish control of a lock file
    
    FID = CHECKOUT_LOCK_FILE(FILENAME)
    
    This function tries to check out the file FILENAME so that different
    programs do not perform some operation at the same time. This is a quick
    and dirty semaphore implementation (see Wikipedia if unfamilar with 
    semaphores).  
    
    This function tries to create an empty file called FILENAME. If the file is
    NOT already present and the creation successful, the
    file will be created and FID will return the file ID (see help fopen).
    
    If instead the file already exists, the function will check
    every 1 second for 30 iterations to see if the file disappears.
    If the function is never able to create a new file because the 
    old file exists, then the function will give up and return FID < 0.'''
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