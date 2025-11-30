import os

def absolute2relative(absolutepath1: str, absolutepath2: str, **kwargs) -> str:
    """
    Determine the relative path between two filenames, given two absolute names.

    Given two absolute paths, this function returns the relative path of path1 with respect to path2.

    Args:
        absolutepath1: The target absolute path.
        absolutepath2: The reference absolute path.
        **kwargs:
            input_filesep (str): Input file separator (default: '/')
            output_filesep (str): Output file separator (default: '/')
            backdir_symbol (str): Symbol for moving back one directory (default: '..')

    Returns:
        The relative path.
    """

    input_filesep = kwargs.get('input_filesep', '/')
    output_filesep = kwargs.get('output_filesep', '/')
    backdir_symbol = kwargs.get('backdir_symbol', '..')

    # Python's os.path.relpath does exactly this, but uses system separators.
    # The MATLAB implementation seems to do string manipulation based on provided separators.
    # To be faithful to the MATLAB implementation, we should follow its logic, especially regarding separators.

    # Also, note that MATLAB implementation assumes the input paths are using `input_filesep`.

    c1 = absolutepath1.split(input_filesep)
    c2 = absolutepath2.split(input_filesep)

    # Find common depth
    d = 0
    # The MATLAB loop: while strcmp(c1{d},c2{d}) & d<numel(c1) & d<numel(c2) (1-based index)
    # Python 0-based.

    # Also note MATLAB strsplit might return empty strings at start if path starts with separator.
    # e.g. '/a/b'.split('/') -> ['', 'a', 'b']

    min_len = min(len(c1), len(c2))
    while d < min_len and c1[d] == c2[d]:
        d += 1

    # depth in MATLAB was d-1 (because d was incremented past the match)
    # In Python, d matches the number of common elements if we stop when they differ.

    # Wait, let's trace:
    # c1 = ['', 'a', 'b']
    # c2 = ['', 'a', 'c']
    # d=0: '' == '' -> d=1
    # d=1: 'a' == 'a' -> d=2
    # d=2: 'b' != 'c' -> stop.
    # d=2.
    # Common parts are index 0 and 1.
    # depth = 2.

    depth = d

    # c2_depth = numel(c2) - 1;
    # If c2 is a file path '/Users/me/mydir3/myfile2.m', split is ['', 'Users', 'me', 'mydir3', 'myfile2.m'] (len 5)
    # c2_depth in MATLAB logic refers to the depth of the directory containing the file,
    # but let's see how it is used.
    # r = [ repmat([backdir_symbol output_filesep],1,c2_depth-depth) strjoin(c1(depth+1:end),output_filesep) ];

    # If we are at /a/c (depth 2), and want to go to /a/b
    # We need to go back from c's directory.
    # Wait, c2 is a file path?
    # Example:
    # p1 = '/Users/me/mydir1/mydir2/myfile1.m'
    # p2 = '/Users/me/mydir3/myfile2.m'
    # c1 = ['', 'Users', 'me', 'mydir1', 'mydir2', 'myfile1.m']
    # c2 = ['', 'Users', 'me', 'mydir3', 'myfile2.m']
    # common: '', 'Users', 'me' -> depth = 3.
    # c2 len = 5. c2_depth = 5 - 1 = 4.
    # diff = 4 - 3 = 1.
    # 1 '..'
    # Result: '../' + joined c1 from index 3 onwards ('mydir1', 'mydir2', 'myfile1.m')
    # '../mydir1/mydir2/myfile1.m'

    # NOTE: The MATLAB code `c2_depth = numel(c2) - 1` implies that c2 is treated as a file,
    # and we calculate relativity from its parent directory.

    c2_depth = len(c2) - 1

    back_steps = c2_depth - depth

    backs = (backdir_symbol + output_filesep) * back_steps

    # strjoin(c1(depth+1:end)) -> Python c1[depth:]

    forward_part = output_filesep.join(c1[depth:])

    return backs + forward_part
