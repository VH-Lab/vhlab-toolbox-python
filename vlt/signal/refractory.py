import numpy as np

def refractory(in_times, refractory_period):
    """
    REFRACTORY - Impose a refractory period on events

    out_times, out_indexes = refractory(in_times, refractory_period)

    This function will remove events from the vector in_times that occur
    more frequently than refractory_period.

    in_times should contain the times of events (in any units, whether they be
    units of time or sample numbers).

    refractory_period is the time after one event when another event cannot
    be said to happen. Any events occuring within refractory_period of a
    previous event will be removed.

    out_times are the times that meet the refractory criteria. out_indexes
    are the index values of the points in in_times that meet the criteria,
    such that out_times = in_times[out_indexes]

    Note: The returned indexes are 0-based, unlike MATLAB's 1-based indexing.
    However, if strict MATLAB compatibility for indices is required, this should
    be noted. Usually, Python returns 0-based indices.
    """

    in_times = np.asarray(in_times)

    if in_times.size == 0:
        return np.array([]), np.array([], dtype=int)

    # Sort in_times and keep track of original indices
    first_rearrange = np.argsort(in_times)
    sorted_times = in_times[first_rearrange]

    # We work on sorted_times
    # out_index tracks indices into sorted_times (which map to first_rearrange)

    # Simple iterative approach is often easiest for refractory logic
    # But to be fast, we can try vectorization or just loop efficiently.
    # MATLAB implementation uses a while loop with diff.

    # MATLAB Algo:
    # 1. Sort
    # 2. compute diff(out_times)
    # 3. find indices where diff <= refractory_period.
    # 4. Remove those.
    # 5. Repeat until no diff <= refractory_period.

    # This greedy removal might remove points that shouldn't be removed?
    # Example: [0, 0.9, 1.8], ref=1.
    # diff: [0.9, 0.9]. Both <= 1.
    # MATLAB removes the *second* of the pair?
    # inds = [1; 1+find(d > ref)]. Keeps the first one always.
    # So it keeps 0. Then checks 0.9 (removed). 1.8?
    # If 0.9 is removed, next diff is between 0 and 1.8 = 1.8. > 1. OK.
    # So [0, 1.8] remains.

    # Let's implement the iterative approach as in MATLAB.

    current_times = sorted_times
    current_indices = np.arange(len(sorted_times)) # Indices into sorted_times

    done = False
    if len(current_times) == 0:
        done = True

    while not done:
        if len(current_times) <= 1:
            break

        d = np.diff(current_times)
        # We keep the first element (index 0) always.
        # Then we keep elements where d > refractory_period.
        # But wait, if we remove element i, the diff changes for i+1.
        # MATLAB does it in rounds.

        # MATLAB: inds = [1; 1+find(d(:)>refractory_period)];
        # This means: keep index 1 (MATLAB). And keep index k+1 if d(k) > ref.
        # d(k) = times(k+1) - times(k).
        # If d(k) <= ref, times(k+1) is too close to times(k).
        # So we drop k+1.

        # This round-based approach removes conflicts with *current* neighbors.

        keep_mask = np.ones(len(current_times), dtype=bool)
        # We assume first is kept.
        # diffs: [d0, d1, d2...] corresponding to (1-0), (2-1), ...
        # If d0 <= ref, we drop element 1.

        valid_diff_indices = np.where(d > refractory_period)[0]
        # valid_diff_indices correspond to index k where times[k+1] - times[k] > ref.
        # So we keep k+1.

        # So we keep index 0, and indices k+1 where d[k] > ref.

        indices_to_keep = [0] + (valid_diff_indices + 1).tolist()
        indices_to_keep = np.unique(indices_to_keep) # Should be sorted and unique already

        if len(indices_to_keep) == len(current_times):
            done = True
        else:
            current_times = current_times[indices_to_keep]
            current_indices = current_indices[indices_to_keep]

    out_times = current_times
    # current_indices maps back to sorted_times.
    # We need to map back to original in_times.
    out_indexes = first_rearrange[current_indices]

    return out_times, out_indexes
