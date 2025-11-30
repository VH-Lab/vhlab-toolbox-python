def islikevarname(name):
    """
    Checks to see if NAME is a like a valid Matlab variable name.

    Returns:
        b: bool
        errormsg: str
    """
    b = False

    # Pre-construct error message part for consistency with Matlab
    # But in Python if name is not printable, we handle it gracefully in f-string

    if not isinstance(name, str):
        errormsg = f"Error in {name}: must be a character string."
        return False, errormsg

    errormsg = f"Error in {name}: "

    if len(name) < 1:
        errormsg += "must be at least one character."
        return False, errormsg

    if not name[0].isalpha():
        errormsg += "must begin with a letter."
        return False, errormsg

    if any(c.isspace() for c in name):
        errormsg += "must have no whitespace."
        return False, errormsg

    b = True
    errormsg = ''
    return b, errormsg
