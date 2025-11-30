import numpy as np
from vlt.neuro.stimulus.stimids2reps import stimids2reps

def findcontrolstimulus(stimid, controlstimid):
    """
    FINDCONTROLSTIMULUS - find the corresponding 'control' stimulus for a set of stimuli

    CONTROLSTIMNUMBER = vlt.neuro.stimulus.findcontrolstimulus(STIMID, CONTROLSTIMID)

    Given an array of STIMID values that indicate stimulus presentation, and an array of
    CONTROLSTIMID value(s) that indicate the identification number of a 'control' stimulus
    (such as a blank screen), this function finds the control stimulus id that corresponds
    to each STIMID presentation.

    If the stimulus presentation is regular (stimuli are presented from 1...numstims in
    some order, followed by a second presentation of 1...numstims in some order, etc, with only
    a single control stimulus), then the control stimulus for each stimulus is the control
    stimulus that corresponds to the same stimulus repetition.

    If the stimulus presentation is not regular, then the 'closest' control stimulus is taken
    to be the control stimulus; if 2 stimuli are equally close, then the first stimulus will be taken
    as the control stimulus.

    CONTROLSTIMNUMBER will always be returned as a column vector.

    See also: vlt.neuro.stimulus.stimids2reps
    """

    controlstimid = np.array(controlstimid).flatten()
    stimid = np.array(stimid).flatten()

    if len(controlstimid) == 0:
        return np.array([])

    numstims = np.max(stimid)

    reps, isregular = stimids2reps(stimid, numstims)

    controlstimnumber = []

    isregular = (isregular and (len(controlstimid) == 1))

    if isregular:
        R = np.max(reps) if len(reps) > 0 else 0

        for r in range(1, R): # 1 to R-1
            rep_inds = np.where(reps == r)[0]
            stimids_in_rep = stimid[rep_inds]

            idx_in_rep = np.where(stimids_in_rep == controlstimid[0])[0]
            if len(idx_in_rep) > 0:
                control_idx_in_rep = idx_in_rep[0]
                control_idx_global = (r - 1) * numstims + control_idx_in_rep
                controlstimnumber.extend([control_idx_global] * numstims)
            else:
                pass

        # Last rep (R)
        if R > 0:
            rep_inds = np.where(reps == R)[0]
            stimids_in_rep = stimid[rep_inds]
            idx_in_rep = np.where(stimids_in_rep == controlstimid[0])[0]

            if len(idx_in_rep) > 0:
                 control_idx_in_rep = idx_in_rep[0]
                 control_idx_global = (R - 1) * numstims + control_idx_in_rep
                 controlstimnumber.extend([control_idx_global] * numstims)
            else:
                 # Last trial may not be complete.
                 if R > 1:
                     rep_prev_inds = np.where(reps == R - 1)[0]
                     stimids_in_prev_rep = stimid[rep_prev_inds]
                     idx_in_prev_rep = np.where(stimids_in_prev_rep == controlstimid[0])[0]
                     if len(idx_in_prev_rep) > 0:
                         control_idx_prev_in_rep = idx_in_prev_rep[0]
                         control_idx_prev_global = (R - 2) * numstims + control_idx_prev_in_rep
                         controlstimnumber.extend([control_idx_prev_global] * numstims)
    else:
        # Not regular
        cs_inds = np.where(np.isin(stimid, controlstimid))[0]

        if len(cs_inds) == 0:
             return np.array([])

        stimid_indices = np.arange(len(stimid))
        cs_dist_matrix = np.abs(stimid_indices[None, :] - cs_inds[:, None])
        min_indices = np.argmin(cs_dist_matrix, axis=0)
        controlstimnumber = cs_inds[min_indices]

    return np.array(controlstimnumber)
