import numpy as np

def fouriercoeffs_tf2(response, tf, samplerate):
    """
    FOURIERCOEFFS_TF  Fourier Transform at a particular frequency.
         ft(response, tf, SAMPLERATE) is the product of response with
         exp( 2*pi*i*tf/SAMPLERATE ). If tf is zero it returns the mean.
         If response is two-dimensional, ft operates on the columns and
         returns a row vector.
         tf is expressed in whatever units SAMPLERATE is expressed in
         (I usually use Hz).
    """

    response = np.array(response)
    # Ensure 2D column vector if 1D array
    if response.ndim == 1:
        response = response.reshape(-1, 1)

    nsamples = response.shape[0]
    duration = nsamples / samplerate

    if tf == 0:
        f = np.mean(response, axis=0)
    else:
        # MATLAB: correctnsamples=floor( SAMPLERATE * floor(duration * tf)/tf );
        # This seems to be a check or truncating to full cycles.
        # But in the MATLAB code provided, `correctnsamples` is calculated but not used explicitly for indexing?
        # Wait, "if correctnsamples == 0, error...".
        # Also MATLAB: expvec=exp(-(1:length(response))*2*pi*sqrt(-1)*tf/SAMPLERATE );
        # Then f=(2/length(response)) * expvec * response(1:length(response),:);
        # So it uses the full response.

        correctnsamples = np.floor(samplerate * np.floor(duration * tf) / tf)
        if correctnsamples == 0:
            raise ValueError('Correctnsamples is zero')

        # 1-based index in MATLAB `1:length(response)` -> 1, 2, ..., nsamples
        indices = np.arange(1, nsamples + 1)
        expvec = np.exp(-indices * 2 * np.pi * 1j * tf / samplerate)

        # expvec is (nsamples,). response is (nsamples, cols).
        # We need dot product: expvec * response
        # In MATLAB: expvec * response. Since expvec is row (1xN), response is (NxM). result is (1xM).

        f = (2 / nsamples) * np.dot(expvec, response)

    if f.size == 1:
        return f.item()
    return f
