# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:03:16 2018

@author: Lite
"""

def text2cellstr(filename):
    '''
    TEXT2CELLSTR - Read a cell array of strings from a text file
    
    C = TEXT2CELLSTR(FILENAME)
    
    Reads a text file and imports each line as an entry 
    in a cell array of strings.
    '''
    c=[]
    with open(filename,'r')as fid:
        for i in fid:
            if i[-1]=='\n':
                i=i[:-1]
            c.append(i)
    return c

