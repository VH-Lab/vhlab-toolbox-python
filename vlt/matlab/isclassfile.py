def isclassfile(filename: str) -> bool:
    """
    Is a Matlab .m file a class definition?

    Args:
        filename: The full path to the .m file.

    Returns:
        True if the file is a Matlab class definition file, False otherwise.

    Note:
        This implementation checks for 'classdef' keyword at the start of the file or after comments.
        It is a simple parser and might not cover all edge cases handled by MATLAB's mtree.
    """

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('%'):
                    continue
                if line.lower().startswith('classdef'):
                    return True
                # If we encounter code that is not a comment and not classdef, it's likely not a class file
                # (function files usually start with 'function')
                return False
    except IOError:
        return False

    return False
