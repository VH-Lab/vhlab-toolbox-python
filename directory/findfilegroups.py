# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:38:39 2018

@author: Lite
"""
from dirstrip import *
import os
import sys
sys.path.insert(0, '../datastructures')
from emptystruct import *

def findfilegroups(parentdir, fileparameters,SameStringSearchSymbol = '#',UseSameStringSearchSymbol = 1,SearchParentFirst = 1,SearchDepth = float("inf"),SearchParent = 1):
    '''
    FINDFILEGROUPS - Find a group of files based on parameters
    
     FILELIST = FINDFILEGROUPS(PARENTDIR, FILEPARAMETERS, ...)
    
     Finds groups of files based on parameters.
    
     FILEPARAMETERS should be a cell list of file name search parameters.
     These parameters can include regular expresion wildcards ('.*') and symbols
     that indicate that the same string needs to be present across files ('#').
     Searches will return matches of these groups of files in PARENTDIR and all
     of its subdirectories.
    
     FILELIST is a cell array of all of the instances of these file groups.
     That is, FILELIST{i} is the ith instance of these file groups.
     The full path file names are returned in the entries of FILELIST{i}.
     That is, FILELIST{i}{j} is the jth file in the ith instance of the file groups.
    
     The parent directory is searched first for matches, and then all subdirectories are searched.
     
     This file can be modified by passing name/value pairs:
    
     Parameter(default):         | Description:
     ----------------------------------------------------------------------
     SameStringSearchSymbol('#') | The symbol to be used to indicate the the same
                                 |    string across files
     UseSameStringSearchSymbol(1)| Should we use the same string search field?
     UseLiteralCharacter(1)      | Use the LiteralCharacter
     SearchParentFirst(1)        | Should we search the parent before the subdirectories of the
                                 |    parent? Otherwise, subdirectories are searched first.
     SearchParent (1)            | Should we search the parent?
     SearchDepth (Inf)           | How many directories 'deep' should we search?
                                 |   0 means parent only, 1 means one folder in, ...
    
     Examples:
    
         ffg_prefix = [userpath filesep 'tools' filesep 'vhlab_mltbx_toolbox' ...
          filesep 'directory' filesep 'test_dirs' filesep]; location of test directories
    
         finds all files with '.ext' extension.
         fileparameters = {'.*\.ext\>'};
         filelist = findfilegroups([ffg_prefix 'findfilegroupstest1'],fileparameters);
         list all files to see which subset(s) was(were) selected:
         dir(([ffg_prefix 'findfilegroupstest1' filesep '**/*']))
    
         finds all sets of files 'myfile.ext1' and 'myfile.ext2' when these files
         co-occur in the same subdirectory of PARENTDIR
         fileparameters = {'myfile.ext1','myfile.ext2'}; finds all sets of files
         filelist = findfilegroups([ffg_prefix 'findfilegroupstest2'],fileparameters);
         dir(([ffg_prefix 'findfilegroupstest2' filesep '**/*']))
                       
         finds all sets of files 'myfile_#.ext1' and 'myfile_#.ext2', where # is 
         the same string, and when these files co-occur in the same subdirectory.
         For example, if the files 'stimtimes1.txt' and 'reference1.txt' were in the same
         subdirectory, these would be returned together.
         fileparameters = {'myfile_#.ext1','myfile_#.ext2'}
         filelist = findfilegroups([ffg_prefix 'findfilegroupstest3'],fileparameters);
         dir(([ffg_prefix 'findfilegroupstest3' filesep '**/*']))
    
     See also: STRCMP_SUBSTITUTE
    '''
    # we're done if we've exceeded search depth
    if SearchDepth<0:
        return []
#    d = dirstrip(os.listdir(parentdir))
    d = dirstrip(parentdir)
    subdirs=[i for i,x in enumerate(d) if x['_isdir_']]
    regularfiles=[i for i,x in enumerate(d) if not x['_isdir_']]
    if not SearchParentFirst:
        for i in subdirs:
            filelist = findfilegroups(parentdir+'/'+ d[i]['_name_'],fileparameters, \
                                      SameStringSearchSymbol = SameStringSearchSymbol,\
                                      UseSameStringSearchSymbol = UseSameStringSearchSymbol,\
                                      SearchParentFirst = SearchParentFirst,\
                                      SearchDepth = SearchDepth,SearchParent=1)
    
    # now look in this directory, if we are supposed to
    if SearchParent:
        # could be many groups of matches in the directory, find all potential lists
        filelist_potential = emptystruct('searchString','filelist')
        # in order for a file group to pass, we have to find potential passing matches to the first criterion
        s2=[]
        for i in regularfiles:
            s2.append(d[i]['_name_'])
        tf, match_string, searchString = strcmp_substitution(fileparameters[0], s2,\
                                                             SubstituteStringSymbol=SameStringSearchSymbol,\
                                                             UseSubstiteString=UseSameStringSearchSymbol)
        indexes=[i for i,x in enumerate(tf) if x==True]
        for i in indexes:
            filelist_potential.update({'searchString':searchString[i],'filelist':match_string[i]})
        for k in range(1,len(fileparameters)):
            new_filelist_potential = emptystruct('searchString','filelist')
            for j in range(len(filelist_potential)):
                tf,match_string,newSearchString = strcmp_substitution(fileparameters[k], s2, \
                                                                      SubstituteStringSymbol=SameStringSearchSymbol,\
                                                                      UseSubstiteString=UseSameStringSearchSymbol,\
                                                                      SubstituteString=filelist_potential[j]['searchString'])
                indexes=[i for i,x in enumerate(tf) if x==True]
                
                for i in indexes:
                    if not filelist_potential[j]['searchString']:
                        matchpotential['searchString'] = newSearchString
                    else:
                        matchpotential['searchString'] = filelist_potential[j]['searchString']
                    matchpotential['filelist'] = filelist_potential[j]['filelist']+[match_string[i]]
                    new_filelist_potential.append(matchpotential)
            filelist_potential = new_filelist_potential
            
            # no matches possible anymore
            if not filelist_potential:
                break
        # now we have scanned everything, report the file groups
        for j in filelist_potential:
            myfilelist = []
            for k in range(len(j['filelist'])):
                myfilelist.append(parentdir +'/'+j['filelist'][k])
            filelist.append(myfilelist)
        
    # now that we've searched the parent, we need to search the subdirs
    if SearchParentFirst:
        for i in subdirs:
            filelist = filelist+findfilegroups(parentdir +'/'+d[i]['_name_'],fileparameters,\
                                               SameStringSearchSymbol = SameStringSearchSymbol,\
                                               UseSameStringSearchSymbol = UseSameStringSearchSymbol,\
                                               SearchParentFirst = SearchParentFirst,\
                                               SearchDepth=SearchDepth-1,\
                                               SearchParent=1)
    return filelist
    
'''
if __name__=='__main__':
    a=[{'_name_':'123','_isdir_':True},{'_name_':'abc','_isdir_':False}]
    b=''
    findfilegroups(a,b,SearchParentFirst = 0)
'''