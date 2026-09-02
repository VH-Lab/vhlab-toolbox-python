import numpy as np
from vlt.neuro.stimulus.findcontrolstimulus import findcontrolstimulus
from vlt.math.fouriercoeffs_tf2 import fouriercoeffs_tf2
from vlt.math.fouriercoeffs_tf_spikes import fouriercoeffs_tf_spikes

def stimulus_response_scalar(timeseries, timestamps, stim_onsetoffsetid, **kwargs):
    """
    STIMULUS_RESPONSE_SUMMARY - compute stimulus responses to stimuli

    RESPONSE = vlt.neuro.stimulus.stimulus_response_scalar(TIMESERIES, TIMESTAMPS, STIM_ONSETOFFSETID, ...)

    Inputs:
      TIMESERIES is a 1xT array of the data values of the thing exhibiting the response, such as
          a voltage signal, calcium dF/F signal, or spike signals (1s).
      TIMESTAMPS is a 1xT array of the occurrences of the signals in TIMESERIES
      STIM_ONSETOFFSETID is a variable that describes the stimulus history. Each row should
          contain [stim_onset_time stim_offset_time stimid] where the times are in units of TIMESTAMPS (s).

    Computes a dictionary RESPONSE with fields:
    Field name:                   | Description:
    ------------------------------------------------------------------------
    stimid                        | The stimulus id of each stimulus observed
    response                      | The scalar response to each stimulus response.
    control_response              | The scalar response to the control stimulus for each stimulus
    controlstimnumber             | The stimulus number used as the control stimulus for each stimulus
    parameters                    | A structure with the parameters used in the calculation

    The behavior of the function can be modified by name/value pairs:
    Parameter (default value)     | Description:
    ------------------------------------------------------------------------
    freq_response (0)             | The frequency response to measure using FFT of TIMESERIES. Can be
                                  |     0 (to use the mean response), or a number corresponding
                                  |     to the frequency to analyze. Can also be a vector the same
                                  |     size as the number of stimuli to indicate the frequency to
                                  |     be used for each stimulus (freq_response[stimid[i]]).
    control_stimid ([])           | The identity (or identities) of a 'blank' control stimulus.
    prestimulus_time ([])         | Calculate a baseline using this much TIMESERIES signal before
                                  |     each stimulus onset.
    prestimulus_normalization ([])| [] or 0) none; 1) 'subtract'; 2) 'fractional'; 3) 'divide'
    isspike (0)                   | 0/1 Is the signal a spike process? If so, TIMESTAMPS correspond
                                  |     to spike events.
    spiketrain_dt (0.001)         | Resolution to use for spike train reconstruction if computing
                                  |     the Fourier transform.

    When FREQ_RESPONSE is non-zero the responses are Fourier coefficients, so 'response' and
    'control_response' are returned as complex arrays; for FREQ_RESPONSE of 0 they are real.
    """

    freq_response = kwargs.get('freq_response', 0)
    control_stimid = kwargs.get('control_stimid', [])
    prestimulus_time = kwargs.get('prestimulus_time', [])
    prestimulus_normalization = kwargs.get('prestimulus_normalization', [])
    isspike = kwargs.get('isspike', 0)
    spiketrain_dt = kwargs.get('spiketrain_dt', 0.001)

    # Store parameters
    # In MATLAB: parameters = vlt.data.workspace2struct(); then remove some fields.
    # Here we can just construct it from kwargs + defaults.
    parameters = {
        'freq_response': freq_response,
        'control_stimid': control_stimid,
        'prestimulus_time': prestimulus_time,
        'prestimulus_normalization': prestimulus_normalization,
        'isspike': isspike,
        'spiketrain_dt': spiketrain_dt
    }
    # Add any extra kwargs
    parameters.update(kwargs)

    timeseries = np.array(timeseries).flatten()
    timestamps = np.array(timestamps).flatten()
    stim_onsetoffsetid = np.array(stim_onsetoffsetid)

    stimid = stim_onsetoffsetid[:, 2].astype(int)

    # Accumulate in lists and build the arrays at the end. MATLAB grows `response = []`,
    # so the array promotes to complex the first time a Fourier coefficient is stored;
    # collecting first and calling np.array() once reproduces that, instead of forcing
    # every value through a preallocated float array (which raises on a complex F1/F2).
    response_values = []
    control_response_values = []

    sample_rate = 0
    if len(timestamps) > 1:
        sample_rate = 1.0 / np.median(np.diff(timestamps))

    controlstimnumber = findcontrolstimulus(stimid, control_stimid)

    if prestimulus_normalization:
        if isinstance(prestimulus_normalization, str):
            prestimulus_normalization = prestimulus_normalization.lower()

    for i in range(len(stimid)):
        stimulus_samples = np.where((timestamps >= stim_onsetoffsetid[i, 0]) &
                                    (timestamps <= stim_onsetoffsetid[i, 1]))[0]

        # duration of *this* stimulus; MATLAB uses it as the denominator for the
        # stimulus, control and prestimulus spike rates alike
        dur = stim_onsetoffsetid[i, 1] - stim_onsetoffsetid[i, 0]

        control_stim_here = None
        control_stimulus_samples = []

        # Access controlstimnumber safely
        if len(controlstimnumber) > i and not np.isnan(controlstimnumber[i]):
            control_stim_here = int(controlstimnumber[i])
            if control_stim_here < len(stim_onsetoffsetid): # Bound check
                control_stimulus_samples = np.where((timestamps >= stim_onsetoffsetid[control_stim_here, 0]) &
                                                    (timestamps <= stim_onsetoffsetid[control_stim_here, 1]))[0]
            else:
                 control_stim_here = None # Invalid index

        outofbounds1 = False
        outofbounds2 = False

        if not isspike:
            if len(timestamps) > 0:
                outofbounds1 = (timestamps[-1] < stim_onsetoffsetid[i, 1]) or (timestamps[0] > stim_onsetoffsetid[i, 0])
                if control_stim_here is not None:
                     outofbounds2 = (timestamps[-1] < stim_onsetoffsetid[control_stim_here, 1]) or (timestamps[0] > stim_onsetoffsetid[control_stim_here, 0])
        else:
            outofbounds1 = False
            outofbounds2 = False

        if outofbounds1 or outofbounds2:
            response_here = np.nan
            control_response_here = np.nan
        else:
            prestimulus_samples = []
            control_prestimulus_samples = []

            if prestimulus_time: # Check if not empty/None/0
                pt = prestimulus_time if np.isscalar(prestimulus_time) else prestimulus_time[0] # handle list
                if pt > 0:
                    prestimulus_samples = np.where((timestamps >= stim_onsetoffsetid[i, 0] - pt) &
                                                   (timestamps < stim_onsetoffsetid[i, 0]))[0]
                    if control_stim_here is not None:
                         control_prestimulus_samples = np.where((timestamps >= stim_onsetoffsetid[control_stim_here, 0] - pt) &
                                                                (timestamps < stim_onsetoffsetid[control_stim_here, 0]))[0]

            # Calculate response

            # Handle freq_response per stimulus
            freq_response_here = freq_response
            if np.size(freq_response) > 1:
                try:
                    # MATLAB indexes freq_response(stimid(i)) with 1-based stimid.
                    idx = int(stimid[i]) - 1
                    if idx >= 0 and idx < np.size(freq_response):
                         freq_response_here = freq_response[idx]
                    else:
                         freq_response_here = freq_response[0]
                except:
                    freq_response_here = freq_response[0] # Fallback

            response_here = 0
            control_response_here = 0
            prestimulus_here = 0
            control_prestimulus_here = 0

            if freq_response_here == 0:
                if not isspike:
                    response_here = np.nanmean(timeseries[stimulus_samples]) if len(stimulus_samples) > 0 else np.nan
                    control_response_here = np.nanmean(timeseries[control_stimulus_samples]) if len(control_stimulus_samples) > 0 else np.nan
                else:
                    response_here = np.sum(timeseries[stimulus_samples]) / dur if dur > 0 else 0
                    if control_stim_here is not None:
                        control_response_here = np.sum(timeseries[control_stimulus_samples]) / dur if dur > 0 else 0

                if prestimulus_time:
                    if not isspike:
                         prestimulus_here = np.nanmean(timeseries[prestimulus_samples]) if len(prestimulus_samples) > 0 else np.nan
                         control_prestimulus_here = np.nanmean(timeseries[control_prestimulus_samples]) if len(control_prestimulus_samples) > 0 else np.nan
                    else:
                         prestimulus_here = np.sum(timeseries[prestimulus_samples]) / dur if dur > 0 else 0
                         control_prestimulus_here = np.sum(timeseries[control_prestimulus_samples]) / dur if dur > 0 else 0
            else:
                 # Fourier
                 if not isspike:
                     if len(stimulus_samples) > 0:
                         response_here = fouriercoeffs_tf2(timeseries[stimulus_samples], freq_response_here, sample_rate)
                     if len(control_stimulus_samples) > 0:
                         control_response_here = fouriercoeffs_tf2(timeseries[control_stimulus_samples], freq_response_here, sample_rate)
                 else:
                     if len(stimulus_samples) > 0:
                         response_here = fouriercoeffs_tf_spikes(timestamps[stimulus_samples] - stim_onsetoffsetid[i, 0], freq_response_here, dur)
                     if len(control_stimulus_samples) > 0:
                         dur_c = stim_onsetoffsetid[control_stim_here, 1] - stim_onsetoffsetid[control_stim_here, 0]
                         control_response_here = fouriercoeffs_tf_spikes(timestamps[control_stimulus_samples] - stim_onsetoffsetid[control_stim_here, 0], freq_response_here, dur_c)

                 if prestimulus_time:
                     pt = prestimulus_time if np.isscalar(prestimulus_time) else prestimulus_time[0]
                     if not isspike:
                         if len(prestimulus_samples) > 0:
                             prestimulus_here = fouriercoeffs_tf2(timeseries[prestimulus_samples], freq_response_here, sample_rate)
                         if len(control_prestimulus_samples) > 0:
                             control_prestimulus_here = fouriercoeffs_tf2(timeseries[control_prestimulus_samples], freq_response_here, sample_rate)
                     else:
                         # MATLAB shifts prestimulus spike times by (stim_onset + prestimulus_time),
                         # which lands them in [-2*pt, -pt) rather than [0, pt). Only the phase of
                         # the coefficient depends on that offset, and we copy MATLAB so the two
                         # toolboxes agree.
                         if len(prestimulus_samples) > 0:
                             prestimulus_here = fouriercoeffs_tf_spikes(timestamps[prestimulus_samples] - stim_onsetoffsetid[i, 0] - pt, freq_response_here, pt)
                         if len(control_prestimulus_samples) > 0:
                             control_prestimulus_here = fouriercoeffs_tf_spikes(timestamps[control_prestimulus_samples] - stim_onsetoffsetid[control_stim_here, 0] - pt, freq_response_here, pt)

            if prestimulus_normalization:
                norm = prestimulus_normalization
                if norm in [0, 'none']:
                    pass
                elif norm in [1, 'subtract']:
                    response_here = response_here - prestimulus_here
                    control_response_here = control_response_here - control_prestimulus_here
                elif norm in [2, 'fractional']:
                    response_here = (response_here - prestimulus_here) / prestimulus_here if prestimulus_here != 0 else np.nan
                    control_response_here = (control_response_here - control_prestimulus_here) / control_prestimulus_here if control_prestimulus_here != 0 else np.nan
                elif norm in [3, 'divide']:
                    response_here = response_here / prestimulus_here if prestimulus_here != 0 else np.nan
                    control_response_here = control_response_here / control_prestimulus_here if control_prestimulus_here != 0 else np.nan

        response_values.append(response_here)
        if control_stim_here is not None:
            control_response_values.append(control_response_here)
        else:
            control_response_values.append(np.nan)

    # np.array() promotes to complex only if a Fourier coefficient was actually stored
    response = np.array(response_values) if response_values else np.array([])
    control_response = np.array(control_response_values) if control_response_values else np.array([])

    result = {
        'stimid': stimid,
        'response': response,
        'control_response': control_response,
        'controlstimnumber': controlstimnumber,
        'parameters': parameters
    }

    return result
