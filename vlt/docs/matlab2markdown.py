from typing import List, Dict, Any, Optional, Union
import os
import glob
from vlt.data.emptystruct import emptystruct
from vlt.file.dirlist_trimdots import dirlist_trimdots
from vlt.matlab.mfile2package import mfile2package
from vlt.matlab.isclassfile import isclassfile
from vlt.docs.class2help import class2help
from vlt.path.absolute2relative import absolute2relative
from vlt.file.str2text import str2text
from vlt.docs.markdownoutput2objectstruct import markdownoutput2objectstruct
from vlt.file.text2cellstr import text2cellstr

def matlab2markdown(input_path: str, output_path: str, ymlpath: str, objectstruct: Optional[List[Dict[str, Any]]] = None, packageprefix: str = '', url_prefix: str = 'https://vh-lab.github.io/NDI-matlab/') -> List[Dict[str, Any]]:
    """
    Recursively converts Matlab documentation to Markdown format (.md) starting from an INPUT_PATH.

    Args:
        input_path: Path to the input directory.
        output_path: Path to the output directory.
        ymlpath: Path for the yml structure.
        objectstruct: Optional list of dicts with 'object' and 'path'.
        packageprefix: Prefix for the package.
        url_prefix: URL prefix for links.

    Returns:
        A list of dictionaries representing the structure of the generated markdown.
    """

    out = [] # List of dicts

    # Skip private, internal and +internal folders
    folder_name = os.path.basename(os.path.normpath(input_path))
    if folder_name in ['private', 'internal', '+internal']:
        return []

    print(f"crawling {input_path} ... ")

    if objectstruct is None:
        objectstruct = []

    # check .matlab2markdown-ignore
    if os.path.exists(os.path.join(input_path, '.matlab2markdown-ignore')):
        return []

    # w = what(input_path) in MATLAB returns struct with m, classes, packages.
    # We need to simulate this.

    m_files = []
    classes = []
    packages = []

    if not os.path.isdir(input_path):
        # If input_path is not a dir, we can't crawl it.
        return []

    # List all files and dirs
    entries = os.listdir(input_path)
    entries.sort()

    for entry in entries:
        full_entry_path = os.path.join(input_path, entry)
        if os.path.isfile(full_entry_path) and entry.endswith('.m'):
            if isclassfile(full_entry_path):
                 # In MATLAB `what` returns classes separate from m files?
                 # Actually `w.m` contains functions, `w.classes` contains classes.
                 # But `isclassfile` check is done in loop over `w.m` in the original code?
                 # Original: for i=1:numel(w.m) ... isclass = ...
                 # So w.m includes classes too? Or maybe just functions?

                 # The code iterates over `w.m`.
                 # Then check `isclass = vlt.matlab.isclassfile(...)`.
                 # So `w.m` likely contains ALL .m files.
                 m_files.append(entry)
            else:
                 m_files.append(entry)

        elif os.path.isdir(full_entry_path):
            if entry.startswith('+'):
                packages.append(entry[1:]) # remove +
            else:
                # Normal directory, will be handled later
                pass

    # Create output dir
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Process .m files
    for m_file in m_files:
        full_m_path = os.path.join(input_path, m_file)

        # Get help (we need a way to get help text)
        # Using class2help logic?
        # class2help is specifically for classes.
        # For functions, we need to extract help similarly.
        # We can reuse the logic we implemented in class2help (partial) or just read comments.

        # Let's read the file content
        lines = text2cellstr(full_m_path)

        # Extract help for function
        # Typically first block of comments.
        help_text = ""
        help_lines = []
        in_help = False
        found_code = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_help:
                     # Allow empty lines in help
                     help_lines.append("")
                continue
            if stripped.startswith("%"):
                in_help = True
                help_lines.append(stripped[1:].strip())
            else:
                if in_help:
                    break # End of help
                if not in_help:
                    # Maybe function definition first?
                    if stripped.lower().startswith("function") or stripped.lower().startswith("classdef"):
                        continue
                    # Code found before help? Usually help is before or after first line.
                    found_code = True

        help_text = "\n".join(help_lines)

        is_class = isclassfile(full_m_path)
        if is_class:
            classstr = 'CLASS '
        else:
            classstr = ''

        pkg_name = mfile2package(full_m_path)
        doctext = f"# {classstr}{pkg_name}\n\n"

        if not is_class:
            h = f"```\n{help_text}\n```\n"
            doctext += h

        out_here = {}
        out_here['title'] = pkg_name
        out_here['path'] = os.path.join(ymlpath, m_file + '.md') # .m.md ? No, MATLAB code adds .md to filename
        # [ymlpath filesep w.m{i} '.md'] -> filename.m.md
        out_here['url_prefix'] = url_prefix

        if is_class:
            try:
                classhelp, prop_struct, methods_struct, superclassnames = class2help(full_m_path)
            except Exception as e:
                print(f"Error parsing class {full_m_path}: {e}")
                classhelp, prop_struct, methods_struct, superclassnames = ("", [], [], [])

            # The test expects CLASS MyClass, not just # MyClass
            # Oh wait, I already added classstr above.

            classhelp_block = f"```\n{classhelp}\n```\n"
            doctext += classhelp_block

            doctext += "## Superclasses\n"
            if not superclassnames:
                doctext += "*none*"

            for j, superclass in enumerate(superclassnames):
                # Link logic
                index = -1
                for k, obj in enumerate(objectstruct):
                    if obj.get('object') == superclass:
                        index = k
                        break

                linkhere = ""
                linkopen = ""
                linkclose = ""

                if index != -1:
                    linkopen = "["
                    linkclose = "]"
                    if url_prefix == objectstruct[index].get('url_prefix'):
                        # absolute2relative
                         # objectstruct path vs out_here path
                         rel = absolute2relative(objectstruct[index]['path'], out_here['path'])
                         linkhere = f"({rel})"
                    else:
                        objhere = objectstruct[index]['path'].replace('+', '%2B')
                        if objhere.endswith('.md'):
                            objhere = objhere[:-3]
                        linkhere = f"({objectstruct[index]['url_prefix']}{objhere})"

                doctext += f"**{linkopen}{superclass}{linkclose}{linkhere}**"
                if j != len(superclassnames) - 1:
                    doctext += ", "

            doctext += "\n\n## Properties\n\n"

            if not prop_struct:
                doctext += "*none*\n"
            else:
                doctext += "| Property | Description |\n"
                doctext += "| --- | --- |\n"
                for prop in prop_struct:
                    doctext += f"| *{prop['property']}* | {prop['doc']} |\n"

            doctext += "\n\n"
            doctext += "## Methods \n\n"

            if not methods_struct:
                doctext += "*none*\n"
            else:
                doctext += "| Method | Description |\n| --- | --- |\n"
                for method in methods_struct:
                    doctext += f"| *{method['method']}* | {method['description']} |\n"

                doctext += "\n\n"
                doctext += "### Methods help \n\n"
                for method in methods_struct:
                    doctext += f"**{method['method']}** - *{method['description']}*\n\n"
                    doctext += f"```\n{method['help']}\n```\n\n---\n\n"

        # Write to file
        output_file = os.path.join(output_path, m_file + '.md')
        str2text(output_file, doctext)
        out.append(out_here)

    # Classes in w.classes?
    # Loop over classes separately?
    # In original: for i=1:numel(w.classes), warning(['Do not know how to write classes yet. Fix me!']); end;
    # It seems w.m included classes, and w.classes are just the class names?
    # If we processed them in m_files, we are good.

    # Packages
    packagelist = []
    for pkg in packages:
        pkg_dirname = '+' + pkg
        packagelist.append(pkg_dirname)

        out_here = {}
        out_here['title'] = pkg + ' PACKAGE'
        out_here['url_prefix'] = url_prefix

        next_inputdir = os.path.join(input_path, pkg_dirname)
        next_outputdir = os.path.join(output_path, pkg_dirname)
        next_ymlpath = os.path.join(ymlpath, pkg_dirname)
        next_packageprefix = packageprefix + pkg + '.'

        outst = matlab2markdown(next_inputdir, next_outputdir, next_ymlpath, objectstruct, next_packageprefix, url_prefix)

        if outst:
            out_here['path'] = outst
            out.append(out_here)

    # Directories (folders) that are not packages
    # d = dir(input_path)
    # d = vlt.file.dirlist_trimdots(d)

    # We need to exclude processed packages and files

    # Get all subdirectories
    all_subdirs = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]

    # Filter
    filtered_dirs = dirlist_trimdots(all_subdirs)

    # Remove packages from this list
    final_dirs = [d for d in filtered_dirs if d not in packagelist]

    for d_name in final_dirs:
        out_here = {}
        out_here['title'] = d_name + ' FOLDER'
        out_here['url_prefix'] = url_prefix

        next_inputdir = os.path.join(input_path, d_name)
        next_outputdir = os.path.join(output_path, d_name)
        next_ymlpath = os.path.join(ymlpath, d_name)

        outst = matlab2markdown(next_inputdir, next_outputdir, next_ymlpath, objectstruct, '', url_prefix)

        if outst:
            out_here['path'] = outst
            out.append(out_here)

    return out
