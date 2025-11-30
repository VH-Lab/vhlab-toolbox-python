import numpy as np
import matplotlib.pyplot as plt

def plot_multichan(data, t, space):
    """
    PLOT_MULTICHAN - Plots multiple channels

    H = plot_multichan(DATA, T, SPACE)

    Plots multiple channels of DATA (assumed to be NUMSAMPLES X NUMCHANNELS)

    T is the time for each sample and SPACE is the space to put between channels.

    Arguments:
        data: (numpy array) data samples (rows) x channels (columns)
        t: (numpy array) time vector
        space: (float) vertical spacing between channels

    Returns:
        h: list of line handles
    """

    data = np.array(data)
    t = np.array(t)

    # Check dimensions. If data is 1D, make it 2D column
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    num_samples, num_channels = data.shape

    h = []

    # Iterate through channels
    for i in range(num_channels):
        # Calculate offset
        # MATLAB: (i-1)*space + data(:,i)
        # Python: i * space + data[:, i] (since i starts at 0)

        offset_data = (i * space) + data[:, i]

        # Plot
        # MATLAB uses color [0.7 0.7 0.7] (grey)
        line, = plt.plot(t, offset_data, color=[0.7, 0.7, 0.7])
        h.append(line)

    return h
