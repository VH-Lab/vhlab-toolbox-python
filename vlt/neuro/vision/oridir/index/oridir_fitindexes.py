import numpy as np
import vlt.fit.otfit_carandini as otfit
import vlt.neuro.vision.oridir.index.fit2fitoi as f2foi
import vlt.neuro.vision.oridir.index.fit2fitoidiffsum as f2foids
import vlt.neuro.vision.oridir.index.fit2fitdi as f2fdi
import vlt.neuro.vision.oridir.index.fit2fitdidiffsum as f2fdids
from vlt.math.rectify import rectify
from vlt.data.rowvec import rowvec

def oridir_fitindexes(respstruct):
    """
    ORIDIR_FITINDEXES - compute orientation/direction fits, index values

    FI = vlt.neuro.vision.oridir.index.oridir_fitindexes(RESPSTRUCT)
    """

    fi = {}

    resp = respstruct['curve']
    angles = resp[0, :]
    mean_resp = resp[1, :]
    std_resp = resp[3, :] # curve(4,:) is standard error

    # [maxresp,if0]=max(resp(2,:));
    maxresp = np.max(mean_resp)
    if0 = np.argmax(mean_resp)
    otpref = angles[if0]

    if np.max(angles) <= 180:
        tuneangles = np.concatenate([angles, angles + 180])
        tuneresps = np.concatenate([mean_resp, mean_resp])
        tuneerr = np.concatenate([std_resp, std_resp])
    else:
        tuneangles = angles
        tuneresps = mean_resp
        tuneerr = std_resp

    sorted_angles = np.sort(angles)
    da = np.diff(sorted_angles)
    da = da[0]

    widthseeds = [da/2, da, 40, 60, 90]
    errors = [float('inf')]

    Rsp, Rp, Ot, sigm, Rn, fitcurve, er, R2 = None, None, None, None, None, None, None, None

    for ws in widthseeds:
        Rspt, Rpt, Ott, sigmt, Rnt, fitcurvet, ert, R2t = otfit.otfit_carandini(
            tuneangles, 0, maxresp, otpref, ws,
            widthint=[da/2, 180],
            Rpint=[0, 3*maxresp],
            Rnint=[0, 3*maxresp],
            spontint=[np.min(tuneresps), np.max(tuneresps)],
            data=tuneresps
        )

        if ert < errors[0]:
             Rsp, Rp, Ot, sigm, Rn = Rspt, Rpt, Ott, sigmt, Rnt
             fitcurve = fitcurvet
             er = ert
             R2 = R2t
             errors[0] = ert

    fi['fit_parameters'] = [Rsp, Rp, Ot, sigm, Rn]
    # fi.fit = [0:359; vlt.data.rowvec(fitcurve)];
    fi['fit'] = np.vstack([np.arange(360), rowvec(fitcurve)])

    fi['ot_index'] = f2foi.fit2fitoi(fi['fit'])
    fi['ot_index_rectified'] = min(rectify(fi['ot_index']), 1)
    fi['ot_index_diffsum'] = f2foids.fit2fitoidiffsum(fi['fit'])
    fi['ot_index_diffsum_rectified'] = min(rectify(fi['ot_index_diffsum']), 1)

    fi['dirpref'] = Ot

    fi['dir_index'] = f2fdi.fit2fitdi(fi['fit'])
    fi['dir_index_rectified'] = min(rectify(fi['dir_index']), 1)
    fi['dir_index_diffsum'] = f2fdids.fit2fitdidiffsum(fi['fit'])
    fi['dir_index_diffsum_rectified'] = min(rectify(fi['dir_index_diffsum']), 1)

    fi['tuning_width'] = sigm * np.sqrt(np.log(4))

    return fi
