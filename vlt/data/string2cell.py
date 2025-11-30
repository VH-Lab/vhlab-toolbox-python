
def string2cell(s, separator, **kwargs):
    """
    STRING2CELL - Convert a delimited list to a list of strings

    C = vlt.data.string2cell(S, SEPARATOR)

    Converts a separator-delimited string list to a list of strings.

    S should be a separator-delimited list, such as 't00001, t00002, t00003'.

    SEPARATOR is the character that separates the items, such as ',' or ';'.

    Additional parameters can be provided as keyword arguments:
    vlt.data.string2cell(S, SEPARATOR, NAME=VALUE)

    Parameter name:           | Description:
    --------------------------|-----------------------------------------
    trimws (True/False, default True)   | Should we trim whitespace for these elements?

    """
    trimws = kwargs.get('trimws', True)

    parts = s.split(separator)

    if trimws:
        parts = [p.strip() for p in parts]

    return parts
