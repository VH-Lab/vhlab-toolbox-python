import numpy as np

def spikewaves2pca(waves, N, rng=None):
    """
    Compute first N principal components of spike waveforms.

    FEATURES = spikewaves2pca(WAVES, N, [RANGE])

    Creates a set of "features" of the spike waveform WAVES by
    calculating the values of the first N principal components.

    Inputs:
        waves: A NumSamples x NumChannels x NumSpikes list of spike waveforms.
               (Note: MATLAB doc says list, but code implies array)
               In Python, we expect (NumSamples, NumChannels, NumSpikes)
               Wait, let's verify input shape.
               MATLAB `waves` input shape:
               `waves` is usually defined as samples x channels x spikes in vhlab-toolbox?
               Wait, `centerspikes_neg` took `NxMxD` (Spikes x Samples x Channels).
               `spikewaves2pca` doc says: `NumSamples x NumChannels x NumSpikes`.
               And code: `waves = reshape(waves,size(waves,1)*size(waves,2),size(waves,3))';`
               If input is S x C x K.
               reshape -> (S*C) x K.
               transpose -> K x (S*C).
               This confirms input is (Samples, Channels, Spikes).

               However, `centerspikes_neg` was N x M x D (Spikes x Samples x Channels).
               This inconsistency is typical in MATLAB codebases over time.
               I should stick to what the function expects.

        N:  the number of principal components to include
        rng: (optional) A 2 element vector with the START and STOP range to examine (1-based indices).

    Outputs:
        features: An N x NumSpikes list of features.
    """
    waves = np.array(waves)

    # MATLAB: if nargin>2, waves = waves(range(1):range(2),:,:); end;
    if rng is not None:
        # rng is 1-based [start, stop] inclusive
        start = int(rng[0]) - 1
        stop = int(rng[1])
        waves = waves[start:stop, :, :]

    # MATLAB: waves = reshape(waves,size(waves,1)*size(waves,2),size(waves,3))';
    # Input waves: S x C x K
    # Reshape to (S*C) x K.
    # We need to be careful with reshape order.
    # MATLAB reshape is column-major.
    # waves(S, C, K).
    # reshape(waves, S*C, K).
    # It iterates through S, then C.
    # So for each spike k, the vector is [w(1,1,k), w(2,1,k), ..., w(S,1,k), w(1,2,k), ...].
    # Python reshape is row-major (C-style) by default.
    # But if we want to match MATLAB reshape on a numpy array, we might need 'F' order.
    # However, since we just want to flatten the first two dimensions, let's see.
    # If we have (S, C, K), we want to flatten S and C.
    # In MATLAB, `waves(:, :, k)` is S x C.
    # Reshaping to S*C column vector stacks columns of S x C.
    # So it stacks channel 1, then channel 2, etc.
    # Python `waves[:, :, k].flatten('F')` would do this.
    # Or `waves.reshape(S*C, K, order='F')`.

    S, C, K = waves.shape

    # Flatten first two dimensions into one, preserving column-major order for those two?
    # Actually, we want a matrix where rows are observations (spikes) and columns are features (time*channels).
    # MATLAB: `waves` becomes K x (S*C).
    # Transpose of `reshape(waves, S*C, K)`.
    # `reshape` produces (S*C) x K.
    # So `waves'` is K x (S*C).

    # In Python:
    # We want to transform (S, C, K) to (K, S*C).
    # We can transpose first to (K, C, S) or (K, S, C)?
    # We need to match the feature vector layout.
    # MATLAB feature vector: [Ch1_S1, Ch1_S2, ..., Ch1_SS, Ch2_S1, ...].
    # Wait, MATLAB reshape is column-major.
    # S x C matrix.
    # Column 1 is Ch1. Column 2 is Ch2.
    # Reshape stacks columns.
    # So [Ch1_S1, Ch1_S2, ..., Ch1_SS, Ch2_S1, ..., Ch2_SS].
    # So features are grouped by channel.

    # Python `waves` (S, C, K).
    # Transpose to (K, C, S).
    # Then reshape to (K, C*S).
    # If we reshape (K, C, S) to (K, C*S), the last dimension varies fastest.
    # So we get [Ch1_S1, Ch1_S2, ..., Ch1_SS, Ch2_S1, ...].
    # This matches MATLAB.

    waves_reshaped = waves.transpose(2, 1, 0).reshape(K, C * S)

    # PCA
    # [coeff, features] = princomp(waves)
    # princomp centers the data (subtracts mean).
    # Returns coeff (eigenvectors), features (scores).
    # Scores = (X - mu) * coeff.

    # We can use SVD on centered data.
    # X centered = U S V^T.
    # Scores = U S.

    # Center the data
    mean_vec = np.mean(waves_reshaped, axis=0)
    X_centered = waves_reshaped - mean_vec

    # SVD
    # numpy.linalg.svd returns u, s, vh
    # X = u @ diag(s) @ vh
    # We need full_matrices=False usually for efficiency.
    u, s, vh = np.linalg.svd(X_centered, full_matrices=False)

    # Scores
    scores = u @ np.diag(s)

    # Take first N components
    # MATLAB: features = features(:,1:N)';
    # Transposes result to N x K.

    if N > scores.shape[1]:
        # Handle case where requested N is more than available components
        # Pad with zeros? Or just return what we have?
        # MATLAB princomp returns min(n-1, p) components.
        # If N > available, it will error in MATLAB `features(:,1:N)` unless N <= size.
        # I'll assume N is valid.
        pass

    features = scores[:, :N].T

    return features
