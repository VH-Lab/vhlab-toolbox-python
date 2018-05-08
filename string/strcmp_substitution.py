# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 22:18:50 2018

@author: Lite
"""
import re

def strcmp_substitution(s1, s2, SubstituteStringSymbol = '#', UseSubstituteString = 1, LiteralCharacter = '\\', SubstituteString = '', ForceCellOutput = 0):
    '''
    STRCMP_SUBSTITUTION - Checks strings for match with ability to substitute a symbol for a string
    
     [TF, MATCH_STRING, SUBSTITUTE_STRING] = STRCMP_SUBSTITUTION(S1, S2, ...)
    
     Compares S1 and S2 and returns in TF a logical 1 if they are of the same form and logical 0 otherwise.
     These strings are of the same form if
        a) S1 and S2 are identical
        b) S2 is a regular expression match of S1 (see REGEXP)
        c) S2 matches S1 when the symbol '#' in S1 is replaced by some string in S2. In this case,
           SUBSTITUTE_STRING, the string that can replace the SubstituteStringSymbol '#' is also returned.
        In any case, the entire matched string MATCH_STRING will be returned.
    
    
     The function also has the form:
    
     [TF, MATCH_STRING, SUBSTITUTE_STRING] = STRCMP_SUBSTITUTION(S1, A, ...)
    
      where A is a cell array of strings. TF will be a vector of 0/1s the same length as A,
      and SUBSTITUTE_STRING will be a cell array of the suitable substitute strings.
      
     One can also specify the substitute string to be used (that is, not allow it to vary)
     by adding the name/value pair 'SubstituteString',THESTRING as extra arguments to the function.
    
     This file can be modified by passing name/value pairs:
    
     Parameter(default):         | Description:
     ----------------------------------------------------------------------
     SubstituteStringSymbol('#') | The symbol to indicate the substitute string 
     UseSubstituteString(1)      | Should we use the SubstituteString option?
     SubstituteString('')        | Force the function to use this string as the only acceptable
                                 |    replacement for SubstituteStringSymbol
     ForceCellOutput(0)          | 0/1 should we output a list even if we receive single strings as S1, S2?
    
    
     Examples:
               s1 = '.*\.ext$'; equivalent of *.ext on the command line
               s2 = [ 'myfile1.ext', 'myfile2.ext', 'myotherfile.ext1'];
               [tf, matchstring, substring] = strcmp_substitution(s1,s2,'UseSubstituteString',0)
    
               s1 = 'stimtimes#.txt';
               s2 = [ 'dummy.ext', 'stimtimes123.txt', 'stimtimes.txt', 'stimtimes456.txt']
               [tf, matchstring, substring] = strcmp_substitution(s1,s2)
    '''
    
    made_cell = 0

    if isinstance(s2,str):
        s2 = [s2]
        made_cell = 1
    
    # step 1, identify all exact matches
    tf=[]
    for i in s2:
        tf.append(i==s1)
        
    substitute_string =['']*len(s2)
    match_string = s2
    
    # step 2, identify all regexp matches
    indexes=[i for i,x in enumerate(tf) if x==False]
    s3=[x for i,x in enumerate(s2) if tf[i]==False]
    reg=re.compile(s1)
    d = list(filter(reg.match,s3))
    for i in d:
        if i in s2:
            tf[s2.index(i)]=True
    
    # step 3, identify all substitution matches
    if UseSubstituteString:
        # what work do we have remaining?
        indexes=[i for i,x in enumerate(tf) if x==False]
        [firsthalf,lasthalf]=re.split(SubstituteStringSymbol,s1)
        for i,j in enumerate(s2):
            if j.startswith(firsthalf) and j.endswith(lasthalf):
                sub=j.replace(firsthalf,'').replace(lasthalf,'')
                if sub:
                    tf[s2.index(j)]=True
                    substitute_string[i]=sub
    # things that don't match and clean up match string indexes
    indexes=[i for i,x in enumerate(tf) if x==False]
    for i in indexes:
        match_string[i]=''
    
    # clean up outputs, string or cell
    if made_cell and not ForceCellOutput:
        match_string = match_string[0]
        substitute_string = substitute_string[0]
  
    return tf, match_string, substitute_string