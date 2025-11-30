import pandas as pd

def emptytable(*args):
    """
    EMPTYTABLE - make an empty table

    T = EMPTYTABLE("variable1Name","variable1DataType",...
       "variable2Name","variable2DataType", ...)

    Create an empty table with the variable names (column names) provided.

    Example:
      t = vlt.data.emptytable("id","string","x","double","y","double");

    Note: Python/Pandas types are inferred from string names where possible,
    but mainly columns are created.
    """

    names = []
    types = []

    # Process args
    # args are alternating name, type

    if len(args) % 2 != 0:
        raise ValueError("Arguments must be pairs of Name and Type")

    for i in range(0, len(args), 2):
        names.append(args[i])
        types.append(args[i+1])

    df = pd.DataFrame(columns=names)

    # Ideally we would set types, but pandas handles empty dfs gracefully.
    # We could try to cast if needed, but for now just empty dataframe with columns is fine.

    return df
