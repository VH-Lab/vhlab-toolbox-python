import numpy as np

def otfit_carandini_conv(direct, par, **kwargs):
    """
    vlt.fit.otfit_carandini_conv Converts between real params and fitting params

    [Rsp,Rp,Op,sig,Rn] = vlt.fit.otfit_carandini_conv(direct, par, ...)

    Converts between the real parameters in the carandini fitting
    function and those used by optimization to find the minimum in the error
    function.

    direct: 'TOREAL', 'TOFITTING', 'TOREALFORFIT'

    par: parameter array

    kwargs:
       'widthint', 'spontfixed', 'spontint', 'Rpint', 'Rnint'
    """

    spontfixed = kwargs.get('spontfixed', np.nan)
    widthint = kwargs.get('widthint', np.nan)
    spontint = kwargs.get('spontint', np.nan)
    Rpint = kwargs.get('Rpint', np.nan)
    Rnint = kwargs.get('Rnint', np.nan)

    s = 0
    # if spontfixed is not nan, s = -1

    if direct == 'TOREALFORFIT':
        if np.isnan(spontfixed):
            if np.any(np.isnan(spontint)):
                Rsp = par[0]
            else:
                # Rsp=spontint(1)+diff(spontint)/(1+abs(par(1)));
                # diff(spontint) = spontint[1] - spontint[0]
                Rsp = spontint[0] + (spontint[1] - spontint[0]) / (1 + np.abs(par[0]))
        else:
            Rsp = spontfixed
            s = -1

        if np.any(np.isnan(Rpint)):
            Rp = np.abs(par[1+s])
        else:
            Rp = Rpint[0] + (Rpint[1] - Rpint[0]) / (1 + np.abs(par[1+s]))

        if np.any(np.isnan(Rnint)):
            Rn = np.abs(par[4+s])
        else:
            Rn = Rnint[0] + (Rnint[1] - Rnint[0]) / (1 + np.abs(par[4+s]))

        Op = par[2+s] % 360

        if np.any(np.isnan(widthint)):
            sig = np.abs(par[3+s])
        else:
            sig = widthint[0] + (widthint[1] - widthint[0]) / (1 + np.abs(par[3+s]))

        return Rsp, Rp, Op, sig, Rn

    elif direct == 'TOREAL':
        if np.isnan(spontfixed):
            if np.any(np.isnan(spontint)):
                Rsp = par[0]
            else:
                Rsp = spontint[0] + (spontint[1] - spontint[0]) / (1 + np.abs(par[0]))
        else:
            Rsp = spontfixed
            s = -1

        if np.any(np.isnan(widthint)):
            sig = np.abs(par[3+s])
        else:
            sig = widthint[0] + (widthint[1] - widthint[0]) / (1 + np.abs(par[3+s]))

        if np.any(np.isnan(Rpint)):
            Rp = np.abs(par[1+s])
        else:
            Rp = Rpint[0] + (Rpint[1] - Rpint[0]) / (1 + np.abs(par[1+s]))

        if np.any(np.isnan(Rnint)):
            Rn = np.abs(par[4+s])
        else:
            Rn = Rnint[0] + (Rnint[1] - Rnint[0]) / (1 + np.abs(par[4+s]))

        if Rp > Rn:
            Op = par[2+s] % 360
        else:
            # Swap Rp and Rn and shift Op by 180
            Rp, Rn = Rn, Rp
            Op = (par[2+s] + 180) % 360

        return Rsp, Rp, Op, sig, Rn

    elif direct == 'TOFITTING':
        # Need to implement inverse mapping
        # MATLAB code implements inverse mapping with conditionals for boundaries.

        # NOTE: The MATLAB code has `if par(1)==spontint(1)`. `par` here are fitting parameters?
        # Wait, if `TOFITTING`, `par` is input (real parameters).
        # The MATLAB code seems to assume `par` are real params.

        # Inverse of y = min + diff / (1+|x|).
        # (1+|x|) = diff / (y-min).
        # |x| = diff/(y-min) - 1.
        # x = diff/(y-min) - 1. (assuming x > 0).
        # MATLAB code: `(spontint(2)-par(1))/(par(1)-spontint(1))`.
        # This looks different from inverse of `min + diff/(1+|x|)`.
        # Let's check.
        # y = min + (max-min)/(1+|x|).
        # 1+|x| = (max-min)/(y-min).
        # |x| = (max-min)/(y-min) - 1 = (max-min - (y-min))/(y-min) = (max-y)/(y-min).
        # This matches `(spontint(2)-par(1))/(par(1)-spontint(1))` if max=spontint(2), min=spontint(1), y=par(1).

        params = []

        if np.isnan(spontfixed):
            if np.any(np.isnan(spontint)):
                params.append(par[0])
            else:
                num = spontint[1] - par[0]
                den = par[0] - spontint[0]
                if den == 0: den = 1e-12
                params.append(num/den)
        else:
            s = -1

        # Rp
        if np.any(np.isnan(Rpint)):
            params.append(par[1+s])
        else:
            num = Rpint[1] - par[1+s]
            den = par[1+s] - Rpint[0]
            if den == 0: den = 1e-12
            params.append(num/den)

        # Op
        params.append(par[2+s])

        # sig
        if np.any(np.isnan(widthint)):
            params.append(par[3+s])
        else:
            num = widthint[1] - par[3+s]
            den = par[3+s] - widthint[0]
            if den == 0: den = 1e-12
            params.append(num/den)

        # Rn
        if np.any(np.isnan(Rnint)):
            params.append(par[4+s])
        else:
            num = Rnint[1] - par[4+s]
            den = par[4+s] - Rnint[0]
            if den == 0: den = 1e-12
            params.append(num/den)

        return np.array(params)

    else:
        raise ValueError(f"Unknown direction {direct}")
