def isa_text(classname_a, classname_b):
    """
    Examines whether a class is a subclass of another class type.

    Args:
        classname_a (str): The class name to check.
        classname_b (str): The potential superclass name.

    Returns:
        tuple: (bool, list) where bool is True if a is b or subclass of b.
               list contains all superclasses of a including itself (as strings).

    Note:
        In Python, this requires importing the class by name to check inheritance.
        This implementation attempts to import the class from string.
        If class cannot be found, it might fail or return False.
        The MATLAB version uses `superclasses` function.
    """
    import importlib

    def get_class(name):
        # Try to import. Assuming name is fully qualified like 'pkg.module.Class'
        try:
            parts = name.split('.')
            module_name = ".".join(parts[:-1])
            class_name = parts[-1]
            if not module_name:
                # Maybe built-in or in current scope?
                # Try builtins
                import builtins
                return getattr(builtins, class_name, None)

            module = importlib.import_module(module_name)
            return getattr(module, class_name, None)
        except (ImportError, AttributeError, ValueError):
            return None

    cls_a = get_class(classname_a)

    if cls_a is None:
        # If we can't load the class, we can't determine inheritance.
        # But maybe we are just checking string equality?
        # MATLAB `isa_text` works on strings.
        # If we can't load, we assume False unless equal?
        # Let's just return equal check if not loaded?
        if classname_a == classname_b:
            return True, [classname_a]
        return False, []

    # Get MRO
    mro = cls_a.mro() # This gives classes
    # Convert to strings
    # We need fully qualified names

    mro_names = []
    for c in mro:
        name = c.__qualname__
        if c.__module__ != 'builtins':
            name = c.__module__ + '.' + name
        mro_names.append(name)

    # We also need to handle `classname_b`.
    # Usually `classname_b` is just a string we compare against.

    # Check if classname_b is in mro_names
    # BUT, classname_b might be 'int' (builtin) or 'vlt.math.Something'.
    # Python naming is tricky.

    # If classname_b is in the list, return True.
    # Note: `mro` includes the class itself.

    b = classname_b in mro_names
    # Or strict equality check if names are consistent.

    return b, mro_names
