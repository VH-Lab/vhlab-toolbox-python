def cluster_spikewaves_gui(*args, **kwargs):
    """
    CLUSTER_SPIKEWAVES_GUI - Cluster spikewaves into groups with manual checking (GUI).

    This function corresponds to the MATLAB function `vlt.neuro.spikesorting.cluster_spikewaves_gui`.

    In the MATLAB implementation, this function brings up a graphical user interface (GUI)
    to allow the user to divide the spikewaves into groups using several algorithms,
    and to check the output of these algorithms with different views.

    Porting Note:
    This function relies heavily on MATLAB's GUI frameworks (uicontrols, figures, callbacks)
    which do not have a direct 1:1 mapping in a standard headless Python environment or
    without a specific GUI framework choice (e.g., PyQt, Tkinter).

    As such, this function is currently a stub and raises a NotImplementedError.

    Original Docstring:
    [CLUSTERIDS,CLUSTERINFO] = vlt.neuro.spikesorting.cluster_spikewaves_gui('WAVES', WAVES, ...
       'WAVEPARAMETERS', WAVEPARAMETERS, ...)
    """
    raise NotImplementedError("The GUI function 'cluster_spikewaves_gui' has not been ported to Python yet.")
