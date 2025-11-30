import numpy as np
from scipy.optimize import minimize
from .otfit_carandini_conv import otfit_carandini_conv
from .otfit_carandini_err import otfit_carandini_err

def otfit_carandini(angles, sponthint, maxresphint, otprefhint, widthhint, **kwargs):
    """
    vlt.fit.otfit_carandini Fits orientation curves like Carandini/Ferster 2000

    [Rsp,Rp,Ot,sigm,Rn,fitcurve,er,R2] = vlt.fit.otfit_carandini(angles, sponthint, ...)
    """

    spontfixed = kwargs.get('spontfixed', np.nan)
    data = kwargs.get('data', np.nan)

    Po = np.array([sponthint, maxresphint, otprefhint, widthhint, maxresphint])

    if not np.isnan(spontfixed):
        Po = Po[1:]

    # Convert to fitting parameters
    # [Rsp_,Rp_,Ot_,sigm_,Rn_]=vlt.fit.otfit_carandini_conv('TOFITTING',Po,varargin{:});
    # Warning: MATLAB passes Po as 'par'.
    # `otfit_carandini_conv` takes real params and converts TO fitting params.
    # Po are real hints. So we convert them to fitting space.

    fitting_params = otfit_carandini_conv('TOFITTING', Po, **kwargs)

    # Optimization
    # options= optimset('Display','off','MaxFunEvals',10000,'TolX',1e-6);

    def objective(x):
        e, _ = otfit_carandini_err(x, angles, needconvert=1, **kwargs)
        return e

    res = minimize(objective, fitting_params, method='Nelder-Mead', tol=1e-6, options={'maxfev': 10000})
    Pf = res.x

    # Convert back
    Rsp, Rp, Ot, sigm, Rn = otfit_carandini_conv('TOREAL', Pf, **kwargs)

    # Error
    # if ~isnan(spontfixed), er = vlt.fit.otfit_carandini_err([Rp Ot sigm Rn],angles,varargin{:});
    if not np.isnan(spontfixed):
        er, _ = otfit_carandini_err(np.array([Rp, Ot, sigm, Rn]), angles, spontfixed=spontfixed, **kwargs)
    else:
        er, _ = otfit_carandini_err(np.array([Rsp, Rp, Ot, sigm, Rn]), angles, **kwargs)

    fitcurve = []
    # If nargout > 5
    # Calculate fitcurve 0:359
    # [d,fitcurve]=vlt.fit.otfit_carandini_err(Pf,0:359,varargin{:},'needconvert',1);

    # We always return fitcurve in Python dict or tuple
    fine_angles = np.arange(360)
    # We shouldn't pass 'data' when calculating fitcurve for plotting?
    # MATLAB: removes 'data' from varargin.
    kwargs_nodata = kwargs.copy()
    if 'data' in kwargs_nodata:
        del kwargs_nodata['data']

    _, fitcurve = otfit_carandini_err(Pf, fine_angles, needconvert=1, **kwargs_nodata)

    R2 = np.nan
    if not np.all(np.isnan(data)):
         # R2 = 1 - sum(er)/(sum((data-mean(data)).^2));
         # er is sum of squared errors
         sst = np.sum((data - np.mean(data))**2)
         if sst != 0:
             R2 = 1 - er / sst
         else:
             R2 = 0 # or NaN?

    return Rsp, Rp, Ot, sigm, Rn, fitcurve, er, R2
