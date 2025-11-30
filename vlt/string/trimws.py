def trimws(mystring):
    """
    TRIMWS - Trim leading whitespace from a string

    newstr = vlt.string.trimws(str)

    Trims leading spaces from a string.

    This function is provided for backward compatibility.

    Example:
        m = trimws('   this string has leading whitespace')
        # m == 'this string has leading whitespace'
    """
    if not mystring:
        return ''

    return mystring.lstrip()
