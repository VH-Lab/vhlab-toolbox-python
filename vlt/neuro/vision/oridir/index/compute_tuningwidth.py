import numpy as np
from scipy.interpolate import interp1d

def compute_tuningwidth(angles, rates):
    """
    vlt.neuro.vision.oridir.index.compute_tuningwidth
    TUNINGWIDTH = vlt.neuro.vision.oridir.index.compute_tuningwidth( ANGLES, RATES )

    Takes ANGLES in degrees

    linearly interpolates rates
    and returns the half of the distance
    between the two points sandwiching the maximum
    where the response is 1/sqrt(2) of the maximum rate.
    returns 90, when function does not come below the point
    """

    angles = np.array(angles).flatten()
    rates = np.array(rates).flatten()

    # angles = [angles 360+angles 720];
    # rates = [rates rates rates(1)];
    # But angles are not necessarily 0..360?
    # Assuming angles are 0..360 or similar.
    # MATLAB code assumes they can be concatenated like this.
    # It probably assumes `angles` is e.g. 0:45:315.

    # We need to ensure we cover the circle.

    # Check if last angle is 360 or close to 0?
    # Usually tuning curves are 0 to 360.

    # Extended angles
    ext_angles = np.concatenate([angles, angles + 360, [720]])
    ext_rates = np.concatenate([rates, rates, [rates[0]]])

    fineangles = np.arange(0, 721, 1)

    # intrates=interp1(angles,rates,fineangles,'linear');
    f = interp1d(ext_angles, ext_rates, kind='linear', fill_value='extrapolate')
    intrates = f(fineangles)

    # [maxrate,pref]=max(intrates(181:540));
    # MATLAB 1-based indexing: 181:540 means indices 181 to 540 inclusive.
    # Python 0-based: 180:540 (since 540 is excluded). Length 360.
    # 180 corresponds to angle 180.

    # MATLAB: intrates is vector corresponding to fineangles 0, 1, ..., 720.
    # intrates(1) is angle 0. intrates(181) is angle 180.
    # indices 181:540 correspond to angles 180 to 539.

    sub_intrates = intrates[180:540]
    maxrate = np.max(sub_intrates)
    pref_idx = np.argmax(sub_intrates) # index relative to 180

    # pref=pref+179; % In MATLAB, pref is index in subwindow. +179 to get index in intrates.
    # In Python, pref_idx is 0-based.
    # Index in intrates = pref_idx + 180.
    pref = pref_idx + 180

    halfheight = maxrate / np.sqrt(2)

    if np.min(intrates - halfheight) > 0:
        return 90
    else:
        # [left,leftvalue]=vlt.data.findclosest(intrates(pref-90:pref),halfheight);
        # MATLAB indices: pref-90 to pref.
        # Python slice: pref-90 : pref+1 (to include pref).
        # But we need to handle boundaries.

        start_idx = max(0, pref - 90)
        end_idx = pref + 1
        window_left = intrates[start_idx:end_idx]

        # findclosest returns index relative to window.
        # We need closest value to halfheight.

        diffs = np.abs(window_left - halfheight)
        left_rel_idx = np.argmin(diffs)

        # left=left+pref-90-2;
        # MATLAB logic: `left` is 1-based index in window.
        # absolute index = (pref-90) + left - 1.
        # `left` variable in MATLAB code is adjusted by `-2`?
        # `left=left+pref-90-2;`
        # Why -2?
        # Maybe `findclosest` returns index starting at 1.
        # `intrates` indices map to angles directly? `fineangles` 0:1:720.
        # Index 1 is angle 0. Index N is angle N-1.
        # So Angle = Index - 1.
        # Angle_left = (left_rel_idx + 1) + (pref - 90) - 1 - ?
        # MATLAB: `left` (index in window)
        # Window starts at index `pref-90`.
        # Absolute index = `pref-90 + left - 1`.
        # Angle = Absolute index - 1.
        # = `pref - 90 + left - 2`.
        # Matches MATLAB code `left+pref-90-2`.

        # In Python:
        # Absolute index = `start_idx + left_rel_idx`.
        # Angle = Absolute index (since index 0 is angle 0).
        # But `pref` is index.
        # Python Angle = `start_idx + left_rel_idx`.

        left_angle = start_idx + left_rel_idx

        # Right side
        # [right,rightvalue]=vlt.data.findclosest(intrates(pref:pref+90),halfheight);
        # MATLAB indices: pref to pref+90.
        start_right = pref
        end_right = min(len(intrates), pref + 91)
        window_right = intrates[start_right:end_right]

        diffs_right = np.abs(window_right - halfheight)
        right_rel_idx = np.argmin(diffs_right)

        # right=right+pref-2;
        # Absolute index = pref + right - 1.
        # Angle = Absolute index - 1 = pref + right - 2.

        # Python:
        right_angle = start_right + right_rel_idx

        tuningwidth = (right_angle - left_angle) / 2.0

        if tuningwidth > 90:
            tuningwidth = 90

        return tuningwidth
