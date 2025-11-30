import os
import struct
import numpy as np
import vlt.file
import vlt.string
import vlt.signal
import vlt.math

def vhsb_sampletype2matlabfwritestring(data_type, data_size):
    """
    Return struct format string for sample type.
    """

    s = ''
    if data_type == 1: # char
        if data_size == 8: return 'c' # char
    elif data_type == 2: # uint
        if data_size == 8: return 'B'
        if data_size == 16: return 'H'
        if data_size == 32: return 'I'
        if data_size == 64: return 'Q'
    elif data_type == 3: # int
        if data_size == 8: return 'b'
        if data_size == 16: return 'h'
        if data_size == 32: return 'i'
        if data_size == 64: return 'q'
    elif data_type == 4: # float
        if data_size == 32: return 'f'
        if data_size == 64: return 'd'

    raise ValueError(f"Unknown data type/size combination: type={data_type}, size={data_size}")

def vhsb_writeheader(fo, **kwargs):
    """
    Write a VH Lab Series Binary file header.
    """

    params = {
        'version': 1,
        'machine_format': 'little-endian',
        'X_data_size': 64,
        'X_data_type': 4,
        'Y_dim': [1, 1],
        'Y_data_size': 64,
        'Y_data_type': 4,
        'X_stored': 1,
        'X_constantinterval': 1,
        'X_start': 0,
        'X_increment': 0,
        'X_units': '',
        'Y_units': '',
        'X_usescale': 0,
        'Y_usescale': 0,
        'X_scale': 1.0,
        'X_offset': 0.0,
        'Y_scale': 1.0,
        'Y_offset': 0.0,
    }

    params.update(kwargs)

    # Validation/Formatting
    skip = 200
    headersize = 1836

    filename = vlt.file.filename_value(fo)

    with open(filename, 'wb') as f:
        # ID
        id_str = "This is a VHSB file, http://github.com/VH-Lab\n"
        id_bytes = id_str.encode('utf-8')
        f.write(id_bytes)
        f.write(b'\0' * (skip - len(id_bytes)))

        # Seek to skip (should be there already)
        f.seek(skip)

        # Write fields. Using little-endian '<'
        f.write(struct.pack('<I', params['version']))

        mf = params['machine_format'] + '\n'
        mf_bytes = mf.encode('utf-8')
        f.write(mf_bytes)
        f.write(b'\0' * (256 - len(mf_bytes)))

        f.write(struct.pack('<I', params['X_data_size']))
        f.write(struct.pack('<H', params['X_data_type']))

        # Y_dim (100 uint64s)
        y_dim = np.array(params['Y_dim'], dtype=np.uint64).flatten()
        if len(y_dim) > 100:
            y_dim = y_dim[:100]
        else:
            y_dim = np.pad(y_dim, (0, 100 - len(y_dim)), 'constant')
        f.write(y_dim.astype('<u8').tobytes())

        f.write(struct.pack('<I', params['Y_data_size']))
        f.write(struct.pack('<H', params['Y_data_type']))

        f.write(struct.pack('<B', params['X_stored']))
        f.write(struct.pack('<B', params['X_constantinterval']))

        # X_start and X_increment
        x_fmt = vhsb_sampletype2matlabfwritestring(params['X_data_type'], params['X_data_size'])
        f.write(struct.pack('<' + x_fmt, params['X_start']))
        f.write(struct.pack('<' + x_fmt, params['X_increment']))

        xu = params['X_units'] + '\n'
        xu_bytes = xu.encode('utf-8')
        f.write(xu_bytes)
        f.write(b'\0' * (256 - len(xu_bytes)))

        yu = params['Y_units'] + '\n'
        yu_bytes = yu.encode('utf-8')
        f.write(yu_bytes)
        f.write(b'\0' * (256 - len(yu_bytes)))

        f.write(struct.pack('<B', params['X_usescale']))
        f.write(struct.pack('<B', params['Y_usescale']))

        f.write(struct.pack('<d', float(params['X_scale'])))
        f.write(struct.pack('<d', float(params['X_offset'])))
        f.write(struct.pack('<d', float(params['Y_scale'])))
        f.write(struct.pack('<d', float(params['Y_offset'])))

    return params

def vhsb_readheader(fo):
    """
    Read a VH Lab Series Binary file header.
    """
    skip = 200
    headersize = 1836

    filename = vlt.file.filename_value(fo)
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Could not find file {filename}")

    h = {}

    filesize = os.path.getsize(filename)

    with open(filename, 'rb') as f:
        f.seek(skip)

        h['version'] = struct.unpack('<I', f.read(4))[0]

        mf_bytes = f.read(256)
        h['machine_format'] = vlt.string.line_n(mf_bytes.decode('utf-8', errors='ignore'), 1)[0]

        h['X_data_size'] = struct.unpack('<I', f.read(4))[0]
        h['X_data_type'] = struct.unpack('<H', f.read(2))[0]

        y_dim_bytes = f.read(8 * 100)
        h['Y_dim'] = np.frombuffer(y_dim_bytes, dtype='<u8')
        h['Y_dim'] = h['Y_dim'][h['Y_dim'] > 0]

        h['Y_data_size'] = struct.unpack('<I', f.read(4))[0]
        h['Y_data_type'] = struct.unpack('<H', f.read(2))[0]

        h['X_stored'] = struct.unpack('<B', f.read(1))[0]
        h['X_constantinterval'] = struct.unpack('<B', f.read(1))[0]

        x_fmt = vhsb_sampletype2matlabfwritestring(h['X_data_type'], h['X_data_size'])
        size_bytes = struct.calcsize('<' + x_fmt)
        h['X_start'] = struct.unpack('<' + x_fmt, f.read(size_bytes))[0]
        h['X_increment'] = struct.unpack('<' + x_fmt, f.read(size_bytes))[0]

        xu_bytes = f.read(256)
        h['X_units'] = vlt.string.line_n(xu_bytes.decode('utf-8', errors='ignore'), 1)[0]

        yu_bytes = f.read(256)
        h['Y_units'] = vlt.string.line_n(yu_bytes.decode('utf-8', errors='ignore'), 1)[0]

        h['X_usescale'] = struct.unpack('<B', f.read(1))[0]
        h['Y_usescale'] = struct.unpack('<B', f.read(1))[0]

        h['X_scale'] = struct.unpack('<d', f.read(8))[0]
        h['X_offset'] = struct.unpack('<d', f.read(8))[0]

        h['Y_scale'] = struct.unpack('<d', f.read(8))[0]
        h['Y_offset'] = struct.unpack('<d', f.read(8))[0]

    # Calculated fields
    if len(h['Y_dim']) > 1:
        prod_ydim_2_end = np.prod(h['Y_dim'][1:])
    else:
        prod_ydim_2_end = 1

    h['X_skip_bytes'] = int(prod_ydim_2_end * (h['Y_data_size'] / 8))
    h['Y_skip_bytes'] = int((h['X_data_size'] / 8) * (1 if h['X_stored'] else 0))
    h['sample_size'] = h['X_skip_bytes'] + h['Y_skip_bytes']

    h['filesize'] = filesize
    h['headersize'] = headersize

    if h['sample_size'] > 0:
        h['num_samples'] = int((filesize - headersize) / h['sample_size'])
    else:
        h['num_samples'] = 0

    return h

def vhsb_write(fo, x, y, **kwargs):
    """
    Write a VHLab series binary file.
    """
    x = np.array(x)
    y = np.array(y)

    if len(x) != len(y):
        raise ValueError("X must have the same number of rows as Y (rows correspond to samples)")

    defaults = {
        'use_filelock': 1,
        'X_units': '',
        'Y_units': '',
        'X_data_size': 64,
        'X_data_type': 'float', # String in kwargs, but map to code
        'Y_data_size': 64,
        'Y_data_type': 'float',
        'X_usescale': 0,
        'Y_usescale': 0,
        'X_scale': 1,
        'X_offset': 0,
        'Y_scale': 1,
        'Y_offset': 0
    }

    if len(x) > 0:
        defaults['X_start'] = x.flat[0]
        if len(x) > 1:
            defaults['X_increment'] = np.median(np.diff(x.flatten()))
            dx = np.diff(x.flatten())
            defaults['X_constantinterval'] = 1 if (np.max(np.abs(np.diff(dx))) < 1e-7) else 0
        else:
            defaults['X_increment'] = 0
            defaults['X_constantinterval'] = 0
    else:
        defaults['X_start'] = 0
        defaults['X_increment'] = 0
        defaults['X_constantinterval'] = 0

    defaults['X_stored'] = 1

    params = defaults.copy()
    params.update(kwargs)

    type_map = {'char': 1, 'uint': 2, 'int': 3, 'float': 4}
    if isinstance(params['X_data_type'], str):
        params['X_data_type'] = type_map[params['X_data_type'].lower()]
    if isinstance(params['Y_data_type'], str):
        params['Y_data_type'] = type_map[params['Y_data_type'].lower()]

    if params['X_usescale']:
        x = x / params['X_scale'] + params['X_offset']
    if params['Y_usescale']:
        y = y / params['Y_scale'] + params['Y_offset']

    params['Y_dim'] = y.shape

    filename = vlt.file.filename_value(fo)

    if params['use_filelock']:
        lock_fname = filename + '-lock'
        fid, key = vlt.file.checkout_lock_file(lock_fname)
        if fid < 0:
            raise Exception(f"Could not get lock for file {lock_fname}")

    try:
        h = vhsb_writeheader(fo, **params)

        with open(filename, 'r+b') as f:
            f.seek(1836)

            x_fmt = vhsb_sampletype2matlabfwritestring(params['X_data_type'], params['X_data_size'])
            y_fmt = vhsb_sampletype2matlabfwritestring(params['Y_data_type'], params['Y_data_size'])

            x_bytes_len = int(params['X_data_size'] / 8)
            y_bytes_len = int(params['Y_data_size'] / 8)
            y_sample_size_bytes = int(np.prod(params['Y_dim'][1:]) * y_bytes_len)

            x_data = x.astype('<' + x_fmt).flatten()

            x_view = x_data.view(np.uint8).reshape(len(x), x_bytes_len)
            y_data = y.astype('<' + y_fmt)
            y_view = y_data.view(np.uint8).reshape(len(y), y_sample_size_bytes)

            if params['X_stored']:
                combined = np.hstack([x_view, y_view])
            else:
                combined = y_view

            f.write(combined.tobytes())

    finally:
        if params['use_filelock']:
            vlt.file.release_lock_file(lock_fname, key)

    return True

def vhsb_read(fo, x0, x1, out_of_bounds_err=False):
    """
    Read a VHLab series binary file.
    """
    h = vhsb_readheader(fo)
    filename = vlt.file.filename_value(fo)

    with open(filename, 'rb') as f:
        if h['X_constantinterval']:
            s = vlt.signal.point2samplelabel([x0, x1], h['X_increment'], h['X_start'])
            s[0] = vlt.math.clip(s[0], [1, h['num_samples']])
            s[1] = vlt.math.clip(s[1], [1, h['num_samples']])
        else:
             s = [1, h['num_samples']]

        num_samples_to_read = int(s[1] - s[0] + 1)
        if num_samples_to_read <= 0:
             return np.array([]), np.array([])

        start_sample_idx = int(s[0] - 1)

        x_fmt = vhsb_sampletype2matlabfwritestring(h['X_data_type'], h['X_data_size'])
        y_fmt = vhsb_sampletype2matlabfwritestring(h['Y_data_type'], h['Y_data_size'])

        x_bytes_len = int(h['X_data_size'] / 8)
        y_bytes_len = int(h['Y_data_size'] / 8)
        y_dim_prod = int(np.prod(h['Y_dim'][1:]) if len(h['Y_dim']) > 1 else 1)

        full_sample_size = h['sample_size']

        f.seek(h['headersize'] + start_sample_idx * full_sample_size)

        data_chunk = f.read(num_samples_to_read * full_sample_size)

        dtype_spec = {
            'names': [],
            'formats': [],
            'offsets': [],
            'itemsize': full_sample_size
        }
        off = 0
        if h['X_stored']:
            dtype_spec['names'].append('x')
            dtype_spec['formats'].append('<' + x_fmt)
            dtype_spec['offsets'].append(0)
            off += x_bytes_len

        dtype_spec['names'].append('y')
        dtype_spec['formats'].append(('<' + y_fmt, (y_dim_prod,)))
        dtype_spec['offsets'].append(off)

        dt = np.dtype(dtype_spec)

        data = np.frombuffer(data_chunk, dtype=dt)

        if h['X_stored']:
            x = data['x']
            if h['X_usescale']:
                x = (x - h['X_offset']) * h['X_scale']
        else:
             x = vlt.signal.samplelabel2point(np.arange(s[0], s[1]+1), h['X_increment'], h['X_start'])

        y = data['y']

        new_shape = [num_samples_to_read] + list(h['Y_dim'][1:])
        y = y.reshape(new_shape)

        if h['Y_usescale']:
            y = (y - h['Y_offset']) * h['Y_scale']

        if not h['X_constantinterval']:
            mask = (x >= x0) & (x <= x1)
            x = x[mask]
            y = y[mask]

        return y, x

def newvhlspikewaveformfile(fid_or_filename, parameters):
    """
    Create a binary file for storing spike waveforms.
    """

    close_at_end = False
    if isinstance(fid_or_filename, str):
        fid = open(fid_or_filename, 'wb')
        close_at_end = True
    else:
        fid = fid_or_filename

    try:
        fid.seek(0)
        fid.write(struct.pack('<B', int(parameters['numchannels'])))
        fid.write(struct.pack('<b', int(parameters['S0'])))
        fid.write(struct.pack('<b', int(parameters['S1'])))

        name = parameters.get('name', '')[:80]
        name_bytes = name.encode('utf-8')
        fid.write(name_bytes)
        fid.write(b'\0' * (80 - len(name_bytes)))

        fid.write(struct.pack('<B', int(parameters['ref'])))

        comment = parameters.get('comment', '')[:80]
        comment_bytes = comment.encode('utf-8')
        fid.write(comment_bytes)
        fid.write(b'\0' * (80 - len(comment_bytes)))

        fid.write(struct.pack('<f', float(parameters['samplingrate'])))

        current_pos = fid.tell()
        fid.write(b'\0' * (512 - current_pos))

    finally:
        if close_at_end:
            fid.close()
            return 1
        else:
            return fid

def addvhlspikewaveformfile(fid_or_filename, waveforms):
    """
    Add waveforms to a VHL spike waveform file.
    """
    close_at_end = False
    if isinstance(fid_or_filename, str):
        fid = open(fid_or_filename, 'ab')
        close_at_end = True
    else:
        fid = fid_or_filename

    try:
        waveforms = np.array(waveforms, dtype='<f4')
        w = waveforms.transpose(2, 1, 0)
        fid.seek(0, 2)
        fid.write(w.tobytes())

    finally:
        if close_at_end:
            fid.close()

def readvhlspikewaveformfile(file_or_fid, wave_start=1, wave_end=float('inf')):
    """
    Read spike waveforms from binary file.
    """

    close_at_end = False
    if isinstance(file_or_fid, str):
        fid = open(file_or_fid, 'rb')
        close_at_end = True
    else:
        fid = file_or_fid

    try:
        fid.seek(0)
        parameters = {}
        parameters['numchannels'] = struct.unpack('<B', fid.read(1))[0]
        parameters['S0'] = struct.unpack('<b', fid.read(1))[0]
        parameters['S1'] = struct.unpack('<b', fid.read(1))[0]

        fid.seek(3)
        name_bytes = fid.read(80)
        parameters['name'] = name_bytes.decode('utf-8', errors='ignore').strip('\x00')

        fid.seek(83)
        parameters['ref'] = struct.unpack('<B', fid.read(1))[0]

        comment_bytes = fid.read(80)
        parameters['comment'] = comment_bytes.decode('utf-8', errors='ignore').strip('\x00')

        parameters['samplingrate'] = struct.unpack('<f', fid.read(4))[0]

        header_size = 512
        samples_per_channel = parameters['S1'] - parameters['S0'] + 1
        num_channels = parameters['numchannels']
        wave_size_floats = num_channels * samples_per_channel
        wave_size_bytes = wave_size_floats * 4

        if wave_start > 0:
            fid.seek(0, 2)
            filesize = fid.tell()

            total_waves = (filesize - header_size) / wave_size_bytes

            if wave_end == float('inf'):
                wave_end = int(total_waves)

            start_idx = int(wave_start) - 1
            count = int(wave_end) - start_idx

            if count <= 0:
                 return np.array([]), parameters

            fid.seek(int(header_size + start_idx * wave_size_bytes))
            data = fid.read(int(count * wave_size_bytes))

            waveforms_flat = np.frombuffer(data, dtype='<f4')

            w = waveforms_flat.reshape(count, num_channels, samples_per_channel)
            waveforms = w.transpose(2, 1, 0)

        else:
            waveforms = np.array([])

        return waveforms, parameters

    finally:
        if close_at_end:
            fid.close()
