import numpy as np
from scipy.stats import f, chi2

def hotellingt2test(X, mu, alpha=0.05):
    """
    vlt.stats.hotellingt2test - Hotelling T^2 test for multivariate samples

    [H,P] = vlt.stats.hotellingt2test(X,MU)
    [H,P] = vlt.stats.hotellingt2test(X,MU,ALPHA)

    Performs Hotelling's T^2 test on multivariate samples X to determine
    if the data have mean MU.  X should be a NxP matrix with N observations
    of P-dimensional data, and the mean MU to be tested should be 1xP.
    ALPHA, the significance level, is 0.05 by default.

    H is 1 if the null hypothesis (that the mean of X is equal to MU) can be
    rejected at significance level ALPHA.  P is the actual P value.
    """

    X = np.array(X)
    mu = np.array(mu)

    n, p = X.shape

    m = np.mean(X, axis=0)

    # MATLAB: S = cov(X). NumPy cov expects rowvar=True by default (variables are rows).
    # Here X is NxP (observations in rows). So rowvar=False.
    S = np.cov(X, rowvar=False)

    # T2 = n*(m-mu)*inv(S)*(m-mu)';
    diff = m - mu

    try:
        invS = np.linalg.inv(S)
    except np.linalg.LinAlgError:
        # If singular, can't compute T2. Return NaN or False?
        # For now assume invertible.
        invS = np.linalg.pinv(S)

    T2 = n * diff @ invS @ diff.T

    if n >= 50: # Chi-square approximation
        X2 = T2
        v = p
        # P = 1-chi2cdf(X2,v);
        P = 1 - chi2.cdf(X2, v)
    else: # F approximation
        # F = (n-p)/((n-1)*p)*T2;
        F_stat = (n - p) / ((n - 1) * p) * T2
        v1 = p
        v2 = n - p
        # P = 1-fcdf(F,v1,v2);
        P = 1 - f.cdf(F_stat, v1, v2)

    H = P < alpha
    return H, P
