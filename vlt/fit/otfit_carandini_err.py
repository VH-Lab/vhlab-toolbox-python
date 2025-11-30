import numpy as np
from .otfit_carandini_conv import otfit_carandini_conv

def angdiff(ang):
    """
    Computes angular difference in degrees, result in [-180, 180).
    """
    # Using vlt.math.angdiff if it existed, but it's not ported yet.
    # Implementation: ((ang + 180) % 360) - 180
    return ((ang + 180) % 360) - 180

def otfit_carandini_err(par, angles, **kwargs):
    """
    vlt.fit.otfit_carandini_err Computes error of Carandini/Ferster orientation fit

    [ERR, RFIT] = otfit_carandini_err(par, angles, ...)
    """

    data = kwargs.get('data', np.nan)
    stddev = kwargs.get('stddev', None)
    needconvert = kwargs.get('needconvert', 0)
    spontfixed = kwargs.get('spontfixed', np.nan)

    # If data is provided, ensure consistent shape
    if not np.all(np.isnan(data)):
        if stddev is None:
            stddev = np.ones(data.shape)
        else:
            # Replicate stddev if needed?
            # MATLAB: stddev = repmat(stddev,size(data,1),1);
            # Assuming stddev is for angles?
            # If data is (Trials x Angles), stddev should broadcast.
            pass

    err = 0

    if needconvert:
        Rsp, Rp, Op, sig, Rn = otfit_carandini_conv('TOREALFORFIT', par, **kwargs)
    else:
        if np.isnan(spontfixed):
            Rsp, Rp, Op, sig, Rn = par[0], par[1], par[2], par[3], par[4]
        else:
            Rsp = spontfixed
            Rp, Op, sig, Rn = par[0], par[1], par[2], par[3]

    # Calculate Rfit
    # MATLAB uses vlt.math.angdiff

    # Rfit = Rsp+Rp*exp(-vlt.math.angdiff(Op-angles).^2/(2*sig^2))+Rn*exp(-vlt.math.angdiff(180+Op-angles).^2/(2*sig^2));

    diff1 = angdiff(Op - angles)
    diff2 = angdiff(180 + Op - angles)

    # Avoid division by zero if sig is 0
    if sig == 0: sig = 1e-12

    Rfit = Rsp + Rp * np.exp(-(diff1**2) / (2 * sig**2)) + Rn * np.exp(-(diff2**2) / (2 * sig**2))

    if not np.all(np.isnan(data)):
        # d = (data-repmat(Rfit,size(data,1),1))./stddev;
        # Python broadcasting handles repmat
        d = (data - Rfit) / stddev
        err = np.sum(d**2)

    return err, Rfit
