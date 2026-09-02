import numpy as np
from vlt.stats.hotellingt2test import hotellingt2test
from vlt.neuro.vision.oridir.index.compute_circularvariance import compute_circularvariance
from vlt.neuro.vision.oridir.index.compute_orientationindex import compute_orientationindex
from vlt.neuro.vision.oridir.index.compute_tuningwidth import compute_tuningwidth
from vlt.neuro.vision.oridir.index.compute_dircircularvariance import compute_dircircularvariance
from vlt.neuro.vision.oridir.index.compute_directionindex import compute_directionindex
from vlt.neuro.vision.oridir.index.compute_directionsignificancedotproduct import compute_directionsignificancedotproduct

def oridir_vectorindexes(respstruct):
    """
    ORIDIR_VECTORINDEX - compute orientation/direction vector indexes

    VI = vlt.neuro.vision.oridir.index.oridir_vectorindexes(RESPSTRUCT)

    Computes orientation/direction index vector values from a response structure RESP.

    RESPSTRUCT is a dictionary of response properties with fields:
    Field    | Description
    -----------------------------------------------------------------------------
    curve    |    4xnumber of directions tested,
             |      curve[0,:] is directions tested (degrees, compass coords.)
             |      curve[1,:] is mean responses
             |      curve[2,:] is standard deviation
             |      curve[3,:] is standard error
    ind      |    list of individual trial responses for each direction (list of arrays)

    Returns a dictionary VI with fields:
    ot_HotellingT2_p                |   Hotelling's T^2 test of orientation vector data
    ot_pref                         |   Angle preference in orientation space
    ot_circularvariance             |   Magnitude of response in orientation space
    ot_index                        |   Orientation index ( (pref-orth)/pref) )
    tuning_width                    |   Vector tuning width
    dir_HotellingT2_p               |   Hotelling's T^2 test of direction vector data
    dir_pref                        |   Angle preference in direction space
    dir_circularvariance            |   Direction index in vector space
    dir_dotproduct_sig_p            |   P value of dot product direction vector significance
    """

    vi = {
        'ot_HotellingT2_p': np.nan,
        'ot_pref': np.nan,
        'ot_circularvariance': np.nan,
        'ot_index': np.nan,
        'tuning_width': np.nan,
        'dir_HotellingT2_p': np.nan,
        'dir_pref': np.nan,
        'dir_circularvariance': np.nan,
        'dir_dotproduct_sig_p': np.nan
    }

    resp = respstruct['curve']
    angles = resp[0, :]
    mean_resp = resp[1, :]

    hasdirection = False

    if np.max(angles) <= 180:
        tuneangles = np.concatenate([angles, angles + 180])
        tuneresps = np.concatenate([mean_resp, mean_resp])
    else:
        hasdirection = True
        tuneangles = angles
        tuneresps = mean_resp

    # Get all responses aligned
    # ind list contains responses for each direction.
    # We need to truncate to smallest n to form a matrix for hotelling?

    ind_list = respstruct.get('ind', [])
    smallest_n = float('inf')

    for trials in ind_list:
        if trials is not None:
             # trials might be nan padded or contain nans
             valid_trials = np.array(trials)[~np.isnan(trials)]
             smallest_n = min(smallest_n, len(valid_trials))

    if smallest_n == float('inf'):
        smallest_n = 0

    allresps = []

    if smallest_n > 0:
        for trials in ind_list:
            if trials is not None:
                valid_trials = np.array(trials)[~np.isnan(trials)]
                allresps.append(valid_trials[:int(smallest_n)])

        allresps = np.array(allresps).T # (Trials x Angles)

        if allresps.size > 0:
            # Orientation space
            # vecresp_ot = (allresps*transpose(exp(sqrt(-1)*2*mod(angles*pi/180,pi))));
            angles_rad = angles * np.pi / 180
            vecresp_ot = np.dot(allresps, np.exp(1j * 2 * (angles_rad % np.pi)))

            # Hotelling T2 on real/imag parts against [0, 0]
            X = np.column_stack((np.real(vecresp_ot), np.imag(vecresp_ot)))
            h2, vi['ot_HotellingT2_p'] = hotellingt2test(X, [0, 0])

            vi['ot_pref'] = (180 / np.pi * np.angle(np.mean(vecresp_ot))) % 180

            if hasdirection:
                # Direction space
                vecresp_dir = np.dot(allresps, np.exp(1j * (angles_rad % (2 * np.pi))))

                X_dir = np.column_stack((np.real(vecresp_dir), np.imag(vecresp_dir)))
                h3, vi['dir_HotellingT2_p'] = hotellingt2test(X_dir, [0, 0])

                vi['dir_pref'] = (180 / np.pi * np.angle(np.mean(vecresp_dir))) % 360

                vi['dir_dotproduct_sig_p'] = compute_directionsignificancedotproduct(angles, allresps)

    vi['ot_circularvariance'] = compute_circularvariance(tuneangles, tuneresps)
    vi['ot_index'] = compute_orientationindex(tuneangles, tuneresps)
    vi['tuning_width'] = compute_tuningwidth(tuneangles, tuneresps)

    if hasdirection:
        vi['dir_circularvariance'] = compute_dircircularvariance(tuneangles, tuneresps)
        vi['dir_index'] = compute_directionindex(angles, mean_resp)

    return vi
