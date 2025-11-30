import os

def isfile(filename: str) -> bool:
    """
    Searches for a file with name filename within the existing path.

    Args:
        filename: The path to the file.

    Returns:
        True if filename is a file, False otherwise.
    """
    return os.path.isfile(filename)
