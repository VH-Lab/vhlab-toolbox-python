#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 19:22:26 2018

@author: yanglite
"""

def emptystruct(keys):
    # EMPTYSTRUCT - Create a dictionary with given fieldnames that is empty
    # S = EMPTYSTRUCT(fieldname1, fieldname2, ...)
    s={}
    for i in range(len(keys)):
        s.update({keys[i]:''})
    return s