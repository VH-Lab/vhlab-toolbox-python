import os
import time
import datetime
import random
import numpy as np
import json
import struct
import re
import shutil
import vlt.data
import vlt.string

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

def isfolder(filename):
    """
    Checks if a directory exists.
    """
    return os.path.isdir(filename)

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

def cellstr2text(filename, cs):
    """
    Write a list of strings to a text file.

    vlt.file.cellstr2text(filename, cs)

    Writes the list of strings cs to the new text file filename.
    One entry is written per line.
    """
    try:
        with open(filename, 'w') as f:
            for s in cs:
                f.write(str(s) + '\n')
    except Exception as e:
        raise Exception(f"Could not open {filename} for writing: {e}")

def textfile2char(filename):
    """
    Read the entire content of a text file into a string.
    """
    if not os.path.exists(filename):
        raise Exception(f"Could not open file {filename} for reading.")
    with open(filename, 'r') as f:
        return f.read()

def str2text(filename, s):
    """
    Write a string to a text file.
    """
    try:
        with open(filename, 'w') as f:
            f.write(s)
    except Exception as e:
        raise Exception(f"Could not open {filename} for writing: {e}")

def string2filestring(s):
    """
    Convert a string to a valid filename string.
    Replaces non-alphanumeric characters (except - and _) with _.
    """
    # Keep alphanumeric, -, _
    # Replace others with _
    s_safe = re.sub(r'[^a-zA-Z0-9\-_]', '_', str(s))
    return s_safe

def filename_value(filename_or_fileobj):
    """
    Return the string of a filename whether it is a filename or inside a fileobj.

    filename = vlt.file.filename_value(filename_or_fileobj)

    Given a value which may be a filename or a vlt.file.fileobj object (or similar),
    return either the filename or the fullpathfilename field of the object.
    """
    # Check if it has 'fullpathfilename' attribute
    if hasattr(filename_or_fileobj, 'fullpathfilename'):
        return str(filename_or_fileobj.fullpathfilename)
    elif hasattr(filename_or_fileobj, 'name') and hasattr(filename_or_fileobj, 'read'): # File-like object
        return str(filename_or_fileobj.name)
    else:
        return str(filename_or_fileobj)

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

# --- Classes ---

class fileobj:
    """
    vlt.file.fileobj - a binary file object wrapper.
    Ports MATLAB vlt.file.fileobj.
    """
    def __init__(self, **kwargs):
        self.fullpathfilename = ''
        self.fid = None # Python file object
        self.permission = 'r'
        self.machineformat = 'native' # 'little-endian', 'big-endian', 'native'

        # Apply kwargs (vlt.data.assign equivalent)
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

        # If filename passed as positional arg in MATLAB, handle via kwargs logic if mapped,
        # or separate init logic if needed. Here we assume kwargs.

    def fopen(self, permission=None, machineformat=None, filename=None):
        if self.fid is not None and not self.fid.closed:
            self.fclose()

        if permission is not None:
            self.permission = permission
        if machineformat is not None:
            self.machineformat = machineformat
        if filename is not None:
            self.fullpathfilename = filename

        self.fullpathfilename = fullfilename(self.fullpathfilename)

        mode = self.permission.replace('b', '') + 'b' # Ensure binary
        # Python open modes: r, w, a, r+, w+, a+
        # MATLAB permissions: r, w, a, r+, w+, a+, W, A
        # Simple mapping:

        try:
            self.fid = open(self.fullpathfilename, mode)
            return self # Success
        except Exception as e:
            self.fid = None
            raise e

    def fclose(self):
        if self.fid is not None:
            try:
                self.fid.close()
            except:
                pass
            self.fid = None

    def fseek(self, offset, reference='bof'):
        # reference: 'bof' (0), 'cof' (1), 'eof' (2)
        whence = 0
        if reference == 'bof' or reference == -1: whence = 0
        elif reference == 'cof' or reference == 0: whence = 1
        elif reference == 'eof' or reference == 1: whence = 2

        if self.fid is not None:
            self.fid.seek(offset, whence)
            return 0
        return -1

    def ftell(self):
        if self.fid is not None:
            return self.fid.tell()
        return -1

    def frewind(self):
        if self.fid is not None:
            self.fid.seek(0)

    def feof(self):
        if self.fid is not None:
            current = self.fid.tell()
            self.fid.seek(0, 2)
            end = self.fid.tell()
            self.fid.seek(current)
            return current >= end
        return -1

    def fwrite(self, data, precision='char', skip=0, machineformat=None):
        if self.fid is None: return 0

        # Mapping precision to struct format
        # This is simplified.
        fmt = self._get_struct_fmt(precision, machineformat)

        # skip is not standard in python write, usually implies write, skip, write.
        # MATLAB fwrite with skip inserts skip bytes.
        # For now, implementing without skip or assuming 0.

        try:
            # Flatten data
            d = np.array(data).flatten()
            b = struct.pack(f'{len(d)}{fmt}', *d)
            self.fid.write(b)
            return len(d)
        except Exception:
            return 0

    def fread(self, count, precision='char', skip=0, machineformat=None):
        if self.fid is None: return [], 0

        fmt = self._get_struct_fmt(precision, machineformat)
        size = struct.calcsize(fmt)

        res = []
        c = 0

        # If count is inf, read all
        if count == float('inf'):
            # Read all
            b = self.fid.read()
            num = len(b) // size
            if num > 0:
                res = struct.unpack(f'{num}{fmt}', b[:num*size])
                c = num
        else:
            b = self.fid.read(count * size)
            num = len(b) // size
            if num > 0:
                res = struct.unpack(f'{num}{fmt}', b[:num*size])
                c = num

        return list(res), c

    def _get_struct_fmt(self, precision, machineformat):
        # Map endian
        mf = machineformat if machineformat else self.machineformat
        end = '<' # Default little
        if mf == 'big-endian' or mf == 'b' or mf == 'ieee-be': end = '>'
        elif mf == 'little-endian' or mf == 'l' or mf == 'ieee-le': end = '<'
        elif mf == 'native' or mf == 'n': end = '@'

        # Map type
        p = precision.lower()
        t = 'c'
        if 'int8' in p: t = 'b'
        elif 'uint8' in p or 'uchar' in p or 'char' in p: t = 'B'
        elif 'int16' in p: t = 'h'
        elif 'uint16' in p: t = 'H'
        elif 'int32' in p: t = 'i'
        elif 'uint32' in p: t = 'I'
        elif 'int64' in p: t = 'q'
        elif 'uint64' in p: t = 'Q'
        elif 'float32' in p or 'single' in p: t = 'f'
        elif 'float64' in p or 'double' in p: t = 'd'

        return end + t


class dumbjsondb:
    """
    vlt.file.dumbjsondb - a simple JSON-based database.
    """
    def __init__(self, command='none', paramfilename='', **kwargs):
        self.paramfilename = ''
        self.dirname = '.dumbjsondb'
        self.unique_object_id_field = 'id'

        if command.lower() == 'new':
            self.paramfilename = paramfilename
            for k, v in kwargs.items():
                setattr(self, k, v)
            self.writeparameters()
        elif command.lower() == 'load':
            self.loadparameters(paramfilename)
        else: # none or just init
             for k, v in kwargs.items():
                setattr(self, k, v)

    def add(self, doc_object, **kwargs):
        overwrite = kwargs.get('Overwrite', 1)
        # doc_version handling from kwargs?

        doc_unique_id = self.docstats(doc_object)

        # Determine version
        latest_l, _ = self.latestdocversion(doc_unique_id)
        current_version = latest_l if latest_l is not None else -1

        doc_version = current_version # Default to latest

        p = self.documentpath()
        # Calculate new version if needed
        # Logic: if file exists and overwrite=2 (increment), new version.
        # If overwrite=1, overwrite current version.
        # If first time (current_version is None/-1), version 0.

        if current_version == -1:
             doc_version = 0
             fileexist = False
        else:
             fileexist = True # Assume if version exists, file exists

        can_we_write = 0
        if not fileexist:
            can_we_write = 1
        else:
            if overwrite == 1:
                can_we_write = 1
            elif overwrite == 0:
                raise Exception(f"Document {doc_unique_id} already exists.")
            elif overwrite == 2:
                doc_version = current_version + 1
                can_we_write = 1

        if can_we_write:
            self.writeobject(doc_object, doc_unique_id, doc_version)

        return self

    def read(self, doc_unique_id, doc_version=None):
        doc_unique_id = str(doc_unique_id)
        if doc_version is None:
            l, _ = self.latestdocversion(doc_unique_id)
            doc_version = l

        if doc_version is None:
            return None, None

        p = self.documentpath()
        f = self.uniqueid2filename(doc_unique_id, doc_version)
        fullpath = os.path.join(p, f)

        if isfile(fullpath):
            t = textfile2char(fullpath)
            try:
                document = json.loads(t)
                return document, doc_version
            except:
                return None, doc_version
        return None, None

    def openbinaryfile(self, doc_unique_id, doc_version=None):
        doc_unique_id = str(doc_unique_id)
        if doc_version is None:
            l, _ = self.latestdocversion(doc_unique_id)
            doc_version = l

        # Ensure document exists? MATLAB calls read to verify.

        f = self.uniqueid2binaryfilename(doc_unique_id, doc_version)
        p = self.documentpath()
        fullpath = os.path.join(p, f)

        lockfilename = fullpath + '-lock'
        fid, key = checkout_lock_file(lockfilename)

        if fid > 0:
            try:
                # Open binary file in append+read binary
                # 'a+' in python puts pointer at end. 'r+b' needs file to exist.
                # 'w+b' truncates.
                # We need to open without truncating, creating if not exists.
                # 'a+b' is standard.
                fobj = open(fullpath, 'a+b')
                # Seek to start? MATLAB code uses 'a+' then maybe seeks.
                # Actually MATLAB openbinaryfile uses 'a+'.
                return fobj, key, doc_version
            except:
                release_lock_file(lockfilename, key)
                return None, None, None
        else:
            return None, None, None

    def closebinaryfile(self, fid, key, doc_unique_id, doc_version=None):
        if fid is not None:
            fid.close()

        if doc_version is None:
             # Logic to find version if not passed?
             # For locking, we need the filename, which depends on version.
             # If caller didn't pass version, we might assume latest?
             l, _ = self.latestdocversion(doc_unique_id)
             doc_version = l

        f = self.uniqueid2binaryfilename(doc_unique_id, doc_version)
        p = self.documentpath()
        fullpath = os.path.join(p, f)
        lockfilename = fullpath + '-lock'

        release_lock_file(lockfilename, key)
        return None

    def search(self, scope, searchParams):
        # scope: {'version': 'latest'/'all'/number}
        # searchParams: dict or list

        scope_dict = {'version': 'latest'}
        if isinstance(scope, dict):
             scope_dict.update(scope)
        # Handle cell array input for scope?

        docs = []
        doc_versions = []

        docids = self.alldocids()

        for docid in docids:
            v_here = []
            if scope_dict['version'] == 'latest':
                l, _ = self.latestdocversion(docid)
                if l is not None: v_here = [l]
            elif scope_dict['version'] == 'all':
                _, v_here = self.latestdocversion(docid)
            else:
                v_here = [scope_dict['version']]

            for v in v_here:
                d, ver = self.read(docid, v)
                if d is not None:
                    # ismatch
                    if self.ismatch(d, searchParams):
                        docs.append(d)
                        doc_versions.append(ver)
        return docs, doc_versions

    def remove(self, doc_unique_id, version='all'):
        doc_unique_id = str(doc_unique_id)

        v_to_delete = []
        if str(version).lower() == 'all':
            _, v = self.latestdocversion(doc_unique_id)
            v_to_delete = v
        else:
            v_to_delete = [version]

        p = self.documentpath()
        for v in v_to_delete:
            vfname = self.uniqueid2filename(doc_unique_id, v)
            bfname = self.uniqueid2binaryfilename(doc_unique_id, v)

            if isfile(os.path.join(p, vfname)):
                os.remove(os.path.join(p, vfname))
            if isfile(os.path.join(p, bfname)):
                os.remove(os.path.join(p, bfname))

        # Update metadata
        op = 'Deleted all versions' if str(version).lower() == 'all' else 'Deleted version'
        self.updatedocmetadata(op, None, doc_unique_id, v_to_delete)

        return self

    def alldocids(self):
        p = self.documentpath()
        res = []
        if not isfolder(p): return res

        # Look for Object_id_*.txt
        # Filename: Object_id_{id}.txt
        # Need to parse {id} back.

        files = os.listdir(p)
        prefix = 'Object_id_'
        suffix = '.txt'

        for f in files:
            if f.startswith(prefix) and f.endswith(suffix):
                # Extract middle
                # Warning: encoded string might not be 1-to-1 if simple replacement
                # But here we just strip prefix/suffix
                s = f[len(prefix):-len(suffix)]
                # In MATLAB it does sscanf.
                # We should probably return s (the file string) or try to decode?
                # The ID in alldocids seems to be the clean ID?
                # But uniqueid2filenameprefix encodes it.
                # So we have the encoded ID.
                # Ideally we decode it, but string2filestring is lossy (replaces with _).
                # So we can't fully recover the original ID if it had special chars.
                # However, the metafile stores the ID? No, metafile name is based on ID.
                # If ID is just alphanumeric, it's fine.
                res.append(s)
        return res

    def docversions(self, doc_unique_id):
        # Helper for public call
        _, v = self.latestdocversion(doc_unique_id)
        return v

    def latestdocversion(self, doc_unique_id):
        # Return (latest, all_versions_list)
        p = self.documentpath()
        if not isfolder(p): return None, []

        # Filename: Object_id_{id}_v{hex}.json
        prefix = self.uniqueid2filenameprefix(doc_unique_id)
        # Prefix is Object_id_{encoded_id}

        # We look for files starting with prefix + '_v'
        search_prefix = prefix + '_v'

        files = os.listdir(p)
        versions = []

        for f in files:
            if f.startswith(search_prefix) and f.endswith('.json'):
                # Extract hex
                # f is prefix + '_v' + hex + '.json'
                # len(search_prefix)
                rest = f[len(search_prefix):-5] # remove .json
                try:
                    v = int(rest, 16)
                    versions.append(v)
                except:
                    pass

        if not versions:
            return None, []

        return max(versions), versions

    def docstats(self, document_obj):
        # Extract ID
        # document_obj is dict (if from json) or object
        id_val = None
        if isinstance(document_obj, dict):
            id_val = document_obj.get(self.unique_object_id_field)
        elif hasattr(document_obj, self.unique_object_id_field):
            id_val = getattr(document_obj, self.unique_object_id_field)

        if id_val is None:
            raise Exception(f"Document does not have field {self.unique_object_id_field}")

        return str(id_val)

    def writeobject(self, doc_object, doc_unique_id, doc_version):
        p = self.documentpath()
        if not isfolder(p):
            os.makedirs(p)

        docfile = self.uniqueid2filename(doc_unique_id, doc_version)

        # json encode
        # using vlt.data.jsonencodenan if available or standard json
        # vlt.data.jsonencodenan returns string.
        js = vlt.data.jsonencodenan(doc_object)
        str2text(os.path.join(p, docfile), js)

        # Update metadata
        self.updatedocmetadata('Added new version', doc_object, doc_unique_id, doc_version)

        # Create blank binary
        fb = self.uniqueid2binaryfilename(doc_unique_id, doc_version)
        touch(os.path.join(p, fb))

    def updatedocmetadata(self, operation, document, doc_unique_id, doc_version):
        p = self.documentpath()
        metafile = self.uniqueid2metafilename(doc_unique_id)
        fullpath = os.path.join(p, metafile)

        op = operation.lower()
        if op == 'added new version':
            str2text(fullpath, str(doc_version))
        elif op == 'deleted version':
            _, v = self.latestdocversion(doc_unique_id)
            if v:
                str2text(fullpath, str(max(v)))
            else:
                if isfile(fullpath): os.remove(fullpath)
        elif op == 'deleted all versions':
            if isfile(fullpath): os.remove(fullpath)

    def documentpath(self):
        if self.paramfilename:
            d = os.path.dirname(self.paramfilename)
            return os.path.join(d, self.dirname)
        else:
            return self.dirname

    def writeparameters(self):
        if not self.paramfilename: return

        d = os.path.dirname(self.paramfilename)
        if d and not os.path.exists(d):
            os.makedirs(d)

        # Write params
        params = {
            'dirname': self.dirname,
            'unique_object_id_field': self.unique_object_id_field
        }
        js = json.dumps(params)
        str2text(self.paramfilename, js)

        # Create db dir
        dbdir = os.path.join(d, self.dirname)
        if not os.path.exists(dbdir):
            os.makedirs(dbdir)

    def loadparameters(self, filename):
        if filename:
            self.paramfilename = filename

        if isfile(self.paramfilename):
            t = textfile2char(self.paramfilename)
            p = json.loads(t)
            for k, v in p.items():
                if k != 'paramfilename':
                    setattr(self, k, v)

    def uniqueid2filenameprefix(self, doc_unique_id):
        s = string2filestring(str(doc_unique_id))
        return 'Object_id_' + s

    def uniqueid2metafilename(self, doc_unique_id):
        return self.uniqueid2filenameprefix(doc_unique_id) + '.txt'

    def uniqueid2filename(self, doc_unique_id, version=0):
        # Hex 5 digits
        if version is None: version = 0
        h = f"{int(version):05X}"
        return self.uniqueid2filenameprefix(doc_unique_id) + '_v' + h + '.json'

    def uniqueid2binaryfilename(self, doc_unique_id, version=0):
        return self.uniqueid2filename(doc_unique_id, version) + '.binary'

    def ismatch(self, document, searchParams):
        # searchParams: dict or list of keys/values
        if isinstance(searchParams, dict):
            return vlt.data.fieldsearch(document, searchParams)

        # List: key, value, key, value...
        # Value can be string (regex) or exact

        # MATLAB: for i=1:2:numel
        # We assume searchParams is a dict in python for simplicity usually,
        # but if it's a list/tuple we handle it.
        # But here let's assume dict for Pythonic usage unless we want strict port.
        # If the user passes list:

        if isinstance(searchParams, (list, tuple)):
            for i in range(0, len(searchParams), 2):
                key = searchParams[i]
                val = searchParams[i+1]

                # Check if document has key
                doc_val = document.get(key)
                if doc_val is None: return False

                if isinstance(val, str):
                    # Regex
                    if not re.search(val, str(doc_val), re.IGNORECASE):
                        return False
                else:
                    # Exact
                    if doc_val != val: # Should use vlt.data.eqlen?
                        return False
            return True

        return True
