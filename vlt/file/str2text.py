import os

def str2text(filename: str, s: str):
    """
    Write a string to a text file.

    Args:
        filename: The path to the file.
        s: The string to write.

    Raises:
        IOError: If the file cannot be opened for writing.
    """

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(s)
    except IOError as e:
        # Re-raise with a custom message to match MATLAB behavior approximately
        raise IOError(f"Could not open {filename} for writing.") from e
