import pandas as pd

def flattenstruct2table(s, abbrev=None):
    """
    FLATTENSTRUCT2TABLE Flattens a structure (list of dicts) to a table (DataFrame), preserving nested struct array data.

    T = flattenstruct2table(S)
    T = flattenstruct2table(S, ABBREV)

    Args:
        s: List of dictionaries (struct array equivalent)
        abbrev: List of [string_to_replace, replacement] pairs

    Returns:
        pd.DataFrame
    """

    if abbrev is None:
        abbrev = []

    if not isinstance(s, list):
        # Could be single dict
        if isinstance(s, dict):
            s = [s]
        else:
             raise ValueError("Input must be a list of dictionaries (structure array).")

    if len(s) == 0:
        return pd.DataFrame()

    # Python doesn't have a direct "struct" type, so we assume dicts.
    # The complexity is handling nested lists of dicts (struct arrays).

    # Strategy: Flatten each item in the list

    flattened_data = []

    for item in s:
        flat_item = _flatten_scalar_recursive(item, '')
        flattened_data.append(flat_item)

    df = pd.DataFrame(flattened_data)

    # Rename columns if needed
    if abbrev:
        new_cols = {}
        for col in df.columns:
            new_name = col
            for abbr in abbrev:
                new_name = new_name.replace(abbr[0], abbr[1])
            new_cols[col] = new_name
        df.rename(columns=new_cols, inplace=True)

    return df

def _flatten_scalar_recursive(s_scalar, prefix):
    """
    Recursive helper to flatten a single dict.
    """
    res = {}

    for key, value in s_scalar.items():
        new_key = f"{prefix}{key}"

        if isinstance(value, dict):
            # Nested dict (scalar struct)
            sub_res = _flatten_scalar_recursive(value, f"{new_key}.")
            res.update(sub_res)
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            # Nested list of dicts (struct array)
            # The original MATLAB code collects sub-fields into cell arrays.
            # value is a list of dicts.
            # We need to collect keys from all dicts in the list.

            # Find all keys across all dicts in the list
            all_keys = set()
            for sub_item in value:
                all_keys.update(sub_item.keys())

            for sub_key in all_keys:
                # Collect values for this key
                collected_values = []
                for sub_item in value:
                    collected_values.append(sub_item.get(sub_key, None)) # None or default?

                # Store as list
                res[f"{new_key}.{sub_key}"] = collected_values
        else:
            # Base case
            res[new_key] = value

    return res
