from typing import Tuple, List, Dict, Any, Optional
import os
import inspect
import importlib.util
from vlt.matlab.isclassfile import isclassfile
from vlt.matlab.mfile2package import mfile2package
from vlt.string.line_n import line_n
from vlt.file.text2cellstr import text2cellstr

def class2help(filename: str) -> Tuple[str, List[Dict[str, str]], List[Dict[str, str]], List[str]]:
    """
    Get help information from a Matlab class .m file.

    Args:
        filename: The full path to the .m file.

    Returns:
        A tuple containing:
        - classhelp: The help string.
        - prop_struct: A list of dicts with 'property' and 'doc'.
        - methods_struct: A list of dicts with 'method', 'description', and 'help'.
        - superclassnames: A list of superclass names.
    """

    if not isclassfile(filename):
        raise ValueError(f"{filename} does not appear to be a class file.")

    packagename = mfile2package(filename)
    lines = text2cellstr(filename)

    classhelp_lines = []

    found_classdef = False
    in_help_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("classdef"):
            found_classdef = True
            continue

        if found_classdef:
            if stripped.startswith("%"):
                in_help_block = True
                classhelp_lines.append(stripped[1:].strip()) # Remove % and space
            elif in_help_block:
                 # End of help block
                 break
            elif not stripped:
                 # Empty line before help block?
                 continue
            else:
                 # Code found, stop looking
                 break

    classhelp = "\n".join(classhelp_lines) + "\n"

    prop_struct = []
    current_props = []

    in_properties = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("properties"):
            in_properties = True
            continue
        if stripped.lower().startswith("end") and in_properties:
            in_properties = False
            continue

        if in_properties:
            if '%' in stripped:
                code_part = stripped.split('%')[0]
                comment_part = stripped.split('%', 1)[1]
            else:
                code_part = stripped
                comment_part = ""

            code_part = code_part.strip()
            if not code_part:
                continue

            parts = code_part.split()
            prop_name = parts[0]
            prop_name = prop_name.split('=')[0].strip()

            current_props.append(prop_name)
            doc = comment_part.strip()

            prop_struct.append({'property': prop_name, 'doc': doc})

    methods_struct = []

    # We need to track method blocks better.
    # `methods` block can appear multiple times.
    # Also `methods (Access=...)`

    in_methods = False

    for i, line in enumerate(lines):
         stripped = line.strip()

         # Check for methods block start
         if stripped.lower().startswith("methods"):
             in_methods = True
             continue

         # Check for end of methods block
         # But `end` also ends functions.
         # So we need to count nesting or just assume correct indentation or structure if we are parsing line by line?
         # MATLAB code is tricky.
         # `function ... end` is inside `methods ... end`.

         # If we are inside methods, and see `end`, it might be end of function or end of methods.
         # Usually functions inside classdef methods block have `end`.
         # But sometimes they don't if they are single file functions?
         # In classdef, they MUST have end if there are multiple?

         # Let's assume for this simple parser that we are looking for `function` keyword.
         # And we don't strictly enforce `in_methods` check because `function` keyword is distinctive enough inside a class file?
         # No, there might be local functions outside `methods` block (helper functions).
         # But those are not "methods" of the class usually, or private?

         # For now, let's just look for `function` and try to extract help.
         # And if we see `end` that reduces indent? No, indent is unreliable.

         if stripped.lower().startswith("function"):
             # Parse function signature
             sig = stripped[8:].strip()

             if "=" in sig:
                 sig = sig.split("=", 1)[1].strip()

             func_name = sig.split("(")[0].strip()

             # Extract help
             func_help_lines = []
             description = ""

             j = i + 1
             while j < len(lines):
                 next_line = lines[j].strip()
                 if next_line.startswith("%"):
                     func_help_lines.append(next_line[1:].strip())
                 elif not next_line:
                     if not func_help_lines: # Empty line before any help
                         j+=1
                         continue
                     else:
                         break # End of help
                 else:
                     break
                 j += 1

             if func_help_lines:
                 description = func_help_lines[0]
                 full_help = "\n".join(func_help_lines[1:])
             else:
                 full_help = ""

             methods_struct.append({
                 'method': func_name,
                 'description': description,
                 'help': full_help
             })

    superclassnames = []

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("classdef"):
            if "<" in stripped:
                parts = stripped.split("<")
                super_part = parts[1]
                supers = super_part.split("&")
                for s in supers:
                    s_name = s.strip().split()[0]
                    superclassnames.append(s_name)
            break

    return classhelp, prop_struct, methods_struct, superclassnames
