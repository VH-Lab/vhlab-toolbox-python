def replacefunction(fuse, replacement_table, **kwargs):
    """
    Replace instances of one function call with another.

    Args:
        fuse (list of dicts): Function usage structures.
        replacement_table (list of dicts or dict):
            Table with keys 'original' and 'replacement'.
            If list, searches for match.
        **kwargs:
            MinLine (int): Default 2.
            Disable (int/bool): Default True (1).
            interactive (bool): Helper for python port. If True, uses input().
                                If False, assumes 'y' or uses a callback?
                                The MATLAB code calls input().
                                In Python tests, we should mock input.

    Returns:
        list: Status strings.
    """
    import os

    # Python doesn't have `vlt.file.text2cellstr` equivalent mapped yet?
    # We can just use readlines.

    MinLine = kwargs.get('MinLine', 2)
    Disable = kwargs.get('Disable', 1)

    # Since `input()` blocks, we might want to allow injection of responses or non-interactive mode.
    # But strictly following port, it uses input().
    # We will assume input() is mocked during tests.

    status = [None] * len(fuse)

    # Normalize replacement_table to list if dict
    if isinstance(replacement_table, dict):
        replacement_table = [replacement_table]

    for f_idx, item in enumerate(fuse):
        # Find replacement
        rep_entry = None
        for entry in replacement_table:
            if entry['original'] == item['name']:
                rep_entry = entry
                break

        if rep_entry is None:
            import warnings
            warnings.warn(f"No entry for {item['name']} in replacement table.")
            continue

        replacement_str = rep_entry['replacement']

        if item['line'] <= MinLine:
            status[f_idx] = 'Skipped'
            continue

        # Read file
        try:
            with open(item['fullfilename'], 'r') as f:
                lines = f.readlines()
        except OSError:
            status[f_idx] = 'Error reading file'
            continue

        # Display context
        # MATLAB uses 1-based lines. Python 0-based list.
        # item['line'] is 1-based.
        line_idx = item['line'] - 1

        start_line = max(0, line_idx - 2)
        end_line = min(len(lines), line_idx + 3)

        context = lines[start_line:end_line]

        print('\n\n\n\n\n')
        print(item)
        print('\n\n\n\n\n')
        for l in context:
            print(l.rstrip())
        print('\n\n')

        current_line_content = lines[line_idx]
        print(current_line_content.rstrip())

        prompt = (f"{f_idx+1}/{len(fuse)}:Should we replace {item['name']} "
                  f"with {replacement_str}? ([Y]es/[N]o/[W]rite Note/[Q]uit):")

        reply = input(prompt).strip().lower()

        if reply == 'y':
            # Perform replacement in memory
            # line content: ... name ...
            # item['character'] is 1-based start index of name.
            char_idx = item['character'] - 1
            name_len = len(item['name'])

            # Reconstruct line
            # line[:char_idx] + replacement + line[char_idx+len:]

            # Careful: if multiple replacements in same line, indices shift.
            # But the loop processes one `fuse` entry at a time.
            # The code updates future fuse entries if they are on the same line.

            # Verify if the text at char_idx is indeed name
            actual_text = lines[line_idx][char_idx : char_idx + name_len]
            if actual_text != item['name']:
                # Maybe shifted due to previous edits?
                # This suggests we should reload file or track shifts.
                # MATLAB code updates `future_index` logic.
                pass

            new_line = (lines[line_idx][:char_idx] +
                        replacement_str +
                        lines[line_idx][char_idx + name_len:])

            lines[line_idx] = new_line
            print(new_line.rstrip())

            if not Disable:
                # Write back to file
                with open(item['fullfilename'], 'w') as f:
                    f.writelines(lines)

                # Update future fuse entries
                shift = len(replacement_str) - len(item['name'])
                if shift != 0:
                    for future_idx in range(f_idx + 1, len(fuse)):
                        f_item = fuse[future_idx]
                        if (f_item['fullfilename'] == item['fullfilename'] and
                            f_item['line'] == item['line'] and
                            f_item['character'] > item['character']):

                            f_item['character'] += shift
                            # fuse is modified in place (list of dicts is mutable)

            status[f_idx] = 'Replaced'
            if Disable:
                status[f_idx] = 'Replace (for fake, disabled)'

        elif reply == 'n':
            status[f_idx] = 'Skipped'
        elif reply == 'w':
            note = input('Write note and hit return:')
            status[f_idx] = note
        elif reply == 'q':
            status[f_idx] = 'Skipped due to quit'
            return status # Return what we have
        else:
            print('unknown input, skipping')
            status[f_idx] = 'Skipped due to unknown input'

    return status
