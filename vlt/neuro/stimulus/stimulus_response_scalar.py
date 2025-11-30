import numpy as np
import vlt.neuro.stimulus.findcontrolstimulus as fcs
import vlt.math.fouriercoeffs_tf2 as ftf2
import vlt.math.fouriercoeffs_tf_spikes as ftfs

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
    response = np.full(len(stimid), np.nan)
    control_response = np.full(len(stimid), np.nan)

    sample_rate = 0
    if len(timestamps) > 1:
        sample_rate = 1.0 / np.median(np.diff(timestamps))

    controlstimnumber = fcs.findcontrolstimulus(stimid, control_stimid)

    if prestimulus_normalization:
        if isinstance(prestimulus_normalization, str):
            prestimulus_normalization = prestimulus_normalization.lower()

    for i in range(len(stimid)):
        stimulus_samples = np.where((timestamps >= stim_onsetoffsetid[i, 0]) &
                                    (timestamps <= stim_onsetoffsetid[i, 1]))[0]

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
                    # stimid[i] is 1-based or 0-based?
                    # In MATLAB usually 1-based. stimids2reps assumed 1..NUMSTIMS.
                    # freq_response(stimid(i)).
                    # If stimid starts at 1, we need stimid[i]-1 for python index.
                    # Or maybe stimid values are arbitrary?
                    # "stimid values may repeat many times".
                    # If freq_response is a vector, it assumes it is indexed by stimid.
                    # I will assume stimid corresponds to index if it's within range.
                    idx = int(stimid[i]) - 1 # Assuming 1-based stimid mapped to 0-based index
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
                    dur = stim_onsetoffsetid[i, 1] - stim_onsetoffsetid[i, 0]
                    response_here = np.sum(timeseries[stimulus_samples]) / dur if dur > 0 else 0
                    if control_stim_here is not None:
                        dur_c = stim_onsetoffsetid[control_stim_here, 1] - stim_onsetoffsetid[control_stim_here, 0]
                        control_response_here = np.sum(timeseries[control_stimulus_samples]) / dur_c if dur_c > 0 else 0

                if prestimulus_time:
                    if not isspike:
                         prestimulus_here = np.nanmean(timeseries[prestimulus_samples]) if len(prestimulus_samples) > 0 else np.nan
                         control_prestimulus_here = np.nanmean(timeseries[control_prestimulus_samples]) if len(control_prestimulus_samples) > 0 else np.nan
                    else:
                         pt = prestimulus_time if np.isscalar(prestimulus_time) else prestimulus_time[0]
                         prestimulus_here = np.sum(timeseries[prestimulus_samples]) / pt if pt > 0 else 0
                         control_prestimulus_here = np.sum(timeseries[control_prestimulus_samples]) / pt if pt > 0 else 0
            else:
                 # Fourier
                 if not isspike:
                     if len(stimulus_samples) > 0:
                         response_here = ftf2.fouriercoeffs_tf2(timeseries[stimulus_samples], freq_response_here, sample_rate)
                     if len(control_stimulus_samples) > 0:
                         control_response_here = ftf2.fouriercoeffs_tf2(timeseries[control_stimulus_samples], freq_response_here, sample_rate)
                 else:
                     if len(stimulus_samples) > 0:
                         dur = stim_onsetoffsetid[i, 1] - stim_onsetoffsetid[i, 0]
                         response_here = ftfs.fouriercoeffs_tf_spikes(timestamps[stimulus_samples] - stim_onsetoffsetid[i, 0], freq_response_here, dur)
                     if len(control_stimulus_samples) > 0:
                         dur_c = stim_onsetoffsetid[control_stim_here, 1] - stim_onsetoffsetid[control_stim_here, 0]
                         control_response_here = ftfs.fouriercoeffs_tf_spikes(timestamps[control_stimulus_samples] - stim_onsetoffsetid[control_stim_here, 0], freq_response_here, dur_c)

                 if prestimulus_time:
                     if not isspike:
                         if len(prestimulus_samples) > 0:
                             prestimulus_here = ftf2.fouriercoeffs_tf2(timeseries[prestimulus_samples], freq_response_here, sample_rate)
                         if len(control_prestimulus_samples) > 0:
                             control_prestimulus_here = ftf2.fouriercoeffs_tf2(timeseries[control_prestimulus_samples], freq_response_here, sample_rate)
                     else:
                         pt = prestimulus_time if np.isscalar(prestimulus_time) else prestimulus_time[0]
                         if len(prestimulus_samples) > 0:
                             prestimulus_here = ftfs.fouriercoeffs_tf_spikes(timestamps[prestimulus_samples] - stim_onsetoffsetid[i, 0] + pt, freq_response_here, pt) # MATLAB subtracts prestimulus_time logic?
                             # MATLAB: timestamps - stim_start - prestimulus_time.
                             # timestamps are in range [start-pre, start].
                             # so timestamps - start is [-pre, 0].
                             # minus prestimulus_time?
                             # MATLAB: timestamps(prestimulus_samples)-stim_onsetoffsetid(i,1)-prestimulus_time
                             # Wait, if timestamps are [start-pre, start], then timestamps-start is [-pre, 0].
                             # Subtracting pre gives [-2pre, -pre].
                             # This seems wrong for fourier of [0, duration]?
                             # `fouriercoeffs_tf_spikes` expects times relative to window start?
                             # Or just times.
                             # If we want the phase to be consistent, we might want it relative to stim start?
                             # If we treat the prestimulus window as a window of length `pre`.
                             # If we shift it to start at 0?
                             # timestamps - (start - pre) = timestamps - start + pre.
                             # MATLAB: `timestamps(...) - start - pre`. This seems weird.
                             # Let's check MATLAB code again.
                             # `timestamps(prestimulus_samples)-stim_onsetoffsetid(i,1)-prestimulus_time`
                             # This shifts times to be very negative.
                             # Maybe it's a typo in MATLAB or I misunderstand?
                             # "timestamps(prestimulus_samples)" are near "start".
                             # Actually they are `start-pre` to `start`.
                             # So `timestamps - start` is `[-pre, 0]`.
                             # `timestamps - start - pre` is `[-2pre, -pre]`.
                             # This is probably not what is intended for a fourier transform of a segment, unless phase matters relative to something way back.
                             # But `fouriercoeffs_tf_spikes` just does `sum(exp(-i*2*pi*f*t))`.
                             # If t is shifted, phase is shifted.
                             # If we want to compare magnitude, it doesn't matter.
                             # If we subtract `start-pre` (start of window), we get `[0, pre]`.
                             # That would be `timestamps - (stim_onsetoffsetid(i,1) - prestimulus_time)`.
                             # = `timestamps - stim + pre`.
                             # MATLAB has `- pre`.
                             # Maybe I should just copy MATLAB exactly?
                             # `timestamps - stim_onsetoffsetid(i,1) - prestimulus_time`.

                             prestimulus_here = ftfs.fouriercoeffs_tf_spikes(timestamps[prestimulus_samples] - stim_onsetoffsetid[i, 0] - pt, freq_response_here, pt)

                         if len(control_prestimulus_samples) > 0:
                             control_prestimulus_here = ftfs.fouriercoeffs_tf_spikes(timestamps[control_prestimulus_samples] - stim_onsetoffsetid[control_stim_here, 0] - pt, freq_response_here, pt)

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

        response[i] = response_here
        if control_stim_here is not None:
            control_response[i] = control_response_here
        else:
            control_response[i] = np.nan

    result = {
        'stimid': stimid,
        'response': response,
        'control_response': control_response,
        'controlstimnumber': controlstimnumber,
        'parameters': parameters
    }

    return result
