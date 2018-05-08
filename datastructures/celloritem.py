#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 20:20:31 2018

@author: yanglite
"""

def celloritem(var, index=0):
    '''
    CELLORITEM - Returns the ith element of a cell list, or a single item
    
      ITEM = CELLORITEM(VAR, [INDEX])
    
     This function examines VAR; if it is a cell list, then it returns
     the INDEXth element of VAR. If it is not a cell list, then it returns
     VAR. If INDEX is not provided, it is assumed to be 1.
    
     This can be used to allow the user the option of providing a cell list or
     a single entry.
    
     Example:
         mylist1 = {'Joe','Larry','Curly'};
         mylist2 = 'Joe';
    
         for i=1:3, 
              celloritem(mylist1,i),
              celloritem(mylist2,i),
         end;
    '''
    if isinstance(var,list):
        item=var[index]
    else:
        item=var
    return item