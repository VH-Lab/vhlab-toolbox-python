import scipy.io
import h5py
import numpy as np
import fnmatch
import os

def load2celllist(filename, *args):
    """
    vlt.file.load2celllist - Loads saved objects to a list (cell list in MATLAB)

    objs, objnames = vlt.file.load2celllist(filename, *args)

    Loads objects from a file (MATLAB format expected) into a list.
    Additional arguments are passed on to the loading mechanism or used to filter variables.

    objs is a list of all variables matching the loading criteria.
    objnames is a list of the names of these variables.

    Example:
        myobjs, mynames = vlt.file.load2celllist('myfile.mat', 'cell*', '-mat')
        # If 'myfile.mat' contains 'cell1' and 'cell2':
        # mynames = ['cell1', 'cell2']
        # myobjs = [data_of_cell1, data_of_cell2]
    """

    # Collect variable names/patterns
    patterns = []

    # MATLAB load arguments can be mixed.
    for arg in args:
        if isinstance(arg, str):
            if arg.startswith('-'):
                pass # Ignore flags for now
            else:
                patterns.append(arg)
        else:
             pass

    data = {}

    # Check if filename needs extension
    if not os.path.exists(filename):
        if os.path.exists(filename + '.mat'):
            filename = filename + '.mat'
        # Else assume it might be created or handled by load mechanisms (though for read it must exist)

    # Try loading
    try:
        # scipy.io.loadmat
        mat_data = scipy.io.loadmat(filename, appendmat=True)

        # Filter out internal keys
        for k, v in mat_data.items():
            if not k.startswith('__'):
                data[k] = v

    except NotImplementedError:
        # Might be v7.3
        try:
             with h5py.File(filename, 'r') as f:
                 for k in f.keys():
                     val = f[k][()]
                     # Transpose logic for v7.3 compatibility
                     # MATLAB saves [Rows, Cols]. HDF5 sees [Cols, Rows] (or vice versa depending on view).
                     # Usually we transpose arrays.
                     if isinstance(val, np.ndarray):
                         val = val.T
                     data[k] = val
        except Exception as e:
            raise Exception(f"Could not load file {filename} (assumed v7.3 after loadmat failed): {e}")
    except Exception as e:
         # Try with h5py just in case it was a different error but actually v7.3?
         try:
             with h5py.File(filename, 'r') as f:
                 for k in f.keys():
                     val = f[k][()]
                     if isinstance(val, np.ndarray):
                         val = val.T
                     data[k] = val
         except:
             # Raise original error
             raise Exception(f"Could not load file {filename}: {e}")

    # Now filter data based on patterns
    if not patterns:
        # Return all
        final_keys = sorted(data.keys())
    else:
        final_keys = []
        all_keys = sorted(data.keys())
        for k in all_keys:
            # Check if k matches ANY pattern
            match = False
            for p in patterns:
                if fnmatch.fnmatch(k, p):
                    match = True
                    break
            if match:
                final_keys.append(k)

    objs = [data[k] for k in final_keys]
    objnames = final_keys

    return objs, objnames
