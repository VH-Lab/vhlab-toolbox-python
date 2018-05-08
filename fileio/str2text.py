# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:28:09 2018

@author: Lite
"""

def str2text(filename,data):
    '''
    STR2TEXT - Write a string to a text file
    
    STR2TEXT(FILENAME, str)
    
    Writes the strings to the new text file FILENAME.
    '''
    with open(filename,'w') as fid:
        fid.write(data)