import numpy as np
import matplotlib.pyplot as plt

def plot_stimulus_timeseries(y, stimon, stimoff, **kwargs):
    """
    PLOT_STIMULUS_TIMESERIES - plot the occurence of a stimulus or stimuli as a thick bar on a time series plot

    [H,HTEXT] = vlt.neuro.stimulus.plot_stimulus_timeseries(Y, STIMON, STIMOFF, ...)

    Uses a thick horizontal bar to indicate the presentation time of a set of stimuli.
    STIMON should be a vector containing all stimulus ON times.
    STIMOFF should be a vector containing all stimulus OFF times.

    This function takes additional arguments in the form of name/value pairs:

    Parameter (default value)          | Description
    ---------------------------------------------------------------------------
    stimid ([])                        | Stimulus ID numbers for each entry in
                                       |     STIMON/STIMOFF; if present, will be plotted
                                       |     Can also be a cell array of string names
    linewidth (2)                      | Line size
    linecolor ([0, 0, 0])              | Line color
    FontSize (12)                      | Font size for text (if 'stimid' is present)
    FontWeight ('normal')              | Font weight
    FontColor ([0, 0, 0])              | Text default color
    textycoord (Y+1)                   | Text y coordinate
    HorizontalAlignment ('center')     | Text horizontal alignment
    """

    stimid = kwargs.get('stimid', [])
    linewidth = kwargs.get('linewidth', 2)
    linecolor = kwargs.get('linecolor', [0, 0, 0])
    FontSize = kwargs.get('FontSize', 12)
    FontWeight = kwargs.get('FontWeight', 'normal')
    FontColor = kwargs.get('FontColor', [0, 0, 0])
    textycoord = kwargs.get('textycoord', y + 1)
    HorizontalAlignment = kwargs.get('HorizontalAlignment', 'center')

    stimon = np.array(stimon).flatten()
    stimoff = np.array(stimoff).flatten()

    h = []
    htext = []

    for i in range(len(stimon)):
        # Plot line
        line, = plt.plot([stimon[i], stimoff[i]], [y, y], color=linecolor, linewidth=linewidth)
        h.append(line)

        if len(stimid) > 0: # Check if stimid is not empty
            xcoord = np.mean([stimon[i], stimoff[i]])

            # Handle stimid being list or array
            if isinstance(stimid, (list, np.ndarray)):
                 if i < len(stimid):
                    val = stimid[i]
                    stimstr = str(val)
                 else:
                    stimstr = ""
            else:
                 stimstr = str(stimid)

            text_obj = plt.text(xcoord, textycoord, stimstr,
                                fontweight=FontWeight, fontsize=FontSize,
                                horizontalalignment=HorizontalAlignment, color=FontColor)
            htext.append(text_obj)

    return h, htext
