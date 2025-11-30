from typing import List
import os

def text2cellstr(filename: str) -> List[str]:
    """
    Read a cell array of strings from a text file.

    Args:
        filename: The path to the text file.

    Returns:
        A list of strings, where each string is a line from the file.

    Raises:
        IOError: If the file cannot be opened.
    """

    c = []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # fgetl reads a line, removing the newline character.
                # Python's iteration keeps the newline.
                # We should strip the trailing newline.

                # fgetl behavior:
                # "Line 1\n" -> "Line 1"
                # "Line 2" (eof) -> "Line 2"

                # Python readline includes \n.

                # We can use splitlines() on the content, but let's do line by line to support large files conceptually.

                if line.endswith('\n'):
                    line = line[:-1]
                # Also handle \r\n
                if line.endswith('\r'):
                    line = line[:-1]

                c.append(line)
    except IOError as e:
        raise IOError(f"Could not open file {filename} for reading.") from e

    return c
