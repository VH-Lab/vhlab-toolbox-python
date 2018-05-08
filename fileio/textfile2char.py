#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 20:43:29 2018

@author: yanglite
"""

def textfile2char(filename):
    '''
    TEXTFILE2CHAR - Read a text file into a character string
    
     STR = TEXTFILE2CHAR(FILENAME)
    
     This function reads the entire contents of the file FILENAME into
     the character string STR.  
    '''
    with open(filename,'r') as fid:
        return str(fid.read())