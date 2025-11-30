import re

def strcmp_substitution(s1, s2, **kwargs):
    """
    STRCMP_SUBSTITUTION - Checks strings for match with ability to substitute a symbol for a string

    tf, match_string, substitute_string = vlt.string.strcmp_substitution(s1, s2, **kwargs)

    Compares s1 and s2 and returns in tf a logical True if they are of the same form and False otherwise.
    These strings are of the same form if
       a) s1 and s2 are identical
       b) s2 is a regular expression match of s1 (where s1 is the pattern)
       c) s2 matches s1 when the symbol '#' in s1 is replaced by some string in s2.
          This is determined by checking if s2 matches s1 where '#' is replaced by '(.+)'.
          If so, the part of s2 that corresponds to '#' is returned in substitute_string.

    In any case, the entire matched string match_string will be returned (which corresponds to s2 elements).

    Parameters:
    s1 (str): The template string or pattern.
    s2 (str or list of str): The string(s) to check against s1.
    **kwargs:
        SubstituteStringSymbol (str): The symbol to indicate the substitute string (default '#')
        UseSubstituteString (bool): Should we use the SubstituteString option? (default True)
        SubstituteString (str): Force the function to use this string as the only acceptable
                                replacement for SubstituteStringSymbol (default '')
        ForceCellOutput (bool): If True, output lists even if s2 was a single string. (default False)

    Returns:
    tf (bool or list of bool): Match status for each element.
    match_string (str or list of str): The string that matched.
    substitute_string (str or list of str): The extracted substring that replaced the symbol.

    Note: In Python, s1 is treated as a regex pattern if it's not a direct match.
    MATLAB uses regexp(s2, s1). So s1 is the pattern.
    """

    SubstituteStringSymbol = kwargs.get('SubstituteStringSymbol', '#')
    UseSubstituteString = kwargs.get('UseSubstituteString', True)
    # LiteralCharacter = '\\' # Not used directly in simple port unless we handle escaping
    SubstituteString = kwargs.get('SubstituteString', '')
    ForceCellOutput = kwargs.get('ForceCellOutput', False)

    made_list = False
    if isinstance(s2, str):
        s2 = [s2]
        made_list = True

    s2_list = s2

    # Initialize outputs
    tf = [False] * len(s2_list)
    substitute_string = [''] * len(s2_list)
    match_string = list(s2_list)

    # Step 1: Exact matches
    for i, s in enumerate(s2_list):
        if s1 == s:
            tf[i] = True

    # Step 2: Regexp matches
    # s1 is the pattern.
    for i, s in enumerate(s2_list):
        if not tf[i]:
            # MATLAB: S = regexp(s2(indexes), s1);
            # Check if s1 matches s
            if re.search(s1, s):
                tf[i] = True

    # Step 3: Substitution matches
    if UseSubstituteString:
        # Construct pattern for substitution
        # We need to replace SubstituteStringSymbol with regex.
        # But we must be careful about special regex chars in s1.
        # MATLAB doesn't escape s1 by default? "s1 is a regular expression match of s1"
        # If s1 contains '#' and we want to treat it as substitution, we should probably
        # escape other parts if they are literals. But the doc says "s2 is a regular expression match of s1".
        # This implies s1 IS a regex.
        # So if s1 = 'stimtimes#.txt', it implies '.' is any char.
        # If user meant literal dot, they should have escaped it?
        # MATLAB code: myregexp = SubstituteStringSymbol;
        # mymatches = setdiff( regexp(s1,myregexp), ... )
        # It finds '#' positions.

        # If SubstituteString is provided, we replace '#' with it and check exact/regex match.

        # We should split s1 by '#' and build a regex.
        if SubstituteStringSymbol in s1:
            parts = s1.split(SubstituteStringSymbol)

            # If SubstituteString is provided (forced substitution)
            if SubstituteString:
                # Reconstruct s1 with fixed substitution
                s1_fixed = SubstituteString.join(parts)
                # Check match
                for i, s in enumerate(s2_list):
                    if not tf[i]:
                        if re.search(s1_fixed, s) or s1_fixed == s:
                             tf[i] = True
                             substitute_string[i] = SubstituteString
            else:
                # Variable substitution. Replace '#' with '(.+)' or similar.
                # MATLAB: s1_ = [s1_(1:mymatches(i)-1) '(.+)' s1_(mymatches(i)+1:end)];
                # Python re: capture group is (.*) or (.+). MATLAB uses (.+).

                # We need to be careful. s1 might contain regex syntax.
                # If s1 is 'stimtimes#.txt', and we turn it into 'stimtimes(.+)txt'.
                # But 't' is literal.

                # If multiple '#' exist? MATLAB errors: "Cannot deal with multiple locations".
                if s1.count(SubstituteStringSymbol) > 1:
                     raise ValueError(f"Cannot deal with multiple locations for string match: {s1}")

                # Replace '#' with '(.+)'
                pattern = s1.replace(SubstituteStringSymbol, '(.+)')

                for i, s in enumerate(s2_list):
                    if not tf[i]:
                        m = re.search(pattern, s)
                        if m:
                            tf[i] = True
                            # Extract the group
                            # We assume the FIRST capture group is the substitution.
                            # But s1 might have other groups?
                            # MATLAB: s1_ = ... '(.+)' ...
                            # It assumes this is the one we want.
                            # In Python, we can check groups.
                            # If s1 already had parens, we might capture more.
                            # But let's assume simple case or take the one corresponding to (.+).
                            # If s1 has other groups, determining which one corresponds to # is hard without parsing.
                            # However, given the use case, s1 is likely simple.
                            # Or we can count groups before #?

                            # Let's trust that the user only adds one capture group via #.
                            # If s1 had other parens, it's ambiguous.
                            # But MATLAB code `S{indexeshere(j)}{1}{1}` implies it takes the first token found?
                            # `regexp(..., 'tokens')` returns list of tokens.
                            # If multiple tokens (groups), it returns them all.
                            # MATLAB implementation seems to take the first one? `S{...}{1}{1}`.

                            if m.groups():
                                substitute_string[i] = m.group(1)

    # Clean up non-matches
    for i in range(len(s2_list)):
        if not tf[i]:
            match_string[i] = ''
            substitute_string[i] = ''

    # Return single or list
    if made_list and not ForceCellOutput:
        return tf[0], match_string[0], substitute_string[0]
    else:
        return tf, match_string, substitute_string
