import numpy as np

def hasAllFields(variable, fieldNames, fieldSizes=None):
    """
    Checks to see if VARIABLE has all of the fieldnames in the list FIELDNAMES
    and also checks to see if the values of those names match the dimensions
    given in the list FIELDSIZES. If you don't care to analyze one
    dimension, pass -1 for that dimension.

    Parameters
    ----------
    variable : dict
        The dictionary to check.
    fieldNames : list of str
        List of keys that should be present in variable.
    fieldSizes : list of lists or tuples, optional
        List of expected sizes for each field. Each element should be a list/tuple
        of length 2 [rows, cols]. Use -1 to ignore a dimension.

    Returns
    -------
    good : bool
        True if all fields are present and (optionally) have the correct size.
    errormsg : str
        Error message if good is False.
    """
    good = True
    errormsg = ''
    checkSizes = fieldSizes is not None
    notbad = True

    # Ensure fieldNames is iterable
    if isinstance(fieldNames, str):
        fieldNames = [fieldNames]

    for i, fieldName in enumerate(fieldNames):
        if good:
            notbad = True

        has_field = fieldName in variable
        good = good and has_field

        if notbad and not good:
            errormsg = f"'{fieldName}' not present."
            notbad = False

        if checkSizes and good:
            val = variable[fieldName]
            szg = fieldSizes[i]

            # Determine size of val (mimicking Matlab behavior roughly for 2D)
            sz_0 = 1
            sz_1 = 1

            if isinstance(val, np.ndarray):
                if val.ndim == 0:
                    sz_0, sz_1 = 1, 1
                elif val.ndim == 1:
                    # Treat 1D array as 1xN row vector
                    sz_0 = 1
                    sz_1 = val.shape[0]
                else:
                    sz_0 = val.shape[0]
                    sz_1 = val.shape[1]
            elif isinstance(val, (list, tuple)):
                 sz_0 = 1
                 sz_1 = len(val)
            elif isinstance(val, str):
                 sz_0 = 1
                 sz_1 = len(val)
            else: # scalar
                 sz_0 = 1
                 sz_1 = 1

            # Check dimensions
            if szg[0] > -1:
                 good = good and (szg[0] == sz_0)
            if szg[1] > -1:
                 good = good and (szg[1] == sz_1)

            if notbad and not good:
                eT1 = 'N' if szg[0] == -1 else str(szg[0])
                eT2 = 'N' if szg[1] == -1 else str(szg[1])
                errormsg = f"{fieldName} not of expected size (got {sz_0}x{sz_1} but expected {eT1}x{eT2})."
                notbad = False

    return good, errormsg
