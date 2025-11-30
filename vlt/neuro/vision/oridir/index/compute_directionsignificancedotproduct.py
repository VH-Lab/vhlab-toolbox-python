import numpy as np
from scipy.stats import ttest_1samp

def compute_directionsignificancedotproduct(angles, rates):
    """
    COMPUTE_DIRECTIONSIGNIFICANCEDOTPRODUCT Direction tuning significance using dot product with empirical orientation preference

    P = COMPUTE_DIRECTIONSIGNIFIANCEDOTPRODUCT(ANGLES, RATES)

    This function calculates the probability that the "true" direction tuning
    vector of a neuron has non-zero length. It performs this by empirically
    determing the unit orientation vector, and then computing the dot
    product of the direction vector for each trial onto the overall orientation
    vector, and then looking to see if the average is non-zero.

    Inputs:  ANGLES is a vector of direction angles at which the response has
             been measured.
             RATES is the response of the neuron in to each angle; each row
             should contain responses from a different trial.
    Output:  P the probability that the "true" direction tuning vector is
             non-zero.
    """

    angles = np.array(angles).flatten()
    rates = np.array(rates)

    # Ensure rates is (Trials x Angles) or (Angles x Trials)?
    # "each row should contain responses from a different trial" -> (Trials, Angles).
    # MATLAB: `avg_rates = mean(rates,1);` -> Average over trials (rows) -> (1, Angles).

    avg_rates = np.mean(rates, axis=0)

    # Step 1: Find the unit orientation vector in direction space
    # ot_vec = avg_rates*transpose(exp(sqrt(-1)*2*mod(angles*pi/180,pi)));

    angles_rad = angles * np.pi / 180

    # Orientation vector (2 * angle)
    # MATLAB: `mod(angles*pi/180,pi)` is redundant for exp(2*i*theta)?
    # exp(i*2*theta).

    # Dot product: avg_rates (1 x A) * exp(...) (A x 1).
    ot_vec = np.dot(avg_rates, np.exp(1j * 2 * (angles_rad % np.pi)))

    # ot_vec = exp(sqrt(-1)*angle(ot_vec)/2);
    # This divides angle by 2 to map back to direction space angle?
    ot_vec = np.exp(1j * np.angle(ot_vec) / 2)

    # Step 2: compute the direction vectors for each trial
    # dir_vec = rates*transpose(exp(sqrt(-1)*mod(angles*pi/180,2*pi)));
    dir_vec = np.dot(rates, np.exp(1j * (angles_rad % (2 * np.pi))))

    # Step 3: now compute the trial by trial dot products
    # dot_prods = ([real(dir_vec) imag(dir_vec)] * [real(ot_vec) imag(ot_vec)]');
    # This is equivalent to Real(dir_vec * conj(ot_vec))?
    # Dot product of vectors [Re, Im].
    # Re(a)*Re(b) + Im(a)*Im(b).
    # This is exactly Re(a * conj(b)).

    dot_prods = np.real(dir_vec * np.conj(ot_vec))

    # now compute p value
    # [h,p] = ttest(dot_prods);
    # One-sample t-test against 0.

    t_stat, p_val = ttest_1samp(dot_prods, 0)

    return p_val
