import re
import numpy as np

def fieldsearch(A, searchstruct):
    """
    FIELDSEARCH - Search a structure to determine if it matches a search structure

    B = vlt.data.fieldsearch(A, SEARCHSTRUCT)

    Determines if a structure A (dict) matches the search structure SEARCHSTRUCT (dict or list of dicts).
    """

    # Handle list of search structs (AND condition)
    if isinstance(searchstruct, list):
        for s in searchstruct:
            if not fieldsearch(A, s):
                return False
        return True

    # Single search struct
    b = False

    field = searchstruct.get('field', '')
    operation = searchstruct.get('operation', '')
    param1 = searchstruct.get('param1', None)
    param2 = searchstruct.get('param2', None)

    isthere = field in A
    value = A.get(field)

    negation = False
    if operation.startswith('~'):
        negation = True
        operation = operation[1:]

    op = operation.lower()

    if op == 'regexp':
        if isthere and isinstance(value, str):
            if re.search(param1, value, re.IGNORECASE):
                b = True
    elif op == 'exact_string':
        if isthere and isinstance(value, str):
            if value == param1:
                b = True
    elif op == 'exact_string_anycase':
        if isthere and isinstance(value, str):
            if value.lower() == param1.lower():
                b = True
    elif op == 'contains_string':
        if isthere and isinstance(value, str):
            if param1 in value:
                b = True
    elif op == 'exact_number':
        if isthere:
            # use eqlen logic equivalent
            if np.array_equal(np.array(value), np.array(param1)):
                b = True
    elif op == 'lessthan':
        if isthere:
            if np.all(np.array(value) < param1):
                b = True
    elif op == 'lessthaneq':
        if isthere:
            if np.all(np.array(value) <= param1):
                b = True
    elif op == 'greaterthan':
        if isthere:
            if np.all(np.array(value) > param1):
                b = True
    elif op == 'greaterthaneq':
        if isthere:
            if np.all(np.array(value) >= param1):
                b = True
    elif op == 'hassize':
        if isthere:
            # shape check
            val_shape = np.shape(value) if hasattr(value, 'shape') else np.shape(np.array(value))
            if np.array_equal(val_shape, param1):
                b = True
    elif op == 'hasmember':
        if isthere:
            # check if param1 is in value
            if param1 in value: # works for list, string, etc.
                 b = True
            elif hasattr(value, '__iter__'):
                 if any(np.array_equal(param1, x) for x in value):
                     b = True
    elif op == 'hasfield':
        b = isthere
    elif op == 'partial_struct':
        if isthere:
            # We need structpartialmatch equivalent.
            # Assume it checks if param1 (dict) is subset of value (dict)
            if isinstance(value, dict) and isinstance(param1, dict):
                # recursive check? Or shallow? partialmatch usually implies fields match.
                # Let's implement shallow check for now or assume strict equality of subfields
                match = True
                for k, v in param1.items():
                    if k not in value or value[k] != v:
                        match = False
                        break
                b = match
    elif op in ['hasanysubfield_contains_string', 'hasanysubfield_exact_string']:
        if isthere and isinstance(value, (list, tuple)): # array of structs
            p1_list = param1 if isinstance(param1, list) else [param1]
            p2_list = param2 if isinstance(param2, list) else [param2]

            for item in value:
                if isinstance(item, dict):
                    b_ = True
                    for k_idx, k_field in enumerate(p1_list):
                        if k_field in item:
                            val2 = item[k_field]
                            match_str = p2_list[k_idx]
                            if op == 'hasanysubfield_contains_string':
                                if isinstance(val2, str) and match_str in val2:
                                    pass
                                else:
                                    b_ = False
                            else: # exact
                                if isinstance(val2, str) and val2 == match_str:
                                    pass
                                else:
                                    b_ = False
                        else:
                            b_ = False
                    if b_:
                        b = True
                        break
    elif op == 'or':
        # param1 and param2 are searchstructs
        b = fieldsearch(A, param1) or fieldsearch(A, param2)

    if negation:
        b = not b

    return b
