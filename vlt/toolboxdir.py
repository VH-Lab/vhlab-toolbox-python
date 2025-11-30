import os
import vlt

def toolboxdir():
    """
    TOOLBOXDIR Returns the root directory of the vlt toolbox

    folderPath = vlt.toolboxdir()

    Returns the absolute path to the root directory of the vlt toolbox.
    This function is useful for locating resources within the toolbox
    structure regardless of the current working directory.

    Outputs:
      folderPath - A string containing the absolute path to the root
                   directory of the vlt toolbox
    """
    # Assuming vlt package is installed/imported
    # vlt/__init__.py is in vlt/
    # toolboxdir is vlt/
    # But usually toolboxdir refers to the repo root?
    # MATLAB: fileparts(fileparts(mfilename('fullpath')))
    # mfilename('fullpath') is .../vlt/toolboxdir.m
    # fileparts -> .../vlt
    # fileparts -> .../ (parent of vlt)
    # But wait. toolboxdir.m is in +vlt/toolboxdir.m (package function)
    # The file vlt/toolboxdir.m is inside +vlt folder?
    # Check original file path: vlt/toolboxdir.m
    # If it is in `+vlt/toolboxdir.m`, then `fileparts` gives `.../+vlt`.
    # `fileparts` again gives `.../`.
    # So it returns the directory CONTAINING the +vlt package.

    # In Python, vlt is a package.
    # vlt module file is vlt/__init__.py
    # We want the directory containing vlt?
    # Or the vlt directory itself?

    # If MATLAB returns parent of +vlt, that is the "toolbox root".

    # Python: vlt.__file__ is .../vlt/__init__.py
    # dirname -> .../vlt
    # dirname -> .../

    # If installed as `vlt`, then `.../vlt` is the package dir.
    # The parent is where it is installed.

    path = os.path.dirname(os.path.dirname(os.path.abspath(vlt.__file__)))
    return path
