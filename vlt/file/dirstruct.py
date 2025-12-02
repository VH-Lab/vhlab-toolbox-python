import os
import shutil
import warnings
import numpy as np
import scipy.io
import h5py

# Dependencies imported directly to avoid circular imports
from .fixpath import fixpath
from .fixtilde import fixtilde
from .custom_struct_io import loadStructArray, saveStructArray
from . import checkout_lock_file, release_lock_file

def _load_mat_file(filepath):
    """
    Helper to load MAT files supporting both v5/v6/v7 (scipy) and v7.3 (h5py).
    Returns a dictionary of variables.
    """
    data = {}
    try:
        # Try scipy first (fastest for older formats)
        # struct_as_record=False, squeeze_me=True match MATLAB behavior better for access
        data = scipy.io.loadmat(filepath, struct_as_record=False, squeeze_me=True)
    except NotImplementedError:
        # Likely v7.3
        try:
            with h5py.File(filepath, 'r') as f:
                # We need to recursively convert h5py objects to numpy/python objects
                # This is a simplified loader. Full v7.3 support is complex.
                # For now we just load dataset values.
                def recurse_h5(obj):
                    if isinstance(obj, h5py.Dataset):
                        return obj[()]
                    elif isinstance(obj, h5py.Group):
                        d = {}
                        for k, v in obj.items():
                            d[k] = recurse_h5(v)
                        return d
                    return obj

                for k in f.keys():
                    data[k] = recurse_h5(f[k])
        except Exception as e:
             raise ValueError(f"Could not read {filepath} as v7.3 MAT file: {e}")
    except Exception as e:
        raise ValueError(f"Could not read {filepath}: {e}")

    return data

class dirstruct:
    """
    vlt.file.dirstruct - Manage experimental data organized in directories.

    This class is intended to manage experimental data. The data are organized
    into separate test directories, with each directory containing one epoch
    of recording. Each such directory has a file called 'reference.txt' that
    contains information about the signals that were acquired during that epoch.
    """

    def __init__(self, pathname=''):
        """
        DIRSTRUCT - Constructor for vlt.file.dirstruct

        OBJ = vlt.file.dirstruct(PATHNAME)

        Returns a DIRSTRUCT object.
        """
        self.pathname = ''
        self.nameref_str = [] # list of dicts
        self.dir_str = [] # list of dicts
        self.dir_list = [] # list of strings
        self.nameref_list = [] # list of dicts
        self.extractor_list = [] # list of dicts
        self.autoextractor_list = [] # list of dicts
        self.active_dir_list = [] # list of strings

        if pathname:
            self.pathname = fixpath(pathname)
            if not os.path.isdir(self.pathname):
                 raise ValueError(f"'{pathname}' does not exist.")

        if self.pathname:
            self.update()

    def update(self):
        """
        UPDATE - Examines the path and updates all structures

        OBJ = UPDATE(OBJ)
        """
        if not os.path.isdir(self.pathname):
            raise ValueError(f"'{self.pathname}' does not exist.")

        dse = len(self.dir_str)
        nse = len(self.nameref_str)

        # List directories
        try:
            d = sorted(os.listdir(self.pathname))
        except OSError:
            d = []

        for name in d:
            if name in ['.', '..'] or name.startswith('.'):
                continue

            full_path = os.path.join(self.pathname, name)
            if not os.path.isdir(full_path):
                continue

            fname = os.path.join(full_path, 'reference.txt')

            if os.path.isfile(fname) and name not in self.dir_list:
                # Add directory to list, add namerefs to other list
                try:
                    a = loadStructArray(fname)
                except Exception as e:
                    warnings.warn(f"Could not load {fname}: {e}")
                    a = []

                if a:
                    # a is a list of dicts
                    namerefs = a
                else:
                    namerefs = []

                self.dir_str.append({'dirname': name, 'listofnamerefs': namerefs})
                self.dir_list.append(name)
                self.active_dir_list.append(name)
                dse += 1

                for j in range(len(namerefs)):
                    ind = self._namerefind(self.nameref_str, namerefs[j]['name'], namerefs[j]['ref'])
                    if ind > -1: # append to existing record
                        self.nameref_str[ind]['listofdirs'].append(name)
                    else: # add new record
                        tmpstr = {
                            'name': namerefs[j]['name'],
                            'ref': namerefs[j]['ref'],
                            'type': namerefs[j].get('type', ''),
                            'listofdirs': [name]
                        }
                        self.nameref_str.append(tmpstr)

                        self.nameref_list.append({
                            'name': namerefs[j]['name'],
                            'ref': namerefs[j]['ref'],
                            'type': namerefs[j].get('type', '')
                        })

                        # also add new extractor record
                        ind2 = self._typefind(self.autoextractor_list, namerefs[j].get('type', ''))

                        extractor_entry = {
                            'name': namerefs[j]['name'],
                            'ref': namerefs[j]['ref'],
                            'type': namerefs[j].get('type', '')
                        }

                        if ind2 > -1:
                            extractor_entry['extractor1'] = self.autoextractor_list[ind2]['extractor1']
                            extractor_entry['extractor2'] = self.autoextractor_list[ind2]['extractor2']
                        else:
                            extractor_entry['extractor1'] = ''
                            extractor_entry['extractor2'] = ''

                        self.extractor_list.append(extractor_entry)
                        nse += 1
        return self

    def getactive(self):
        """
        GETACTIVE - Returns a cell list of the active directories
        """
        return self.active_dir_list

    def getallnamerefs(self):
        """
        GETALLNAMEREFS - Returns a structure with all name/ref pairs
        """
        return self.nameref_list

    def getalltests(self):
        """
        GETALLTESTS - Returns a list of all test directories
        """
        return self.dir_list

    def getcells(self, nameref=None, inds=None):
        """
        GETCELLS - Returns cells from the experiment
        """
        C = []
        e, _ = self.getexperimentfile()

        if not os.path.isfile(e):
            return C

        keys = []

        # Try to read keys without loading full file
        try:
            vars_info = scipy.io.whosmat(e)
            keys = [info[0] for info in vars_info]
        except NotImplementedError:
            # v7.3, must open file to list keys
            try:
                with h5py.File(e, 'r') as f:
                    keys = list(f.keys())
            except:
                return C
        except:
             return C

        if nameref is None:
            # Load all keys starting with 'cell'
            for k in keys:
                if k.startswith('cell'):
                    C.append(k)
        else:
            prefix = f"cell_{nameref['name']}_{nameref['ref']:04d}"
            if inds is None:
                    for k in keys:
                        if k.startswith(prefix):
                            C.append(k)
            else:
                for k in keys:
                        if k.startswith(prefix):
                            # Extract index
                            try:
                                full_prefix = prefix + '_'
                                if k.startswith(full_prefix):
                                    idx_str = k[len(full_prefix):len(full_prefix)+3]
                                    idx = int(idx_str)
                                    if idx in inds:
                                        C.append(k)
                            except:
                                pass

        return C

    def getexperimentfile(self, createit=False):
        """
        GETEXPERIMENTFILE - Returns the experiment data filename
        """
        expf = ''
        p = ''

        if not os.path.isdir(self.pathname):
            return p, expf

        # Determine expf from pathname
        path_stripped = self.pathname.rstrip(os.sep)
        head, tail = os.path.split(path_stripped)

        if not tail: # if pathname was just / or C:\
             expf = head # fallback
        else:
             expf = tail

        analysis_dir = os.path.join(self.pathname, 'analysis')
        analysis_dir = fixpath(analysis_dir)
        p = os.path.join(analysis_dir, 'experiment.mat')

        if createit:
            if not os.path.isfile(p):
                if not os.path.isdir(analysis_dir):
                    try:
                        os.makedirs(analysis_dir)
                    except OSError:
                        pass

                name = expf
                # Save name to p
                try:
                    scipy.io.savemat(p, {'name': name})
                except ImportError:
                    pass

        return p, expf

    def getextractors(self, name, ref):
        """
        GETEXTRACTORS - Get extractor info
        """
        ind = self._namerefind(self.extractor_list, name, ref)
        if ind > -1:
            return self.extractor_list[ind]['extractor1'], self.extractor_list[ind]['extractor2']
        else:
            raise ValueError('Could not find name/ref')

    def getnamerefs(self, testdir):
        """
        GETNAMEREFS - Return namerefs from a given test directory
        """
        try:
            loc = self.dir_list.index(testdir)
            return self.dir_str[loc]['listofnamerefs']
        except ValueError:
            return []

    def getpathname(self):
        """
        GETPATHNAME - Returns the pathname
        """
        return fixpath(fixtilde(self.pathname))

    def getscratchdirectory(self, createit=False):
        """
        GETSCRATCHDIRECTORY - Returns the scratch directory path
        """
        p = ''
        if not os.path.isdir(self.pathname):
            return p

        analysis_dir = os.path.join(self.pathname, 'analysis')
        p = os.path.join(analysis_dir, 'scratch')
        p = fixpath(p) # Ensure trailing slash

        if createit:
            if not os.path.isdir(p):
                try:
                    os.makedirs(p)
                except OSError:
                    pass
        return p

    def getstimscript(self, thedir):
        """
        GETSTIMSCRIPT - Gets the stimscript and MTI
        """
        saveScript = None
        MTI = None

        p = self.getpathname()
        dirpath = os.path.join(p, thedir)

        if not os.path.isdir(dirpath):
            raise ValueError(f"Directory {dirpath} does not exist.")

        stimsfile = os.path.join(dirpath, 'stims.mat')
        if not os.path.isfile(stimsfile):
            raise ValueError(f"No stims in directory {dirpath}.")

        try:
            g = _load_mat_file(stimsfile)
            # Accessing fields from dict
            if 'saveScript' in g:
                saveScript = g['saveScript']
            if 'MTI2' in g:
                MTI = g['MTI2']
        except Exception:
            pass

        return saveScript, MTI

    def getstimscripttimestruct(self, thedir):
        """
        GETSTIMSCRIPTTIMESTRUCT - Gets stimscript as stimscripttimestruct
        """
        ss, mti = self.getstimscript(thedir)
        # return stimscripttimestruct(ss, mti)
        raise NotImplementedError("stimscripttimestruct not yet implemented")

    def gettag(self, dir_name):
        """
        GETTAG - Get tag(s) from a directory
        """
        wholedir = os.path.join(self.getpathname(), dir_name)
        tagfilename = os.path.join(wholedir, 'tags.txt')

        if os.path.isfile(tagfilename):
             return loadStructArray(tagfilename)
        else:
             return []

    def gettagvalue(self, dir_name, name):
        """
        GETTAGVALUE - Get a value of a named tag
        """
        v = None
        tags = self.gettag(dir_name)

        for tag in tags:
            if tag.get('tagname') == name:
                return tag.get('value')
        return v

    def gettests(self, name, ref):
        """
        GETTESTS - Returns the list of directories for name/ref
        """
        g = self._namerefind(self.nameref_str, name, ref)
        if g > -1:
            return self.nameref_str[g]['listofdirs']
        else:
            return []

    def hastag(self, dir_name, tagname):
        """
        HASTAG - Returns TRUE if a given tagname is present
        """
        tags = self.gettag(dir_name)
        for tag in tags:
            if tag.get('tagname') == tagname:
                return True
        return False

    def isactive(self, dirname):
        """
        ISACTIVE - Returns True if dirname is an active directory
        """
        if isinstance(dirname, str):
            return dirname in self.active_dir_list
        else:
            # List of dirs
            return [d in self.active_dir_list for d in dirname]

    def neuter(self, dir_or_list):
        """
        NEUTER - Disable directory without removing data
        """
        if isinstance(dir_or_list, str):
            dir_or_list = [dir_or_list]

        for d in dir_or_list:
            dirpathhere = os.path.join(self.getpathname(), d)
            if not os.path.isdir(dirpathhere):
                raise ValueError(f"No such directory {dirpathhere}.")

            reference_txt = os.path.join(dirpathhere, 'reference.txt')
            reference0_txt = os.path.join(dirpathhere, 'reference0.txt')

            if not os.path.isfile(reference_txt):
                raise ValueError(f"No such file {reference_txt}.")

            shutil.move(reference_txt, reference0_txt)

        # Re-initialize
        self.__init__(self.getpathname())
        return self

    def newtestdir(self):
        """
        NEWTESTDIR - Returns a suitable new test directory name
        """
        p = self.getpathname()
        i = 1
        while True:
            d = f"t{i:05d}"
            if not os.path.isdir(os.path.join(p, d)):
                return d
            i += 1

    def addtag(self, dir_name, tagname, value):
        """
        ADDTAG - Add a tag to a dirstruct directory
        """
        wholedir = os.path.join(self.getpathname(), dir_name)
        tagfilename = os.path.join(wholedir, 'tags.txt')
        taglockfilename = os.path.join(wholedir, 'tags-lock.txt')

        newtag = {'tagname': tagname, 'value': value}

        # Check if valid identifier
        if not tagname.isidentifier():
             raise ValueError(f"Cannot add tag with requested tagname {tagname} to directory {wholedir}; the tag name is not a valid variable name.")

        fid, key = checkout_lock_file(taglockfilename, 30, True)
        if fid > 0:
            try:
                tags = self.gettag(dir_name)
                found = False
                for tag in tags:
                    if tag.get('tagname') == tagname:
                        tag['value'] = value
                        found = True
                        break
                if not found:
                    tags.append(newtag)

                saveStructArray(tagfilename, tags)
            except Exception as e:
                release_lock_file(taglockfilename, key)
                raise e

            release_lock_file(taglockfilename, key)

    def removetag(self, dir_name, tagname):
        """
        REMOVETAG - Remove a tag from a dirstruct directory
        """
        wholedir = os.path.join(self.getpathname(), dir_name)
        tagfilename = os.path.join(wholedir, 'tags.txt')
        taglockfilename = os.path.join(wholedir, 'tags-lock.txt')

        fid, key = checkout_lock_file(taglockfilename, 30, True)
        if fid > 0:
            try:
                tags = self.gettag(dir_name)
                new_tags = [tag for tag in tags if tag.get('tagname') != tagname]

                if not new_tags:
                    if os.path.isfile(tagfilename):
                        os.remove(tagfilename)
                else:
                    saveStructArray(tagfilename, new_tags)
            except Exception as e:
                release_lock_file(taglockfilename, key)
                raise e

            release_lock_file(taglockfilename, key)

    def saveexpvar(self, vrbl_sev, name_sev, pres=False):
        """
        SAVEEXPVAR - Saves an experiment variable
        """
        preserved_sev = pres

        if isinstance(name_sev, str):
            vrbl_sev = [vrbl_sev]
            name_sev = [name_sev]

        fn_sev, _ = self.getexperimentfile(True)
        fnlock_sev = fn_sev + '-lock'

        fid, key = checkout_lock_file(fnlock_sev, 30, True)

        if fid > 0:
            try:
                data = {}
                # Safely load existing data
                if os.path.isfile(fn_sev):
                    try:
                        data = _load_mat_file(fn_sev)
                        # Ensure data is a dict (it should be from _load_mat_file)
                        if not isinstance(data, dict):
                            data = {}
                    except Exception as e:
                        # If we can't read it, we shouldn't just overwrite it blindly if it has content?
                        # But MATLAB often overwrites or errors.
                        # Ideally we throw an error if file exists but is unreadable to prevent data loss.
                        # Unless it's empty.
                        if os.path.getsize(fn_sev) > 0:
                            raise ValueError(f"File {fn_sev} exists and is not empty, but could not be read. Aborting saveexpvar to prevent data loss. Error: {e}")
                        data = {}

                for i in range(len(name_sev)):
                    # In python we just update the dict
                    data[name_sev[i]] = vrbl_sev[i]

                # Filter out internal keys before saving?
                # scipy.io.savemat handles it.
                # However, if we loaded from h5py, we might have clean data.
                # Warning: saving back using scipy.io.savemat will save as v5 (limit 2GB).
                # If original was v7.3 because it was huge, this might fail or truncate?
                # For now, we use scipy.io.savemat as primary writer.
                # If we need v7.3 writing, we need a different approach.
                # Given strict instruction to just "import whatever libraries are needed" for *reading*,
                # and this is a port, usually standard savemat is sufficient unless large data.

                scipy.io.savemat(fn_sev, data)

            except Exception as e:
                release_lock_file(fnlock_sev, key)
                raise e

            release_lock_file(fnlock_sev, key)

    def deleteexpvar(self, variablenametobedeleted, additionalvariables=None, additionalvariablenames=None, preserveassociates=False):
        """
        DELETEEXPVAR - Delete a variable from the experiment.mat file
        """
        if not variablenametobedeleted and additionalvariables is None:
            return

        if isinstance(variablenametobedeleted, str):
            variablenametobedeleted = [variablenametobedeleted]

        fn_sev, _ = self.getexperimentfile()

        if os.path.isfile(fn_sev):
            fnlock_sev = fn_sev + '-lock'
            fid, key = checkout_lock_file(fnlock_sev, 30, True)

            if fid > 0:
                try:
                    try:
                        data = _load_mat_file(fn_sev)
                    except Exception as e:
                         if os.path.getsize(fn_sev) > 0:
                             raise ValueError(f"File {fn_sev} exists and is not empty, but could not be read. Aborting deleteexpvar. Error: {e}")
                         data = {}

                    # Delete variables
                    if variablenametobedeleted:
                        for v in variablenametobedeleted:
                            if v in data:
                                del data[v]

                    # Add additional variables
                    if additionalvariables is not None and additionalvariablenames is not None:
                         for i in range(len(additionalvariablenames)):
                             data[additionalvariablenames[i]] = additionalvariables[i]

                    # Filter out internal keys before checking if empty?
                    user_keys = [k for k in data.keys() if not k.startswith('__')]

                    if user_keys:
                        scipy.io.savemat(fn_sev, data)
                    else:
                        os.remove(fn_sev)

                except Exception as e:
                    release_lock_file(fnlock_sev, key)
                    raise e

                release_lock_file(fnlock_sev, key)
        else:
            if additionalvariables is not None:
                 self.saveexpvar(additionalvariables, additionalvariablenames, preserveassociates)

    def setactive(self, adirlist, append=False):
        """
        SETACTIVE - Sets the active directories
        """
        if isinstance(adirlist, str):
            thedirlist = [adirlist]
        else:
            thedirlist = adirlist

        # Intersect with dir_list
        active_list = [d for d in thedirlist if d in self.dir_list]

        if append:
            # Union
            self.active_dir_list = list(set(self.active_dir_list) | set(active_list))
            self.active_dir_list.sort()
        else:
            self.active_dir_list = active_list

        return self

    def __str__(self):
        return f"dirstruct object; manages directory {self.getpathname()}"

    def __repr__(self):
        return self.__str__()

    # Private methods
    def _namerefind(self, nameref_str, name, ref):
        """
        NAMEREFIND - returns -1 if not there, or the index of the nameref pair
        """
        for i, item in enumerate(nameref_str):
            if item['name'] == name and item['ref'] == ref:
                return i
        return -1

    def _typefind(self, autoextractlist, type_str):
        """
        TYPEFIND - returns -1 if not there, or the index of the nameref pair
        """
        for i, item in enumerate(autoextractlist):
            if item.get('type') == type_str:
                return i
        return -1
