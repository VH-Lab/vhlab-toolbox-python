import numpy as np
import matplotlib.pyplot as plt

def supersubplot(fig, m, n, p):
    """
    SUPERSUBPLOT - Organize axes across multiple figures

    AX_H = supersubplot(FIG, M, N, P)

    Returns a set of axes that can be arranged across multiple figures.

    Inputs:
        FIG - figure number of the first figure in series (or pyplot figure object)
        M - The number of rows of plots in each figure
        N - the number of columns of plots in each figure
        P - the plot number to use, where the numbers go
            from left to right, top to bottom, and then
            continue across figures. (1-based index)

    Outputs: AX_H - the axes handle
    """

    # Handle 'fig' argument
    # If fig is None or invalid, create new figure.
    # In Python/Matplotlib, figures are objects or integers (indices).

    start_fig = None

    if fig is None:
        start_fig = plt.figure()
    elif isinstance(fig, int):
        if plt.fignum_exists(fig):
             start_fig = plt.figure(fig)
        else:
             # Create with that number? Or just create new?
             # Matplotlib creates if not exists
             start_fig = plt.figure(fig)
    elif hasattr(fig, 'number'): # Figure object
        start_fig = fig
    else:
        # Some other handle? Assume create new
        start_fig = plt.figure()

    # We need to store/retrieve the list of associated figures.
    # MATLAB uses 'userdata'.
    # We can attach an attribute to the figure object.
    # Let's call it `_supersubplot_figures`.

    if not hasattr(start_fig, '_supersubplot_figures'):
        # Initialize with itself as the first figure (index 0)
        start_fig._supersubplot_figures = {1: start_fig}

    ud = start_fig._supersubplot_figures

    # Calculate which figure number and plot number we need.
    # p is 1-based index across all figures.
    # m*n plots per figure.

    plots_per_fig = m * n

    # Python integer division
    # figure_number = ceil(p / plots_per_fig)
    figure_number = int(np.ceil(p / plots_per_fig))

    # Determine which figure object to use
    if figure_number in ud:
        current_fig = ud[figure_number]
        plt.figure(current_fig.number) # Make active
    else:
        # Create new figure
        current_fig = plt.figure()
        ud[figure_number] = current_fig
        # Update the dictionary on the start_fig so it tracks this new one
        start_fig._supersubplot_figures = ud

    # Calculate plot index within the figure
    # MATLAB: plotnumber = p - m*n*(figure_number-1)
    plotnumber = p - plots_per_fig * (figure_number - 1)

    # Create subplot
    # subplot takes (rows, cols, index) where index is 1-based
    ax = current_fig.add_subplot(m, n, plotnumber)

    return ax
