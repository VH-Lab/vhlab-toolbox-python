import numpy as np
from vlt.data.eqlen import eqlen

def stimids2reps(stimids, numstims):
    """
    STIMIDS2REPS - Label each stimulus id with the repetition number for a regular
     stimulus sequence

     [REPS, ISREGULAR] = vlt.neuro.stimulus.stimids2reps(STIMIDS, NUMSTIMS)

     Given a list of STIMIDS that indicate an order of presentation,
     and given that STIMIDS range from 1..NUMSTIMS, vlt.neuro.stimulus.stimids2reps returns a label
     REPS, the same size as STIMIDS, that indicates the repetition
     number if the stimuli were to be presented in a regular order.
     Regular order means that all stimuli 1...NUMSTIMS are shown in some order once,
     followed by 1..NUMSTIMS in some order a second time, etc.

     ISREGULAR is 1 if the sequence of STIMIDS is in a regular order. The last
     repetition need not be complete for the stimulus presentation to be regular
     (that is, if a sequence ended early it can still be regular).

     Example:
        reps, isregular = vlt.neuro.stimulus.stimids2reps([1, 2, 3, 1, 2, 3], 3)
           # reps = [1, 1, 1, 2, 2, 2]
           # isregular = 1
    """

    stimids = np.array(stimids).flatten()
    N_reps = len(stimids) / numstims

    # if 0 & round(N_reps)-N_reps>1e-6:
    #     error... (skipped in MATLAB code by 0 & ...)

    reps = np.ceil(np.arange(1, len(stimids) + 1) / numstims).astype(int)

    R = np.max(reps) if len(reps) > 0 else 0

    isregular = True # look for evidence that contradicts

    for r in range(1, R): # 1 to R-1
        # In MATLAB: sort(stimids(find(reps==r)))
        # reps starts at 1.
        current_reps_indices = np.where(reps == r)[0]
        current_stimids = stimids[current_reps_indices]
        if not eqlen(np.sort(current_stimids), np.arange(1, numstims + 1)):
            isregular = False
            return reps, isregular

    # Last repetition (R)
    if R > 0:
        laststims = stimids[np.where(reps == R)[0]]

        # are all stimid numbers in range?
        in_range = np.all((laststims <= numstims) & (laststims >= 1))
        # does each stimulus presented so far appear at most once?
        unique_check = (len(np.sort(laststims)) == len(np.unique(laststims)))

        if not in_range or not unique_check:
            isregular = False

    return reps, isregular
