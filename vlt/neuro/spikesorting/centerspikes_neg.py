import numpy as np

def centerspikes_neg(spikeshapes, center_range):
    """
    Center negative-going spike waveforms based on minimum.

    [CENTEREDSPIKES, SHIFTS] = centerspikes_neg(SPIKESHAPES, CENTER_RANGE)

    Inputs:
        spikeshapes: NxMxD numpy array where N is the number of spikes, M is the
            number of samples that comprise each spike waveform, and D is dimensions
            (i.e., number of channels).
        center_range: the range, in samples, around the center sample that the program
            should search to identify the center (e.g., 10)

    Outputs:
        centeredspikes: the re-centered spikes; if the center of a spike has shifted, then
            the edges will be zero padded.
        shifts: the number of samples the spike has been shifted. Negative means the centered spike
            was shifted to the left, positive is shifted to the right.
    """

    spikeshapes = np.array(spikeshapes)

    # Handle dimensions
    if spikeshapes.ndim == 2:
        # If NxM, assume D=1. Reshape to NxMx1
        spikeshapes = spikeshapes[:, :, np.newaxis]

    if spikeshapes.ndim != 3:
        raise ValueError("spikeshapes must be NxMxD or NxM")

    N, M, D = spikeshapes.shape

    # MATLAB: center_pts = round((M)/2) + [-center_range:center_range ];
    # Replicate MATLAB round(M/2):
    center_idx_matlab = int(np.floor(M/2 + 0.5))

    # Python 0-based center index
    center_idx_py = center_idx_matlab - 1

    # Search indices relative to spike start (0-based)
    search_indices = np.arange(-center_range, center_range + 1) + center_idx_py

    shifts = np.zeros(N, dtype=int)
    centeredspikes_list = []

    for i in range(N):
        spike = spikeshapes[i] # M x D

        # Extract the window to search for min
        # Ensure indices are within bounds? MATLAB code doesn't explicitly check,
        # assumes reasonable center_range relative to M.
        # We will assume valid indices for now.
        ss = spike[search_indices, :] # (2*center_range+1) x D

        # Find global minimum in the window
        flat_idx = np.argmin(ss)
        min_row, min_col = np.unravel_index(flat_idx, ss.shape)

        # min_row is the index within 'ss' (0 to 2*center_range)
        # We want shift relative to the center of the window.
        # In the window, the center element is at index 'center_range'.
        # shift = (index of min) - (index of center)
        # shift = min_row - center_range

        # Let's verify with MATLAB logic:
        # MATLAB: shift = center_pts(min_index) - round((M)/2);
        # center_pts(min_index) is the absolute sample index.
        # round(M/2) is absolute center index.
        # shift = absolute_sample_index - absolute_center_index
        #
        # Python:
        # absolute_sample_index = search_indices[min_row]
        # absolute_center_index = center_idx_py
        # shift = search_indices[min_row] - center_idx_py
        #
        # search_indices[min_row] = min_row - center_range + center_idx_py
        # shift = (min_row - center_range + center_idx_py) - center_idx_py
        # shift = min_row - center_range

        shift = min_row - center_range

        # MATLAB: shifts(i) = -shift;
        shifts[i] = -shift

        # Padding and shifting
        # Pad along time axis (axis 0)
        # We want to shift the spike 'shift' samples to the left (if shift < 0) or right.
        # Actually:
        # If min is to the left of center (shift < 0), we want to center it.
        # So we need to shift the waveform to the RIGHT (positive shift) to bring it to center?
        # Let's trace MATLAB:
        # shift = found_loc - center_loc. (e.g. found at 10, center is 15. shift = -5).
        # We want to move found_loc (10) to center_loc (15). So we add +5.
        # MATLAB does: paddedspike = paddedspike(1, shift+center_range+1 : ...)
        # Wait, MATLAB `shift` variable is `center_pts(min_index) - round((M)/2)`.
        # If min is to the left, shift is negative.
        # To center it, we need to extract a window that is shifted to the left?
        # paddedspike has `center_range` zeros at start.
        # If shift is -5, start index = -5 + center_range + 1.
        # If center_range=10, start index = -5 + 10 + 1 = 6.
        # Original starts at 11 (because of 10 padding).
        # So we start reading earlier (at 6). This effectively shifts the data to the RIGHT in the output window.
        # Yes.

        # My Python slicing:
        # start_idx = shift + center_range
        # If shift = -5, start_idx = 5.
        # Original data starts at `center_range` = 10.
        # So we read from 5, which includes 5 zeros then data.
        # This shifts data right by 5 samples. Correct.

        padded_spike = np.pad(spike, ((center_range, center_range), (0, 0)), mode='constant')
        start_idx = shift + center_range
        end_idx = start_idx + M

        new_spike = padded_spike[start_idx:end_idx, :]
        centeredspikes_list.append(new_spike)

    centeredspikes = np.array(centeredspikes_list)

    return centeredspikes, shifts
