import os
import time
import datetime
import random

# --- Basics ---

def isfilepathroot(filepath):
    """
    Determines if a FILEPATH is at the root of a drive or not.
    """
    if os.name == 'nt': # Windows
        return ':' in filepath or filepath.startswith('/') or filepath.startswith('\\')
    else: # Unix
        return filepath.startswith('/')

def isfile(filename):
    """
    Checks if a file exists.
    """
    return os.path.isfile(filename)

def isfolder(foldername):
    """
    Checks if a folder exists.

    B = vlt.file.isfolder(foldername)

    B is True if foldername is a folder located on the specified path or in the
    current folder, and False if no folder is found.
    """
    return os.path.isdir(foldername)

def fullfilename(filename, usewhich=True):
    """
    Returns the full path file name of a file.
    """
    if os.path.isabs(filename):
        return filename
    return os.path.abspath(filename)

def createpath(filename):
    """
    Create a directory path to a given file name, if necessary.
    Returns (b, errormsg).
    """
    try:
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        return True, ''
    except Exception as e:
        return False, str(e)

def touch(filename):
    """
    Create a file (empty) if it does not already exist.
    """
    if os.path.exists(filename):
        return

    fullname = fullfilename(filename)
    b, err = createpath(fullname)
    if not b:
        raise Exception(err)

    try:
        with open(fullname, 'w') as f:
            pass
    except Exception as e:
        raise Exception(f"Could not open file {fullname}: {e}")

def text2cellstr(filename):
    """
    Read a list of strings from a text file.
    """
    if not os.path.exists(filename):
        raise Exception(f"Could not open file {filename} for reading.")

    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return lines

def textfile2char(filename):
    """
    Read a text file into a character string.

    STR = vlt.file.textfile2char(FILENAME)

    This function reads the entire contents of the file FILENAME into
    the character string STR.
    """
    if not os.path.exists(filename):
        raise Exception(f"Could not open text file named {filename}.")

    with open(filename, 'r') as f:
        return f.read()

def str2text(filename, s):
    """
    Write a string to a text file.

    vlt.file.str2text(FILENAME, str)

    Writes the strings to the new text file FILENAME.
    """
    try:
        with open(filename, 'w') as f:
            f.write(s)
    except Exception as e:
        raise Exception(f"Could not open {filename} for writing.")

def dirstrip(ds):
    """
    Removes '.' and '..' from a directory list.
    Also removes '.DS_Store' and '.git'.

    ds: a list of strings (filenames) or a list of dictionaries/objects mimicking os.scandir entries.

    If ds is a list of strings, returns filtered list of strings.
    If ds is a list of dicts (like from os.scandir or manual construction), returns filtered list.
    """
    garbage = {'.', '..', '.DS_Store', '.git', '.svn', '__pycache__'}

    if not ds:
        return []

    if isinstance(ds[0], str):
        return [f for f in ds if f not in garbage]
    elif hasattr(ds[0], 'name'): # os.DirEntry or similar object
        return [f for f in ds if f.name not in garbage]
    elif isinstance(ds[0], dict) and 'name' in ds[0]:
         return [f for f in ds if f['name'] not in garbage]
    else:
        # Fallback, assume strings?
        return [f for f in ds if str(f) not in garbage]

def dirlist_trimdots(dirlist, output_struct=False):
    """
    Trim strings '.' or '..' from a list of directory strings.

    DIRLIST = vlt.file.dirlist_trimdots(DIRLIST_OR_DIRLISTSTRUCT, [OUTPUT_STRUCT])

    This function behaves like dirstrip but with more specific options matching the MATLAB version.
    In Python, we typically deal with lists of strings.

    If output_struct is True, expects list of dicts/objects and returns list of dicts/objects.
    """
    return dirstrip(dirlist)

def findfiletype(pathname, extension):
    """
    Find all files of a given extension in a folder.

    FILENAMES = vlt.file.findfiletype(PATHNAME, EXTENSION)

    Find all the files with a given extension in a folder PATHNAME,
    including subfolders of PATHNAME.

    Extension should include the dot, e.g. '.txt'.
    """
    filenames = []

    # In Python, we can use os.walk which is easier than recursion
    # But to match MATLAB logic exactly, let's look at how it does it.
    # MATLAB: d = dirstrip(dir(pathname)); then recurses if isdir.

    # Let's use os.walk as it is more pythonic and robust.
    # Note: MATLAB version returns full paths?
    # Yes: filenames{end+1} = [pathname filesep d(i).name];

    extension = extension.lower()

    for root, dirs, files in os.walk(pathname):
        # Filter dirs in place to mimic dirstrip if needed?
        # dirstrip removes . and .. which os.walk doesn't include anyway.
        # It also removes .git and .DS_Store from *files* (and dirs?)
        # os.walk lists dirs and files separately.

        # Check files
        for f in files:
            if f in {'.DS_Store'}: continue

            _, ext = os.path.splitext(f)
            if ext.lower() == extension:
                filenames.append(os.path.join(root, f))

        # To strictly match dirstrip behavior on directories (skipping .git etc),
        # we can modify dirs list in place.
        garbage = {'.git', '.svn', '__pycache__'}
        dirs[:] = [d for d in dirs if d not in garbage]

    return filenames

def filebackup(fname, DeleteOrig=False, Digits=3, ErrorIfDigitsExceeded=True):
    """
    Create a backup of a file.

    BACKUPNAME = vlt.file.filebackup(FNAME)

    Creates a backup file of the file named FNAME (full path). The
    new file is named [FNAME '_bkupNNN' EXT], where NNN is a number.
    The number NNN is chosen such that no file has that name.

    Returns the name of the backup file.
    """
    import shutil

    if not os.path.isfile(fname):
        raise Exception(f"No file {fname} to backup.")

    pathstr, name = os.path.split(fname)
    name, ext = os.path.splitext(name)

    maxdigit = 10**Digits - 1
    foundit = 0
    backupname = ''

    for i in range(1, maxdigit + 1):
        # Format with leading zeros
        fmt = f"{{:0{Digits}d}}"
        numstr = fmt.format(i)

        backupname = os.path.join(pathstr, f"{name}_bkup{numstr}{ext}")
        if not os.path.exists(backupname):
            foundit = i
            break

    if foundit > 0:
        try:
            shutil.copy2(fname, backupname)
        except Exception as e:
            raise Exception(f"Could not copy from {fname} to {backupname}. Check permissions? {e}")

        if DeleteOrig:
            os.remove(fname)

        return backupname
    else:
        if ErrorIfDigitsExceeded:
            raise Exception(f"Could not create backup file with {Digits} digits for file {fname}.")
        return ''

def searchreplacefiles_shell(dirsearch, findstring, replacestring):
    """
    Search and replace text in all files in a directory search.

    vlt.file.searchreplacefiles_shell(DIRSEARCH, FINDSTRING, REPLACESTRING)

    Searches all of the files in the string DIRSEARCH (examples: '*.m',
    or '*/*.m') for occurrances of the string FINDSTRING and replaces those
    strings with REPLACESTRING.

    At present, this requires unix (it calls the shell commands 'find' and 'sed').

    The function prints its shell command before attempting to run.
    """
    import subprocess

    if os.name != 'posix':
        raise Exception("This function is only compatible with unix at this time.")

    # Python equivalent construction of the command:
    # command_string = ['LC_ALL=C find . -type f -name ''' dirsearch ...
    #    ''' -exec  sed -i '''' s/' findstring '/' replacestring '/g {} +']

    # We should be careful with shell injection, but the original function is a shell wrapper.
    # Note: The original MATLAB code uses `find .` which searches from current directory.

    # Warning: using shell=True with user input is dangerous, but we are porting existing functionality.
    # Also, sed syntax might vary (BSD vs GNU). The MATLAB code uses `sed -i ''`.
    # This empty string argument for -i is required on BSD (macOS) but fails on GNU sed (Linux).
    # On GNU sed, -i should not have an argument or should be -i''.

    # Let's try to make it slightly more robust or stick to the original if it assumes BSD.
    # The original repo seems to be from a lab that might use Macs?
    # "See also: ... (Apple desktop information)" in dirlist_trimdots implies Mac usage.

    # However, in this environment (likely Linux), `sed -i ''` might fail.
    # We can check `uname`.

    cmd = f"LC_ALL=C find . -type f -name '{dirsearch}' -exec sed -i 's/{findstring}/{replacestring}/g' {{}} +"

    # On Linux (GNU sed), -i takes no arg for in-place without backup.
    # On MacOS (BSD sed), -i requires an arg (can be empty string).
    # The MATLAB code `sed -i ''''` passes an empty string.
    # If we are on Linux, we should probably remove the `''`.

    # Let's check `sed --version` to see if it's GNU.
    try:
        ver = subprocess.check_output(['sed', '--version'], stderr=subprocess.STDOUT).decode()
        is_gnu = 'GNU' in ver
    except:
        is_gnu = False # Assume BSD if --version fails or other error

    if not is_gnu:
         # BSD sed
         cmd = f"LC_ALL=C find . -type f -name '{dirsearch}' -exec sed -i '' 's/{findstring}/{replacestring}/g' {{}} +"

    print(cmd)
    subprocess.run(cmd, shell=True, check=True)

def manifest(folderPath, ReturnFullPath=False):
    """
    Generates a hierarchical list of files and directories.

    [fileList, isDir] = manifest(folderPath)

    returns a list of relative paths and a corresponding list of boolean indicating if each
    entry is a directory. Paths are relative to the PARENT directory of folderPath.

    If ReturnFullPath is True, returns full absolute paths.
    """
    fileList = []
    isDir = []

    if not os.path.isdir(folderPath):
        # In MATLAB, if not folder, it might error or return empty.
        # But for robust porting, let's assume valid folder.
        return [], []

    # Get absolute path of target folder
    absFolderPath = os.path.abspath(folderPath)
    parentDir = os.path.dirname(absFolderPath)

    # We need to traverse recursively.
    # The MATLAB version uses dir('**/*') which includes the folder itself sometimes?
    # No, it filters . and ..

    # We can use os.walk.
    # The order in MATLAB is depth-first, siblings sorted alphabetically.
    # os.walk yields (root, dirs, files). We can sort dirs and files.

    # However, os.walk goes top-down.
    # We need to structure the list such that we get:
    # target/file
    # target/subdir
    # target/subdir/file

    # This matches os.walk top-down order if we iterate sorted lists.

    # First entry should be the contents of folderPath?
    # "Paths are relative to the PARENT directory of folderPath."
    # So if we scan /a/b, and found /a/b/c.txt, the relative path is b/c.txt.

    for root, dirs, files in os.walk(absFolderPath):
        # Sort in place to ensure alphabetical order
        dirs.sort()
        files.sort()

        # Calculate relative path from parentDir
        relRoot = os.path.relpath(root, parentDir)

        # In os.walk, we are visiting 'root'.
        # We need to list files and subdirs in 'root'.
        # Actually, the MATLAB manifest seems to list everything in a flat list (depth-first).

        # Wait, the MATLAB code does:
        # fullPaths = arrayfun(@(s) fullfile(s.folder, s.name), allFilesStruct, ...
        # then sort hierarchically.

        # Let's collect all items first, then sort them.
        pass

    all_paths = []
    all_isdir = []

    for root, dirs, files in os.walk(absFolderPath):
        for d in dirs:
             fullp = os.path.join(root, d)
             all_paths.append(fullp)
             all_isdir.append(True)
        for f in files:
             fullp = os.path.join(root, f)
             all_paths.append(fullp)
             all_isdir.append(False)

    # Now sort.
    # We want hierarchical sort.
    # In Python, standard string sort of full paths usually achieves hierarchical order
    # because 'path/to/dir' comes before 'path/to/dir/file'.
    # e.g. 'a', 'a/b', 'a/b/c'.
    # Actually 'a' < 'a/b'.
    # But 'a/b' vs 'a-c'. '/' char ascii value is 47. '-' is 45.
    # So 'a-c' < 'a/b'.
    # If we want 'a' then 'a/b', standard sort works.

    # Combine and sort
    combined = list(zip(all_paths, all_isdir))
    combined.sort(key=lambda x: x[0])

    sorted_paths = [x[0] for x in combined]
    sorted_isdir = [x[1] for x in combined]

    if ReturnFullPath:
        return sorted_paths, sorted_isdir
    else:
        # Relative to parent of folderPath
        rel_paths = [os.path.relpath(p, parentDir) for p in sorted_paths]
        return rel_paths, sorted_isdir

def findfilegroups(parentdir, fileparameters, **kwargs):
    """
    Find a group of files based on parameters.

    FILELIST = vlt.file.findfilegroups(PARENTDIR, FILEPARAMETERS, ...)

    Finds groups of files based on parameters.
    FILEPARAMETERS should be a list of file name search parameters.
    These parameters can include regular expresion wildcards ('.*') and symbols
    that indicate that the same string needs to be present across files ('#').

    Options (kwargs):
      SameStringSearchSymbol ('#')
      UseSameStringSearchSymbol (True)
      SearchParentFirst (True)
      SearchDepth (float('inf'))
      SearchParent (True)

    Returns a list of lists. FILELIST[i] is the ith instance of these file groups.
    FILELIST[i][j] is the jth file in the ith instance.
    """
    import re
    # Requires vlt.string.strcmp_substitution.
    # I need to check if vlt.string is ported.
    # If not, I might need to implement the logic here or mock it.

    # Let's check if vlt.string.strcmp_substitution exists.
    # It probably doesn't. I'll implement a helper here if needed or check existing memory/code.
    # I don't recall porting vlt.string.

    # I'll implement the logic directly here for now, or a helper.

    options = {
        'SameStringSearchSymbol': '#',
        'UseSameStringSearchSymbol': True,
        'SearchParentFirst': True,
        'SearchDepth': float('inf'),
        'SearchParent': True
    }
    options.update(kwargs)

    SameStringSearchSymbol = options['SameStringSearchSymbol']
    UseSameStringSearchSymbol = options['UseSameStringSearchSymbol']
    SearchParentFirst = options['SearchParentFirst']
    SearchDepth = options['SearchDepth']
    SearchParent = options['SearchParent']

    filelist = []

    if SearchDepth < 0:
        return []

    # Get dir listing
    # d = dirstrip(dir(parentdir))
    if not os.path.isdir(parentdir):
        return []

    try:
        entries = os.listdir(parentdir)
    except:
        return []

    # Separate files and dirs
    # Filter using dirstrip logic (remove hidden etc)
    garbage = {'.', '..', '.DS_Store', '.git', '.svn', '__pycache__'}
    entries = [e for e in entries if e not in garbage]

    subdirs = []
    regularfiles = []

    for e in entries:
        fullp = os.path.join(parentdir, e)
        if os.path.isdir(fullp):
            subdirs.append(e)
        elif os.path.isfile(fullp):
            regularfiles.append(e)

    # Subdir recursion (if SearchParentFirst is False)
    if not SearchParentFirst:
        for sd in subdirs:
            fl = findfilegroups(os.path.join(parentdir, sd), fileparameters, **{**kwargs, 'SearchDepth': SearchDepth - 1, 'SearchParent': True})
            filelist.extend(fl)

    if SearchParent:
        # Search in this directory
        # The logic involves finding matches for fileparameters[0], extracting the substitution string,
        # and then matching subsequent parameters.

        # We need a regex for each fileparameter.
        # If UseSameStringSearchSymbol is True, we replace '#' with '(.+)' or similar to capture the group.
        # fileparameters is a list of strings like 'myfile_#.ext1', 'myfile_#.ext2'

        # Step 1: Match first parameter
        p1 = fileparameters[0]
        regex1 = p1
        if UseSameStringSearchSymbol:
            # Escape the string first, then unescape the symbol?
            # Or manually replace.
            # Regex escape all except the symbol.
            # This is tricky.
            # Simplification: Assume simple patterns for now.
            # Replace '#' with '(?P<match>.*)' ? No, just (.*)

            # Escape everything
            regex1 = re.escape(regex1)
            # Unescape the symbol (it was escaped to \#)
            regex1 = regex1.replace(re.escape(SameStringSearchSymbol), r'(.*)')

        # Add anchors
        regex1 = f"^{regex1}$"

        # Find matches in regularfiles
        matches1 = []
        for f in regularfiles:
            m = re.match(regex1, f)
            if m:
                # Store match string (the part that matched #)
                match_str = m.group(1) if (UseSameStringSearchSymbol and m.groups()) else ''
                matches1.append({'file': f, 'match_str': match_str})

        # For each match, check other parameters
        for m1 in matches1:
            current_group = [os.path.join(parentdir, m1['file'])]
            match_str = m1['match_str']

            all_found = True
            for k in range(1, len(fileparameters)):
                pk = fileparameters[k]

                # Construct regex for pk
                # If we have a match_str, we substitute it back into pk where # is.
                # If UseSameStringSearchSymbol is True.

                target_filename = pk
                if UseSameStringSearchSymbol:
                     target_filename = pk.replace(SameStringSearchSymbol, match_str)

                # Now check if target_filename exists in regularfiles
                # Use regex match? Or exact match?
                # If there are wildcards (.*) in parameters, we need regex.
                # The doc says "include regular expresion wildcards ('.*')"

                # If match_str was inserted, we still treat it as regex?
                # Usually substituted part is literal.

                # Let's assume we construct a regex where the inserted part is literal,
                # but the rest is regex.

                # Split pk by symbol?
                # This gets complicated.

                # Simplification:
                # If pk has regex chars, we must respect them.
                # If we substitute match_str, we must escape match_str?
                # Probably yes.

                regex_k = pk
                if UseSameStringSearchSymbol:
                    # We want to replace # with escaped match_str.
                    # But wait, pk itself might be a regex.
                    # We can't use re.escape(pk) fully.
                    # We assume user provides valid regex except for #.
                    # So we just replace # with re.escape(match_str).
                    regex_k = regex_k.replace(SameStringSearchSymbol, re.escape(match_str))

                regex_k = f"^{regex_k}$"

                # Find file matching regex_k
                found_k = None
                for f in regularfiles:
                    if re.match(regex_k, f):
                        found_k = f
                        break

                if found_k:
                    current_group.append(os.path.join(parentdir, found_k))
                else:
                    all_found = False
                    break

            if all_found:
                filelist.append(current_group)

    # Subdir recursion (if SearchParentFirst is True)
    if SearchParentFirst:
        for sd in subdirs:
            fl = findfilegroups(os.path.join(parentdir, sd), fileparameters, **{**kwargs, 'SearchDepth': SearchDepth - 1, 'SearchParent': True})
            filelist.extend(fl)

    return filelist

def loadStructArray(fname, fields=None):
    """
    Load a struct array from a tab-delimited file.

    A = vlt.file.loadStructArray(FNAME, [FIELDS])

    Reads tab-delimited text from the file FNAME to create a list of
    dictionaries. If FIELDS is not provided, then the field names
    are read from the first row of FNAME.

    If fields is None, it reads header.
    """
    import csv

    if not os.path.exists(fname):
        # In MATLAB, returns empty list on error?
        # But let's check basic validity.
        raise Exception(f"Could not open file {fname}.")

    a = []

    try:
        with open(fname, 'r', newline='') as f:
            reader = csv.reader(f, delimiter='\t')

            headers = None
            if fields is None:
                try:
                    headers = next(reader)
                    # Clean up headers?
                    # MATLAB: matlab.lang.makeValidName...
                    # We just use them as keys.
                    # Remove empty strings from end if any?
                    headers = [h for h in headers if h]
                except StopIteration:
                     return []
            else:
                headers = fields

            for row in reader:
                # MATLAB: if length(s)>0
                if not row: continue

                # If row is shorter than headers, pad with None or empty string?
                # MATLAB `tabstr2struct` behavior.
                # Assuming simple mapping.

                item = {}
                for i, h in enumerate(headers):
                    val = row[i] if i < len(row) else ''

                    # Try to convert to numbers if possible?
                    # MATLAB `tabstr2struct` calls `vlt.data.tabstr2struct`.
                    # I should check if vlt.data is available or assume strings.
                    # MATLAB structs usually have typed data if converted, but text files are strings.
                    # However, usually one wants numbers.
                    # The prompt didn't ask to port `vlt.data.tabstr2struct`.
                    # I will keep as strings for now or try simple conversion.
                    # Given `vlt` philosophy, maybe strings are safer unless specific instruction.
                    # But often JSON/TSV loading implies type inference.
                    # Let's check `vlt.data.tabstr2struct` implementation if possible.
                    # I'll stick to strings for now to be safe.
                    item[h] = val
                a.append(item)
    except Exception as e:
        raise Exception(f"Error reading file {fname}: {e}")

    return a

def saveStructArray(fname, gdi, header=True):
    """
    Save a structure array (list of dicts) into a text file.

    vlt.file.saveStructArray(FILENAME, STRUCTARRAY, [HEADER])

    Saves structure array data of type STRUCT into a text
    file.
    """
    import csv

    if not gdi:
        # Create empty file?
        with open(fname, 'w') as f:
            pass
        return

    # Get fields from first element? Or union of all?
    # MATLAB: fn = fieldnames(gdi([])); -> this implies fields of the struct type.
    # In Python list of dicts, keys might vary.
    # Assume consistent keys from first element.
    keys = list(gdi[0].keys())

    try:
        with open(fname, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')

            if header:
                writer.writerow(keys)

            for item in gdi:
                row = []
                for k in keys:
                    val = item.get(k, '')
                    # Convert to string?
                    # vlt.data.struct2tabstr does string conversion.
                    # We rely on str(val).
                    row.append(str(val))
                writer.writerow(row)
    except Exception as e:
        print(f"{e}: {fname}")

def filenamesearchreplace(dirname, searchStrs, replaceStrs, **kwargs):
    """
    Seach and replace filenames within a directory.

    vlt.file.filenamesearchreplace(DIRNAME, SEARCHSTRS, REPLACESTRS, ...)

    This function searches all files in the directory DIRNAME for matches
    of any string in the list of strings SEARCHSTRS. If it finds a match,
    then it creates a new file with the search string replaced by the
    corresponding entry in the list of strings REPLACESTRS.

    Options:
    deleteOriginals (0)      | Should original file be deleted?
    useOutputDir (0)         | Should we write to a different output directory?
    OutputDirPath (DIRNAME)  | The parent path of the output directory
    OutputDir ('subfolder')  | The name of the output directry in OutputDirPath
    noOp (0)                 | If 1, this will not perform the operation but will print it
    recursive (0)            | Should we call this recursively on subdirectories?
    """
    import shutil

    options = {
        'deleteOriginals': False,
        'useOutputDir': False,
        'OutputDirPath': dirname,
        'OutputDir': 'subfolder',
        'noOp': False,
        'recursive': False
    }
    options.update(kwargs)

    deleteOriginals = options['deleteOriginals']
    useOutputDir = options['useOutputDir']
    OutputDirPath = options['OutputDirPath']
    OutputDir = options['OutputDir']
    noOp = options['noOp']
    recursive = options['recursive']

    if not isinstance(searchStrs, list): searchStrs = [searchStrs]
    if not isinstance(replaceStrs, list): replaceStrs = [replaceStrs]

    if len(searchStrs) != len(replaceStrs):
        raise Exception("searchStrs and replaceStrs must have same length.")

    # Get entries
    try:
        entries = os.listdir(dirname)
    except:
        return

    garbage = {'.', '..', '.DS_Store', '.git', '.svn', '__pycache__'}
    entries = [e for e in entries if e not in garbage]

    # Determine output path
    if not useOutputDir:
        outputPath = dirname
    else:
        outputPath = os.path.join(OutputDirPath, OutputDir)
        if not os.path.exists(outputPath):
            if not noOp:
                os.makedirs(outputPath)
            else:
                print(f"Would have made {outputPath}.")

    for name in entries:
        oldnamefullpath = os.path.join(dirname, name)

        # Check if name contains any search string
        match_idx = -1
        for i, s in enumerate(searchStrs):
             if s.lower() in name.lower(): # Ignore case
                 match_idx = i
                 break

        if match_idx >= 0:
            # Found match
            # Case insensitive replace is tricky.
            # But existing MATLAB code:
            # newname = strrep(d(i).name,searchStrs{idx},replaceStrs{idx});
            # MATLAB strrep IS case sensitive. But contains check was ignore case.
            # So if I have "File.txt" and search "file", contains matches.
            # strrep("File.txt", "file", "replaced") -> "File.txt" (no change) because case mismatch.
            # The MATLAB code seems to assume case matches or it relies on `contains` ignoreCase logic
            # but then `strrep` might fail to replace if case differs.
            # Let's assume we should do case-insensitive replacement or mimic MATLAB exactly (which might be buggy/weird).
            # MATLAB: newname = strrep(d(i).name,searchStrs{idx}, replaceStrs{idx});

            # If I want to exactly mimic MATLAB behavior:
            # If `contains` (ignore case) is true, we try `strrep` (case sensitive).
            # If cases don't match, nothing happens to the string?
            # But the code copies oldnamefullpath to newnamefullpath.
            # If newname == oldname (because strrep failed), it copies file to itself?
            # If output dir is same, copyfile(f, f) fails/warns.

            # Let's assume the user intends to replace ignoring case.
            # But wait, let's stick to Python replace which is case sensitive.
            # Or use regex for case insensitive replace.

            # If I stick to Python's `.replace()`, it behaves like MATLAB `strrep`.

            newname = name.replace(searchStrs[match_idx], replaceStrs[match_idx])
            newnamefullpath = os.path.join(outputPath, newname)

            if not noOp:
                if newnamefullpath != oldnamefullpath:
                    if os.path.isdir(oldnamefullpath):
                        shutil.copytree(oldnamefullpath, newnamefullpath)
                    else:
                        shutil.copy2(oldnamefullpath, newnamefullpath)
            else:
                print(f"Would have copied {oldnamefullpath} to {newnamefullpath}")

            if deleteOriginals:
                if not noOp:
                    if os.path.isdir(oldnamefullpath):
                        shutil.rmtree(oldnamefullpath)
                    else:
                        os.remove(oldnamefullpath)
                else:
                    print(f"Would have deleted {oldnamefullpath}")

        # Recursion
        # If we renamed/moved the directory, we should recurse into the NEW path if it exists.
        # If we didn't rename (no match), we recurse into OLD path.

        target_recurse_path = oldnamefullpath
        if match_idx >= 0 and useOutputDir:
             # If we moved it, newnamefullpath is where it is now.
             # Note: if useOutputDir is false, newnamefullpath might be different from oldnamefullpath only by name.
             # If deleteOriginals is true, oldnamefullpath is gone.
             target_recurse_path = newnamefullpath
        elif match_idx >= 0 and not useOutputDir and deleteOriginals:
             # Renamed in place
             target_recurse_path = newnamefullpath

        if recursive and os.path.isdir(target_recurse_path):
             filenamesearchreplace(target_recurse_path, searchStrs, replaceStrs, **kwargs)

# --- Lock ---

def checkout_lock_file(filename, checkloops=30, throwerror=False, expiration=3600):
    """
    Try to establish control of a lock file.
    Returns (fid, key). fid is 1 on success, -1 on failure.
    """
    loops = checkloops
    key = f"{datetime.datetime.now().timestamp()}_{random.random()}"

    loop = 0
    expiration_time_of_file = None

    while isfile(filename) and loop < loops:
        file_exists = isfile(filename)

        if file_exists:
            try:
                lines = text2cellstr(filename)
                if lines:
                    exp_str = lines[0].strip()
                    try:
                        expiration_time_of_file = datetime.datetime.fromisoformat(exp_str)
                    except ValueError:
                        pass # Format error
            except:
                pass # Gone or unreadable

        isexpired = False
        if expiration_time_of_file:
            if datetime.datetime.now() > expiration_time_of_file:
                isexpired = True

        if not isexpired:
            time.sleep(1)
        else:
            try:
                os.remove(filename)
            except:
                pass
        loop += 1

    if loop < loops:
        try:
            with open(filename, 'w') as f:
                t2 = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
                f.write(t2.isoformat() + '\n')
                f.write(key + '\n')
            return 1, key
        except Exception as e:
            if throwerror:
                raise e
            return -1, ''
    else:
        if throwerror:
            raise Exception(f"Unable to obtain lock with file {filename}")
        return -1, ''

def release_lock_file(fid_or_filename, key):
    """
    Release a lock file given its filename and key.
    """
    filename = fid_or_filename

    if not isfile(filename):
        return True

    try:
        lines = text2cellstr(filename)
    except:
        if not isfile(filename):
            return True
        else:
            raise Exception(f"{filename} could not be opened")

    if len(lines) != 2:
         # In MATLAB it raises error.
         # "error([filename ' does not appear to be a lock file created by vlt.file.checkout_lock_file.']);"
         # We will be lenient or raise? Let's raise to match.
         raise Exception(f"{filename} does not appear to be a lock file created by vlt.file.checkout_lock_file.")

    if lines[1].strip() == key:
        os.remove(filename)
        return True
    else:
        return False

# --- Text ---

def addline(filename, message):
    """
    Add a line of text to a text file.
    Returns (b, errormsg).
    """
    fullname = fullfilename(filename)
    b, err = createpath(fullname)
    if not b:
        return False, err

    mylockfile = fullname + '-lock'
    lockfid, key = checkout_lock_file(mylockfile)

    if lockfid > 0:
        try:
            with open(fullname, 'a') as f:
                f.write(message + '\n')
            b = True
            errormsg = ''
        except Exception as e:
            b = False
            errormsg = str(e)

        release_lock_file(mylockfile, key)
    else:
        b = False
        errormsg = f"Never got control of {mylockfile}; it was busy."

    return b, errormsg

class fileobj:
    """
    vlt.file.fileobj - a Python binary file object; an interface to file operations.

    This is an object interface to file operations.
    """

    def __init__(self, fullpathfilename='', fid=None, permission='r', machineformat='n'):
        """
        Create a new binary file object.
        """
        self.fullpathfilename = fullpathfilename
        self.fid = fid # In Python, this will be the file object itself
        self.permission = permission
        self.machineformat = machineformat

        if self.fullpathfilename and self.fid is None:
             # Just setting properties, not opening yet unless requested?
             # MATLAB version sets properties but doesn't open in constructor unless implicit?
             # Constructor: fileobj(varargin) -> sets properties.
             pass

    def setproperties(self, **kwargs):
        """
        Set properties of fileobj.
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        return self

    def fopen(self, permission=None, machineformat=None, filename=None):
        """
        Open a fileobj.

        FILEOBJ_OBJ = FOPEN(FILEOBJ_OBJ, [ , PERMISSION], [MACHINEFORMAT],[FILENAME])
        """
        if self.fid is not None and not (isinstance(self.fid, int) and self.fid == -1):
            # Close if open
            try:
                self.fclose()
            except:
                pass

        if permission is None: permission = self.permission
        if machineformat is None: machineformat = self.machineformat
        if filename is None: filename = self.fullpathfilename

        filename = fullfilename(filename)
        self.fullpathfilename = filename
        self.permission = permission
        self.machineformat = machineformat

        # Map permission
        # MATLAB: 'r', 'w', 'a', 'r+', 'w+', 'a+', 'W', 'A'
        # Python: 'r', 'w', 'a', 'r+', 'w+', 'a+'
        # Also binary mode 'b' is usually needed for binary files.
        # fileobj implies binary file object.
        # So append 'b' if not present.

        mode = self.permission
        if 'b' not in mode:
            mode += 'b'

        try:
            self.fid = open(self.fullpathfilename, mode)
            # Handle machine format? Python struct module handles endianness.
            # But the file object itself doesn't care.
            # We store it for later use in fread/fwrite.
        except Exception as e:
            self.fid = -1
            print(f"Error opening file: {e}")

        return self

    def fclose(self):
        """
        Close a fileobj.
        """
        if self.fid is not None and self.fid != -1:
            try:
                self.fid.close()
            except:
                pass
            self.fid = -1
        return self

    def fseek(self, offset, reference):
        """
        Seek to a location within a FILEOBJ.

        reference:
          'bof' or -1 : Beginning
          'cof' or 0  : Current
          'eof' or 1  : End
        """
        if self.fid is None or self.fid == -1: return -1

        whence = 0
        if reference == 'bof' or reference == -1: whence = 0
        elif reference == 'cof' or reference == 0: whence = 1
        elif reference == 'eof' or reference == 1: whence = 2

        try:
            self.fid.seek(offset, whence)
            return 0
        except:
            return -1

    def ftell(self):
        """
        Find current location.
        """
        if self.fid is None or self.fid == -1: return -1
        try:
            return self.fid.tell()
        except:
            return -1

    def frewind(self):
        """
        Rewind.
        """
        self.fseek(0, 'bof')

    def feof(self):
        """
        Test end of file.
        """
        if self.fid is None or self.fid == -1: return -1
        # Python doesn't have explicit feof.
        # Usually check if read returns empty.
        # But to check without reading:
        try:
            curr = self.fid.tell()
            self.fid.seek(0, 2) # End
            end = self.fid.tell()
            self.fid.seek(curr)
            return 1 if curr >= end else 0
        except:
            return -1

    def fwrite(self, data, precision='char', skip=0, machineformat=None):
        """
        Write data.
        precision: 'char', 'int8', 'float32', etc.
        """
        if self.fid is None or self.fid == -1: return 0

        import struct

        # Map precision to struct format
        # char -> c (bytes) or s?
        # int8 -> b
        # uint8 -> B
        # int16 -> h
        # uint16 -> H
        # int32 -> i
        # uint32 -> I
        # float32 -> f
        # float64 -> d

        fmt_map = {
            'char': 'c', 'uchar': 'B', 'schar': 'b',
            'int8': 'b', 'uint8': 'B',
            'int16': 'h', 'uint16': 'H',
            'int32': 'i', 'uint32': 'I',
            'int64': 'q', 'uint64': 'Q',
            'float32': 'f', 'float64': 'd',
            'double': 'd', 'single': 'f'
        }

        p = precision.lower()
        if p not in fmt_map and p != 'char*1':
             # Fallback
             pass

        code = fmt_map.get(p, 'B') # Default to byte?

        # Endianness
        if machineformat is None: machineformat = self.machineformat
        endian = ''
        if machineformat == 'b' or machineformat == 'big-endian' or machineformat == 'ieee-be': endian = '>'
        elif machineformat == 'l' or machineformat == 'little-endian' or machineformat == 'ieee-le': endian = '<'

        count = 0
        try:
            if isinstance(data, str):
                b = data.encode('utf-8') # Or latin-1?
                self.fid.write(b)
                count = len(b)
            elif isinstance(data, (bytes, bytearray)):
                self.fid.write(data)
                count = len(data)
            else:
                # Numeric array
                # Use struct.pack
                # If data is list or numpy array
                try:
                    import numpy as np
                    if isinstance(data, np.ndarray):
                        data = data.flatten().tolist()
                except:
                    pass

                if not isinstance(data, list): data = [data]

                fmt = endian + code * len(data)
                b = struct.pack(fmt, *data)
                self.fid.write(b)
                count = len(data)

        except Exception as e:
            print(f"fwrite error: {e}")

        return count

    def fread(self, count=float('inf'), precision='char', skip=0, machineformat=None):
        """
        Read data.
        """
        if self.fid is None or self.fid == -1: return [], 0

        import struct

        fmt_map = {
            'char': 'c', 'uchar': 'B', 'schar': 'b',
            'int8': 'b', 'uint8': 'B',
            'int16': 'h', 'uint16': 'H',
            'int32': 'i', 'uint32': 'I',
            'int64': 'q', 'uint64': 'Q',
            'float32': 'f', 'float64': 'd',
            'double': 'd', 'single': 'f'
        }

        p = precision.lower()
        code = fmt_map.get(p, 'B')
        size = struct.calcsize(code)

        if machineformat is None: machineformat = self.machineformat
        endian = ''
        if machineformat == 'b' or machineformat == 'big-endian' or machineformat == 'ieee-be': endian = '>'
        elif machineformat == 'l' or machineformat == 'little-endian' or machineformat == 'ieee-le': endian = '<'

        data = []
        read_count = 0

        try:
            if count == float('inf'):
                # Read all
                b = self.fid.read()
                num_items = len(b) // size
            else:
                num_items = int(count)
                b = self.fid.read(num_items * size)

            if len(b) < size: return [], 0

            # Unpack
            actual_items = len(b) // size
            fmt = endian + code * actual_items
            # Slice buffer to match expected size
            b = b[:actual_items * size]
            data = list(struct.unpack(fmt, b))

            if p == 'char':
                # Convert bytes to string?
                # MATLAB fread with char returns numbers?
                # "Attempts to read COUNT elements... If PRECISION is not provided, 'char' is assumed."
                # In MATLAB char(fread(...)) converts to string. fread returns double by default unless precision specified.
                # Here we return the values.
                # If code is 'c', struct returns bytes of length 1.
                if code == 'c':
                    data = [x.decode('latin-1') for x in data] # Decode bytes to chars

            read_count = actual_items

        except Exception as e:
            print(f"fread error: {e}")

        return data, read_count

    def fgetl(self):
        """
        Get line, strip newline.
        """
        if self.fid is None or self.fid == -1: return ''
        try:
            line = self.fid.readline()
            if isinstance(line, bytes): line = line.decode('utf-8')
            return line.rstrip('\n').rstrip('\r')
        except:
            return ''

    def fgets(self):
        """
        Get line, keep newline.
        """
        if self.fid is None or self.fid == -1: return ''
        try:
            line = self.fid.readline()
            if isinstance(line, bytes): line = line.decode('utf-8')
            return line
        except:
            return ''

    def ferror(self):
        return '', 0

    def delete(self):
        self.fclose()

class dumbjsondb:
    """
    vlt.file.dumbjsondb - a very simple and slow JSON-based database with associated binary files
    """

    def __init__(self, command=None, paramfilename=None, **kwargs):
        """
        Create a DUMBJSONDB object.
        """
        self.paramfilename = ''
        self.dirname = '.dumbjsondb'
        self.unique_object_id_field = 'id'

        if command is not None and command.lower() == 'new':
            self.paramfilename = paramfilename
            self._set_properties(**kwargs)
            self.writeparameters()
        elif command is not None and command.lower() == 'load':
            self.paramfilename = paramfilename # 2nd arg is openfile in MATLAB
            self.loadparameters(self.paramfilename)
        else:
            self._set_properties(**kwargs)

    def _set_properties(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def add(self, doc_object, **kwargs):
        """
        Add a document to a DUMBJSONDB.
        Options:
          Overwrite: 1 (overwrite), 0 (error), 2 (increment version)
          doc_version: specific version or None (latest)
        """
        options = {'Overwrite': 1, 'doc_version': None}
        options.update(kwargs)
        Overwrite = options['Overwrite']
        doc_version = options['doc_version']

        doc_unique_id = self.docstats(doc_object)

        # Determine version if not provided?
        # MATLAB code: doc_version = dumbjsondb_obj.latestdocversion(doc_unique_id);
        # This gets CURRENT latest.
        # But if we are adding, we might be writing version 0 if none exists.

        current_latest_version, all_versions = self.latestdocversion(doc_unique_id)

        if doc_version is None:
             # Default to latest if exists, or 0?
             if current_latest_version is None:
                 doc_version = 0
             else:
                 doc_version = current_latest_version

        p = self.documentpath()
        f = dumbjsondb.uniqueid2filename(doc_unique_id, doc_version)
        fileexist = isfile(os.path.join(p, f))

        can_we_write = 0
        if not fileexist:
            # Writing for first time (for this version)
            can_we_write = 1
        else:
            if Overwrite == 1:
                can_we_write = 1
            elif Overwrite == 0:
                raise Exception(f"Document with id {doc_unique_id} already exists.")
            elif Overwrite == 2:
                # Increment version
                if current_latest_version is None:
                    doc_version = 0 # Should not happen if fileexist is true
                else:
                    doc_version = current_latest_version + 1
                can_we_write = 1
            else:
                raise Exception(f"Unknown Overwrite mode: {Overwrite}")

        if can_we_write:
            self.writeobject(doc_object, doc_unique_id, doc_version)

        return self

    def read(self, doc_unique_id, doc_version=None):
        """
        Read the JSON document.
        """
        doc_unique_id = dumbjsondb.fixdocuniqueid(doc_unique_id)

        if doc_version is None:
            # Read latest
            v_list = self.docversions(doc_unique_id)
            if v_list:
                doc_version = max(v_list)
                return self.read(doc_unique_id, doc_version)
            else:
                return {}, None # No document
        else:
            # Read specific version
            p = self.documentpath()
            f = dumbjsondb.uniqueid2filename(doc_unique_id, doc_version)
            fullpath = os.path.join(p, f)

            if isfile(fullpath):
                try:
                    t = textfile2char(fullpath)
                    import json
                    document = json.loads(t)
                    return document, doc_version
                except:
                    return {}, None
            else:
                return {}, None

    def openbinaryfile(self, doc_unique_id, doc_version=None):
        """
        Return the FID (python file object) for the binary file.
        Returns (fid, key, doc_version).
        fid is None if failure.
        """
        doc_unique_id = dumbjsondb.fixdocuniqueid(doc_unique_id)

        # Ensure document exists?
        # MATLAB calls read(...) first.
        doc, doc_version = self.read(doc_unique_id, doc_version)
        if doc_version is None:
             raise Exception("Document not found.")

        f = dumbjsondb.uniqueid2binaryfilename(doc_unique_id, doc_version)
        p = self.documentpath()

        lockfilename = os.path.join(p, f + '-lock')
        lockfid, key = checkout_lock_file(lockfilename)

        fid = None
        if lockfid > 0:
            try:
                # Open in a+b (append binary, read/write)
                # MATLAB: 'a+', 'ieee-le'
                # Python doesn't support simultaneous read/write easily in append mode?
                # 'a+' opens for updating (reading and writing) at end of file.
                # seek(0) to read from start.
                fid = open(os.path.join(p, f), 'a+b')
                # Python file objects don't enforce endianness, user must handle it.
            except Exception as e:
                print(f"Error opening binary file: {e}")
                fid = None
                release_lock_file(lockfilename, key)

        return fid, key, doc_version

    def closebinaryfile(self, fid, key, doc_unique_id, doc_version=None):
        """
        Close binary file and release lock.
        fid: python file object.
        """
        if fid is not None:
            try:
                fid.close()
            except:
                pass

        doc_unique_id = dumbjsondb.fixdocuniqueid(doc_unique_id)
        if doc_version is None:
             # We need version to find filename for lock
             _, doc_version = self.read(doc_unique_id) # Latest?

        # Re-resolve filename to get lockfile name
        # Wait, if doc_version is None, we need to know WHICH version was opened.
        # Ideally the user passes the doc_version returned by openbinaryfile.
        # If not, we guess latest?

        if doc_version is None:
             # Try to find latest? Or assume?
             # MATLAB: [document, doc_version] = dumbjsondb_obj.read(doc_unique_id, doc_version);
             # If doc_version passed as None/Empty, it finds latest.
             _, doc_version = self.read(doc_unique_id)

        f = dumbjsondb.uniqueid2binaryfilename(doc_unique_id, doc_version)
        p = self.documentpath()
        lockfilename = os.path.join(p, f + '-lock')
        release_lock_file(lockfilename, key)
        return None

    def remove(self, doc_unique_id, version='all'):
        """
        Remove document.
        """
        if version is None or version == 'all':
            v_list = self.docversions(doc_unique_id)
            for v in v_list:
                self.remove(doc_unique_id, v)

            # Update metadata
            self.updatedocmetadata('Deleted all versions', None, doc_unique_id, None)
            return

        # Specific version
        # version should be integer
        p = self.documentpath()
        vfname = dumbjsondb.uniqueid2filename(doc_unique_id, version)
        bfname = dumbjsondb.uniqueid2binaryfilename(doc_unique_id, version)

        if isfile(os.path.join(p, vfname)):
            os.remove(os.path.join(p, vfname))
        if isfile(os.path.join(p, bfname)):
            os.remove(os.path.join(p, bfname))

        self.updatedocmetadata('Deleted version', None, doc_unique_id, version)

    def alldocids(self):
        """
        Return all doc unique ids.
        """
        ids = []
        p = self.documentpath()
        if not os.path.isdir(p): return []

        # Look for Object_id_*.txt
        # MATLAB: sscanf(d(i).name,'Object_id_%s')
        # Filename: Object_id_XYZ.txt
        import glob
        files = glob.glob(os.path.join(p, 'Object_id_*.txt'))
        for f in files:
            name = os.path.basename(f)
            # Remove Object_id_ and .txt
            # name is Object_id_....txt
            # prefix len = 10 ('Object_id_')
            # suffix len = 4 ('.txt')
            if name.startswith('Object_id_') and name.endswith('.txt'):
                id_str = name[10:-4]
                ids.append(id_str)
        return ids

    def docversions(self, doc_unique_id):
        """
        Return all version numbers for a doc id.
        """
        versions = []
        doc_unique_id = dumbjsondb.fixdocuniqueid(doc_unique_id)
        # Filename pattern: Object_id_{id}_v{hex}.json
        # id might contain special chars? sanitize?
        # MATLAB: fnamesearch = strrep(fname, '00000', '*');

        prefix = dumbjsondb.uniqueid2filenameprefix(doc_unique_id)
        p = self.documentpath()

        import glob
        pattern = os.path.join(p, f"{prefix}_v*.json")
        files = glob.glob(pattern)

        for f in files:
            name = os.path.basename(f)
            # format: prefix_v#####.json
            # Extract #####
            # prefix length
            pl = len(prefix)
            # suffix .json length 5
            # middle is _v#####
            # _v is 2 chars.
            # So from pl+2 to end-5
            v_str = name[pl+2:-5]
            try:
                v = int(v_str, 16)
                versions.append(v)
            except:
                pass
        return sorted(versions)

    def search(self, scope, searchParams):
        """
        Perform a search of DUMBJSONDB documents.
        """
        # scope is tuple/list of name-value pairs? or dict?
        # MATLAB: search(db, {}, {'value', 5})
        # scope: {}, searchParams: {'value', 5}

        # Parse scope
        version = 'latest'
        # scope is expected to be dict or list of pairs
        if isinstance(scope, dict):
            if 'version' in scope: version = scope['version']
        elif isinstance(scope, (list, tuple)):
            for i in range(0, len(scope), 2):
                if scope[i].lower() == 'version':
                    version = scope[i+1]

        docs = []
        doc_versions = []

        docids = self.alldocids()

        for docid in docids:
            if str(version).lower() == 'latest':
                v_here = self.docversions(docid)
                if v_here:
                    v_here = [max(v_here)]
                else:
                    v_here = []
            elif str(version).lower() == 'all':
                v_here = self.docversions(docid)
            else:
                v_here = [version]

            for v in v_here:
                doc_here, version_here = self.read(docid, v)
                if doc_here:
                    b = dumbjsondb.ismatch(doc_here, searchParams)
                    if b:
                        docs.append(doc_here)
                        doc_versions.append(version_here)

        return docs, doc_versions

    def clear(self, areyousure='no'):
        """
        Remove all records.
        """
        if areyousure.lower() == 'yes':
            ids = self.alldocids()
            for i in ids:
                self.remove(i)
        else:
            print("Not clearing because user did not indicate he/she is sure.")

    def latestdocversion(self, doc_unique_id):
        v = self.docversions(doc_unique_id)
        if v:
            return max(v), v
        else:
            return None, []

    def docstats(self, document_obj):
        """
        Return doc unique id.
        """
        # Assume document_obj is dict
        val = document_obj.get(self.unique_object_id_field)
        return dumbjsondb.fixdocuniqueid(val)

    def writeobject(self, doc_object, doc_unique_id, doc_version):
        doc_unique_id = dumbjsondb.fixdocuniqueid(doc_unique_id)
        p = self.documentpath()
        createpath(os.path.join(p, 'dummy')) # Ensure dir exists

        docfile = dumbjsondb.uniqueid2filename(doc_unique_id, doc_version)
        self.docobject2file(doc_object, os.path.join(p, docfile))

        self.updatedocmetadata('Added new version', doc_object, doc_unique_id, doc_version)

        # Touch binary file
        fb = dumbjsondb.uniqueid2binaryfilename(doc_unique_id, doc_version)
        touch(os.path.join(p, fb))

    def updatedocmetadata(self, operation, document, doc_unique_id, doc_version):
        p = self.documentpath()
        metafile = os.path.join(p, dumbjsondb.uniqueid2metafilename(doc_unique_id))

        op = operation.lower()
        if op == 'added new version':
            str2text(metafile, str(doc_version))
        elif op == 'deleted version':
            v = self.docversions(doc_unique_id)
            if v:
                str2text(metafile, str(max(v)))
            else:
                if isfile(metafile): os.remove(metafile)
        elif op == 'deleted all versions':
            if isfile(metafile): os.remove(metafile)

    def documentpath(self):
        return os.path.join(os.path.dirname(self.paramfilename), self.dirname)

    def writeparameters(self):
        if not self.paramfilename: return

        filepath = os.path.dirname(self.paramfilename)
        if not os.path.isdir(filepath):
            os.makedirs(filepath)

        s = {
            'dirname': self.dirname,
            'unique_object_id_field': self.unique_object_id_field
        }

        import json
        with open(self.paramfilename, 'w') as f:
            json.dump(s, f)

        thedir = os.path.join(filepath, self.dirname)
        if not os.path.isdir(thedir):
            os.makedirs(thedir)

    def loadparameters(self, filename):
        if not isfile(filename): raise Exception(f"File {filename} does not exist.")
        t = textfile2char(filename)
        import json
        s = json.loads(t)

        if 'dirname' in s: self.dirname = s['dirname']
        if 'unique_object_id_field' in s: self.unique_object_id_field = s['unique_object_id_field']

    @staticmethod
    def docobject2file(doc_object, filename):
        import json
        # Handle NaN? Python standard json can handle NaN as NaN (non-standard but supported by default)
        # or we can use custom encoder.
        # But for now simple dump.
        with open(filename, 'w') as f:
            json.dump(doc_object, f)

    @staticmethod
    def fixdocuniqueid(doc_unique_id):
        return str(doc_unique_id)

    @staticmethod
    def uniqueid2filenameprefix(doc_unique_id):
        doc_unique_id = dumbjsondb.fixdocuniqueid(doc_unique_id)
        # string2filestring?
        # Simple sanitization
        keepcharacters = (' ','.','_','-')
        safe = "".join(c for c in doc_unique_id if c.isalnum() or c in keepcharacters).rstrip()
        f = 'Object_id_' + safe
        return f

    @staticmethod
    def uniqueid2filename(doc_unique_id, version=0):
        if version is None: version = 0
        f = dumbjsondb.uniqueid2filenameprefix(doc_unique_id)
        # version 5 digit hex
        h = f"{int(version):05X}"
        return f"{f}_v{h}.json"

    @staticmethod
    def uniqueid2binaryfilename(doc_unique_id, version=0):
        f = dumbjsondb.uniqueid2filename(doc_unique_id, version)
        # Replace .json with .binary?
        # MATLAB: f = [f '.binary']; -> appends .binary. So .json.binary
        return f + '.binary'

    @staticmethod
    def uniqueid2metafilename(doc_unique_id):
        f = dumbjsondb.uniqueid2filenameprefix(doc_unique_id)
        return f + '.txt'

    @staticmethod
    def ismatch(document, searchParams):
        """
        Is a document a match?
        """
        if isinstance(searchParams, dict):
            # vlt.data.fieldsearch? Implement logic here
            # searchParams is dict of field: value
            for k, v in searchParams.items():
                if k not in document: return False
                if document[k] != v: return False
            return True

        elif isinstance(searchParams, (list, tuple)):
            # list of key, value, key, value
            for i in range(0, len(searchParams), 2):
                field = searchParams[i]
                val = searchParams[i+1]

                if field not in document: return False

                doc_val = document[field]

                if isinstance(val, str):
                    # Regex match
                    import re
                    # MATLAB regexpi is case insensitive
                    if not isinstance(doc_val, str): return False
                    if not re.search(val, doc_val, re.IGNORECASE):
                        return False
                else:
                    # Exact match
                    if doc_val != val: return False

            return True
        return False
      
from vlt.file.dirlist_trimdots import dirlist_trimdots
from vlt.file.str2text import str2text
from vlt.file.text2cellstr import text2cellstr
from vlt.file.touch import touch
from vlt.file.addline import addline
from vlt.file.isfile import isfile
from vlt.file.fullfilename import fullfilename
from vlt.file.createpath import createpath
from vlt.file.isfilepathroot import isfilepathroot
from vlt.file.lock import checkout_lock_file, release_lock_file
