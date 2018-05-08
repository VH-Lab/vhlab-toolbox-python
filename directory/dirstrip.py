# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 23:21:43 2018

@author: Lite
"""

def dirstrip(ds):
    '''
    Removes '.' and '..' from a directory structure returned by the function
     "DIR". Also removes '.DS_Store' (Apple desktop information) from the
     list.
    
     This will return all file names, including regular files. To return only
     directories, see DIRLIST_TRIMDOTS.
    
     See also: DIR, DIRLIST_TRIMDOTS
    '''
    for i,x in enumerate(ds):
        if x.get('_name_') in ['.','..','.DS_Store']:
            del ds[i]
    return ds