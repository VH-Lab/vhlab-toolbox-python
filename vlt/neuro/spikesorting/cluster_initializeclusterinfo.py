def cluster_initializeclusterinfo():
    """
    Initialize cluster info structure.

    Returns a list of dictionaries representing the initialized cluster info.

    Structure fields:
    - number
    - qualitylabel
    - number_of_spikes
    - meanshape
    - EpochStart
    - EpochStop
    """

    # In MATLAB, this often returns an empty struct array `struct('number',[],...)`
    # which is 0x0 struct array with those fields.
    # Or sometimes a single empty element?
    # `clusterinfo=struct('number',[],'qualitylabel','','number_of_spikes',[],'meanshape',[],'EpochStart',[],'EpochStop',[]);`
    # `clusterinfo = clusterinfo([]);` -> makes it empty 0x1 struct array.

    return []
