import numpy as np

def dotdisc(data, dots):
    """
    DOTDISC - Dot discriminator, an advanced window discriminator

    event_samples = dotdisc(data, dots)

    Detect events with "dots", a form of advanced window discrimination.

    Parameters:
    data (array-like): The data to be examined.
    dots (array-like): An N x 3 matrix with the "dots" to be used for the
                       discrimination. The first row is [THRESH, SIGN, 0] indicating
                       that all events larger than THRESH (in the direction of SIGN,
                       which can be 1 or -1) will be considered. Each additional
                       row is [THRESH, SIGN, OFFSET], and only events that have a
                       signal of size THRESH (in the direction of SIGN) at the sample
                       location OFFSET relative to the highest/lowest point that
                       was determined in the first row will be selected.

    Returns:
    event_samples (numpy.ndarray): The sample numbers of events that are described
                                   by the DOTS. If more than one adjacent sample
                                   passes the dot tests, then the sample number
                                   corresponds to the point in the middle of the
                                   points that pass.
    """
    data = np.asarray(data).flatten()
    dots = np.asarray(dots)

    if dots.shape[1] != 3:
        raise ValueError("dots must be an N x 3 matrix")

    # First dot
    thresh0, sign0, _ = dots[0]

    # Identify candidates
    # Condition: data[i] * sign > thresh
    mask = (data * sign0) > thresh0

    # Filter candidates with other dots
    for k in range(1, dots.shape[0]):
        thresh, sign, offset = dots[k]
        offset = int(offset)

        # We need to check if data[i + offset] * sign > thresh
        # We create an array corresponding to data[i + offset]

        rolled_data = np.roll(data, -offset)
        check_vals = (rolled_data * sign) > thresh

        # Handle boundary conditions (invalidate wrap-around)
        if offset > 0:
            # Positive offset: we look ahead. i -> i+offset.
            # roll(-offset) shifts left.
            # The last 'offset' elements wrap around from the beginning.
            # So check_vals[-offset:] are invalid.
            check_vals[-offset:] = False
        elif offset < 0:
            # Negative offset: we look behind. i -> i-abs(offset).
            # roll(-offset) shifts right (because -offset is positive).
            # The first 'abs(offset)' elements wrap around from the end.
            # So check_vals[:abs(offset)] are invalid.
            check_vals[:int(abs(offset))] = False

        mask = mask & check_vals
        if not np.any(mask):
            break

    final_indices = np.where(mask)[0]

    if len(final_indices) == 0:
        return np.array([])

    # Group adjacent samples
    diffs = np.diff(final_indices)
    breaks = np.where(diffs > 1)[0]

    event_samples = []
    start_idx = 0

    for brk in breaks:
        group = final_indices[start_idx : brk + 1]
        event_samples.append(np.mean(group))
        start_idx = brk + 1

    group = final_indices[start_idx:]
    event_samples.append(np.mean(group))

    return np.array(event_samples)
