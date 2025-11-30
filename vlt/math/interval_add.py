import numpy as np

def interval_add(i_in, i_add):
    """
    Add intervals.

    Args:
        i_in (numpy.ndarray): Matrix of intervals [T1_0 T1_1; T2_0 T2_1 ...].
                              Shape (N, 2). Can be empty.
                              Sorted by start time.
        i_add (list or numpy.ndarray): Interval to add [S0 S1].

    Returns:
        numpy.ndarray: New matrix of intervals.
    """

    # Handle empty inputs
    if i_in is None or len(i_in) == 0:
        return np.array([i_add], dtype=float) if i_add is not None else np.empty((0,2))

    if i_add is None or len(i_add) == 0:
        return i_in

    i_in = np.array(i_in)
    i_add = np.array(i_add).flatten()

    if len(i_add) != 2:
        raise ValueError('The interval to add must be a 2-element vector.')

    # Check validity of i_in
    if np.any(i_in[:, 1] - i_in[:, 0] <= 0):
        raise ValueError('In all intervals ti_0 must be less than ti_1')

    if len(i_in) > 1:
        if np.any(i_in[1:, 0] - i_in[:-1, 1] <= 0):
            raise ValueError('In all input intervals I_IN, ti_1 must be greater than than t(i-1)_2')

    s0 = i_add[0]
    s1 = i_add[1]

    if s1 - s0 <= 0:
        raise ValueError('S0 must be less than S1')

    # s0_inside = (s0 >= i_in(:,1)) & (s0 < i_in(:,2));
    # s1_inside = (s1 >= i_in(:,1)) & (s1 < i_in(:,2));
    # Note: MATLAB indices 1=start, 2=end. Python 0=start, 1=end.

    s0_inside = (s0 >= i_in[:, 0]) & (s0 < i_in[:, 1])
    s1_inside = (s1 >= i_in[:, 0]) & (s1 < i_in[:, 1])

    s0_less_and_s1_greater = (s0 < i_in[:, 0]) & (s1 > i_in[:, 1])
    # s0_less_and_s1_inside = (s0 < i_in(:,1) & s1_inside); # Redundant in MATLAB code logic?

    i_out = []
    did_something = -1 # -1 means nothing done

    for i in range(len(i_in)):
        out_here = i_in[i].tolist()

        if s0_inside[i]:
            if s1_inside[i]:
                # Inside, do nothing
                did_something = i
            else:
                # Extend to s1
                out_here = [i_in[i, 0], s1]
                did_something = i
        elif s1_inside[i]:
            # s0 was not inside (implied by elseif order), s1 inside
            # Extend start to s0
            out_here = [s0, i_in[i, 1]]
            did_something = i
        elif s0_less_and_s1_greater[i]:
            # Envelops the interval
            out_here = [s0, s1]
            did_something = i
        else:
            # Leave alone
            pass

        i_out.append(out_here)

    i_out = np.array(i_out)

    if did_something == -1:
        # Need to add this interval and sort
        i_out = np.vstack((i_out, [s0, s1]))
        # Sort by start time
        idx = np.argsort(i_out[:, 0])
        i_out = i_out[idx]
        # find where we inserted it
        # MATLAB: did_something = indexes(end);
        # Wait, MATLAB sorts and takes the index of the newly added one?
        # In MATLAB: i_out = [i_out; s0 s1]; [dummy, indexes] = sort(i_out(:,1));
        # The new element was at end. `indexes` maps new pos to old pos.
        # So we need to find where the last element went.
        # Or simply, did_something is the index where the new interval is now.
        # But MATLAB code uses `did_something` to check for overlaps with PREVIOUS interval.
        # `if did_something>1` (1-based).

        # In Python, finding where the new interval ended up is easier if we just search or track.
        # But wait, the logic below handles merging.

        # Re-implement merge logic carefully.
        # "if did_something==0" (MATLAB)
        # We used -1.

        # We need to know the index `did_something` where the modified/inserted interval is.
        # If we inserted and sorted, we need to find it.
        # It's the one with s0, s1? Maybe not unique if s0,s1 duplicates exist?
        # But intervals are disjoint in i_in. And we just added one.

        # Actually, if we just inserted [s0, s1], and sorted.
        # We might have inserted it such that it overlaps with neighbours?
        # The logic below:
        # if did_something>1: check overlap with did_something-1.

        # If we sorted, we need to find which index corresponds to our added interval.
        # It is the one that starts at s0? Yes, unless another one starts at s0 (which is invalid for disjoint strict inequalities? No, T(i)_0 > T(i-1)_0 implies strict).
        # So s0 is unique start time?
        # Not necessarily, s0 could be equal to existing start time?
        # If s0 == existing start time, then s0_inside would be false (s0 >= start is true, s0 < end).
        # Wait, if s0 == start, s0_inside is True.
        # So we would have hit the loop logic.
        # So `did_something` would not be -1.

        # So if `did_something` is -1, it means s0 is not in any interval range, AND s1 is not.
        # AND s0 < start & s1 > end is false for all.
        # This implies [s0, s1] is strictly between intervals or before/after all.
        # So s0 is distinct from all start times.

        # So we can find index where start == s0.

        # Let's find index in `i_out` where `i_out[k] == [s0, s1]`.
        # Since we sorted, we can just look for it.
        # Or better, we can just iterate again to merge overlaps.
        # But the function tries to be efficient.

        # Let's find the index `k` where `i_out[k,0] == s0`.
        k = np.where(i_out[:, 0] == s0)[0][0]
        did_something = k

    # Check for overlapping intervals
    # MATLAB: if did_something>1 (1-based) -> >0 (0-based)
    # Checks overlap with previous.

    # We also need to check overlap with next?
    # The loop handled updating intervals.
    # If we modified an interval (extended it), it might now overlap with the NEXT one.
    # The MATLAB code:
    # `if did_something>1` ... check `i_out(did_something-1,2)>=i_out(did_something,1)`.
    # Merges with previous if needed.

    # Does it check next?
    # MATLAB code doesn't seem to check next?
    # `i_out(did_something-1,2) = i_out(did_something,2); i_out(did_something,:) = [];`
    # This merges current into previous if they overlap.

    # What if we extended to the right and hit the next one?
    # Example: [0 2], [4 6]. Add [2 5].
    # i=0: [0 2]. s0=2 not inside (2<2 False).
    # i=1: [4 6]. s0=2 < 4. s1=5 inside. -> [2 6].
    # i_out = [ [0 2], [2 6] ].
    # did_something = 1.
    # did_something > 0.
    # Check previous: i_out[0, 1] (2) >= i_out[1, 0] (2).
    # Overlap!
    # Merge: i_out[0, 1] = i_out[1, 1] (6).
    # i_out[0] becomes [0 6].
    # Delete i_out[1].
    # Result: [0 6]. Correct.

    # What if we span multiple intervals?
    # [0 2], [4 6], [8 10]. Add [1 9].
    # i=0: [0 2]. s0=1 inside. s1=9 outside. Extend -> [0 9].
    # i=1: [4 6]. s0=1 < 4. s1=9 > 6. Envelop -> [1 9]. Wait.
    #   Logic: s0_inside is False for i=1. s1_inside False (9 not < 6). s0_less_and_s1_greater True.
    #   Replaces [4 6] with [1 9].
    # i=2: [8 10]. s0=1 < 8. s1=9 inside. Extend -> [1 10].
    # Result list: [ [0 9], [1 9], [1 10] ].
    # This looks broken?
    # The loop replaces each interval independently based on s0, s1.
    # Then `did_something` is just the last one?
    # The MATLAB code uses `did_something` variable, which gets overwritten.
    # So `did_something` holds the index of the LAST modified interval.
    # In the example above:
    # i=0: did_something=1. i_out(1)=[0 9].
    # i=1: did_something=2. i_out(2)=[1 9].
    # i=2: did_something=3. i_out(3)=[1 10].
    # Then `did_something`=3.
    # Check overlap with 2: i_out(2,2)=9 >= i_out(3,1)=1. Merge.
    # i_out(2) becomes [1 10]. i_out(3) removed.
    # Now we have [ [0 9], [1 10] ].
    # We still have overlap between 1 and 2!
    # The code only checks ONCE.
    # Does the MATLAB code handle multi-interval merges?
    # The code looks simplistic. "let's start out assuming we can operate on the intervals in order; we probably can".
    # And "we need to check to make sure that we didn't create overlapping intervals".
    # It only checks `did_something-1`.
    # It assumes we only touch one spot?
    # If s0, s1 spans multiple intervals, `interval_add` might produce messy output if the intervals are not consumed.
    # But wait, `s0_inside` etc. are computed upfront.
    # If s0=1, s1=9.
    # i=0 ([0 2]): s0 inside. -> [0 9].
    # i=1 ([4 6]): s0 < 4, s1 > 6. -> [1 9]. (Note: s0 is 1).
    # i=2 ([8 10]): s1 inside. -> [1 10].

    # The output is indeed [ [0 9], [1 9], [1 10] ].
    # The cleanup only merges the last two.
    # Result: [ [0 9], [1 10] ].
    # This is invalid (overlapping).
    # So the MATLAB function might be buggy for complex cases, or assumes standard usage where you add small intervals.
    # Or maybe I misunderstood "we assume we can operate on intervals in order".

    # However, I must PORT the function, bugs and all, unless it's obviously wrong and I can fix it while keeping intent.
    # But usually "Porting" means replicating logic.
    # If the MATLAB code is buggy, my python code should be too?
    # Or should I improve it?
    # Given the instructions, I should probably stick to the logic.
    # BUT, if I write a test case that fails because of this logic, I'll be confused.
    # I should write tests that cover simple cases first.

    # Let's implement exactly as MATLAB.

    if did_something > 0: # 0-based index > 0 means at least index 1 (second element)
        prev = did_something - 1
        curr = did_something
        if i_out[prev, 1] >= i_out[curr, 0]:
            # Merge
            # i_out(did_something-1,2) = i_out(did_something,2);
            i_out[prev, 1] = i_out[curr, 1]
            # i_out(did_something,:) = [];
            i_out = np.delete(i_out, curr, axis=0)

    return i_out
