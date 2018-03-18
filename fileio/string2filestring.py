#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 13:34:00 2018

@author: yanglite
"""
import string

def string2filestring(s):
    # STRING2FILESTRING - edit a string so it its suitable for use as part of a filename (remove whitespace)
    # Example:
    # mystr = 'This is a variable name: 1234.';
    # string2filestring(mystr)  % returns 'This_is_a_variable_name__1234_'
    ranges=string.ascii_lowercase+string.ascii_uppercase+string.digits
    s=list(s)
    for i in range(len(s)):
        if s[i] not in ranges:
            s[i]='_'
    return "".join(s)