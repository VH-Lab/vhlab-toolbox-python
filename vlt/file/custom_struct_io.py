import vlt.data
import re

def loadStructArray(fname, fields=None):
    """
    LOADSTRUCTARRAY - load a struct array from a tab-delimited file

    A = vlt.file.loadStructArray(FNAME [, FIELDS])

    Reads tab-delimited text from the file FNAME to create a list of dicts.
    """
    a = []

    try:
        with open(fname, 'r') as f:
            lines = f.read().splitlines()
    except Exception as e:
        raise Exception(f"Could not open file {fname}.")

    if not lines:
        return []

    # Read header
    header_line = lines[0]

    # Python split('\t') will produce list of fields
    # If fields arg is not provided
    if fields is None:
        raw_fields = header_line.split('\t')
        fields = []
        for rf in raw_fields:
            # makeValidName logic?
            # Replace spaces with _, remove invalid chars
            # Simple version:
            f = re.sub(r'[^a-zA-Z0-9_]', '_', rf)
            if f and f[0].isdigit():
                f = '_' + f
            fields.append(f)

    # Read data
    for i in range(1, len(lines)):
        s = lines[i]
        if s:
            try:
                entry = vlt.data.tabstr2struct(s, fields)
                a.append(entry)
            except Exception as e:
                # Warning or error? MATLAB errors but catches and breaks?
                # "error(['Error reading data content line ' ... int2str(count) ': ' lasterr]);"
                # It seems it stops reading and raises error.
                raise Exception(f"Error reading data content line {i+1}: {e}")

    return a

def saveStructArray(fname, gdi, header=True):
    """
    SAVESTRUCTARRAY - Save a structure array into a text file

    vlt.file.saveStructArray(FILENAME, STRUCTARRAY, [HEADER])

    Saves list of dicts GDI into a text file.
    """

    try:
        with open(fname, 'w') as f:
            if not gdi:
                return # Nothing to write

            # Identify fields from the first element or all?
            # MATLAB uses fieldnames(gdi([])) which implies fieldnames of the struct array.
            # In Python list of dicts, keys might vary, but usually consistent.
            # We take keys from first element.
            keys = list(gdi[0].keys())

            if header:
                f.write('\t'.join(keys) + '\n')

            for item in gdi:
                # Enforce column order based on 'keys'
                s = ''
                for key in keys:
                    val = item.get(key)
                    if val is None:
                        val_str = ''
                    elif isinstance(val, str):
                        val_str = val
                    else:
                        val_str = str(val)

                    s += '\t' + val_str

                # Remove leading tab
                if s.startswith('\t'):
                    s = s[1:]

                f.write(s + '\n')

    except Exception as e:
        # disp([msg,': ',fname]);
        print(f"Error writing to {fname}: {e}")
