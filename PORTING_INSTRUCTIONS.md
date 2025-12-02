# Porting Instructions

We are porting from the public repo https://github.com/VH-Lab/vhlab-toolbox-matlab

We do not need to port the entire matlab repo but only the functions inside the namespace `vlt`.

If files need to read from .mat files, make no assumptions as to whether the .mat file is version 7.3 or later. Some programs read files in .mat format even if the file does not have a .mat extension (look for '-mat' option in Matlab load or save functions).

## Scope

Only port functions and classes within the `vlt` namespace as requested.

## Namespace

The functions/classes in python should have the same namespace form as the Matlab functions/classes. For example, `vlt.data.dropnan` in Matlab should be `vlt.data.dropnan` in Python.

## Testing

Unittests should be created for all functions/classes.
