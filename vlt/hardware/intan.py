"""Intan RHD2000 file reading utilities.

Port of vlt.hardware.intan.read_Intan_RHD2000_header from MATLAB.
Reference: https://github.com/Intan-Technologies/load-rhd-notebook-python
"""

import os
import struct


_RHD_MAGIC_NUMBER = 0xC6912702


def _read_qstring(fid):
    """Read a Qt-style QString from a binary file.

    QStrings are encoded as a 4-byte unsigned int length (in bytes),
    followed by length/2 unsigned 16-bit values (UTF-16LE characters).
    A length of 0xFFFFFFFF indicates a null/empty string.
    """
    length, = struct.unpack('<I', fid.read(4))
    if length == 0xFFFFFFFF:
        return ''
    if length == 0:
        return ''
    data = fid.read(length)
    return data.decode('utf-16-le')


def read_Intan_RHD2000_header(filename: str) -> dict:
    """Read the header of an Intan RHD2000 .rhd file.

    Port of vlt.hardware.intan.read_Intan_RHD2000_header from MATLAB.

    Args:
        filename: Path to .rhd file

    Returns:
        Dict with keys including:
        - sample_rate: float
        - num_amplifier_channels: int
        - num_aux_input_channels: int
        - num_supply_voltage_channels: int
        - num_board_adc_channels: int
        - num_board_dig_in_channels: int
        - num_board_dig_out_channels: int
        - num_samples: int (computed from file size)
        - amplifier_channels: list of channel info dicts
        - frequency_parameters: dict
    """
    filesize = os.path.getsize(filename)

    with open(filename, 'rb') as fid:
        # 1. Magic number
        magic_number, = struct.unpack('<I', fid.read(4))
        if magic_number != _RHD_MAGIC_NUMBER:
            raise ValueError(
                f'Not a valid Intan RHD file: bad magic number '
                f'0x{magic_number:08X} (expected 0x{_RHD_MAGIC_NUMBER:08X})'
            )

        # 2. Version
        version = {}
        version['major'], version['minor'] = struct.unpack('<hh', fid.read(4))

        # 3. Sample rate
        sample_rate, = struct.unpack('<f', fid.read(4))

        # 4. Frequency parameters
        freq = {}
        (freq['dsp_enabled'],
         freq['actual_dsp_cutoff_frequency'],
         freq['actual_lower_bandwidth'],
         freq['actual_upper_bandwidth'],
         freq['desired_dsp_cutoff_frequency'],
         freq['desired_lower_bandwidth'],
         freq['desired_upper_bandwidth']) = struct.unpack('<hffffff', fid.read(26))

        notch_filter_mode, = struct.unpack('<h', fid.read(2))
        freq['notch_filter_frequency'] = {0: 0, 1: 50, 2: 60}.get(notch_filter_mode, 0)

        (freq['desired_impedance_test_frequency'],
         freq['actual_impedance_test_frequency']) = struct.unpack('<ff', fid.read(8))

        # Derived sample rates
        num_samples_per_data_block = 60
        if version['major'] > 1:
            num_samples_per_data_block = 128

        freq['amplifier_sample_rate'] = sample_rate
        freq['aux_input_sample_rate'] = sample_rate / 4
        freq['supply_voltage_sample_rate'] = sample_rate / num_samples_per_data_block
        freq['board_adc_sample_rate'] = sample_rate
        freq['board_dig_in_sample_rate'] = sample_rate

        # 5. Notes (3 QStrings)
        notes = {
            'note1': _read_qstring(fid),
            'note2': _read_qstring(fid),
            'note3': _read_qstring(fid),
        }

        # 6. Num temp sensor channels (version >= 1.1)
        num_temp_sensor_channels = 0
        if version['major'] > 1 or (version['major'] == 1 and version['minor'] >= 1):
            num_temp_sensor_channels, = struct.unpack('<h', fid.read(2))

        # 7. Eval board mode (version >= 1.3)
        eval_board_mode = 0
        if version['major'] > 1 or (version['major'] == 1 and version['minor'] >= 3):
            eval_board_mode, = struct.unpack('<h', fid.read(2))

        # 8. Reference channel (version >= 2.0)
        reference_channel = ''
        if version['major'] > 1:
            reference_channel = _read_qstring(fid)

        # 9. Signal groups and channels
        number_of_signal_groups, = struct.unpack('<h', fid.read(2))

        amplifier_channels = []
        aux_input_channels = []
        supply_voltage_channels = []
        board_adc_channels = []
        board_dig_in_channels = []
        board_dig_out_channels = []

        for _ in range(number_of_signal_groups):
            signal_group_name = _read_qstring(fid)
            signal_group_prefix = _read_qstring(fid)
            (signal_group_enabled,
             signal_group_num_channels,
             _) = struct.unpack('<hhh', fid.read(6))

            if signal_group_enabled == 0 or signal_group_num_channels == 0:
                continue

            for _ in range(signal_group_num_channels):
                native_channel_name = _read_qstring(fid)
                custom_channel_name = _read_qstring(fid)
                (native_order,
                 custom_order,
                 signal_type,
                 channel_enabled,
                 chip_channel,
                 board_stream) = struct.unpack('<hhhhhh', fid.read(12))
                (voltage_trigger_mode,
                 voltage_threshold,
                 digital_trigger_channel,
                 digital_edge_polarity) = struct.unpack('<hhhh', fid.read(8))
                (electrode_impedance_magnitude,
                 electrode_impedance_phase) = struct.unpack('<ff', fid.read(8))

                if channel_enabled == 0:
                    continue

                channel_info = {
                    'native_channel_name': native_channel_name,
                    'custom_channel_name': custom_channel_name,
                    'native_order': native_order,
                    'custom_order': custom_order,
                    'signal_type': signal_type,
                    'chip_channel': chip_channel,
                    'board_stream': board_stream,
                    'voltage_trigger_mode': voltage_trigger_mode,
                    'voltage_threshold': voltage_threshold,
                    'digital_trigger_channel': digital_trigger_channel,
                    'digital_edge_polarity': digital_edge_polarity,
                    'electrode_impedance_magnitude': electrode_impedance_magnitude,
                    'electrode_impedance_phase': electrode_impedance_phase,
                }

                if signal_type == 0:
                    amplifier_channels.append(channel_info)
                elif signal_type == 1:
                    aux_input_channels.append(channel_info)
                elif signal_type == 2:
                    supply_voltage_channels.append(channel_info)
                elif signal_type == 3:
                    board_adc_channels.append(channel_info)
                elif signal_type == 4:
                    board_dig_in_channels.append(channel_info)
                elif signal_type == 5:
                    board_dig_out_channels.append(channel_info)

        header_size = fid.tell()

    # 10. Compute num_samples from file size
    num_amplifier_channels = len(amplifier_channels)
    num_aux_input_channels = len(aux_input_channels)
    num_supply_voltage_channels = len(supply_voltage_channels)
    num_board_adc_channels = len(board_adc_channels)
    num_board_dig_in_channels = len(board_dig_in_channels)
    num_board_dig_out_channels = len(board_dig_out_channels)

    # Compute bytes per data block
    bytes_per_block = 0
    # Timestamps: num_samples_per_data_block * 4 bytes (int32)
    bytes_per_block += num_samples_per_data_block * 4
    # Amplifier data: num_samples_per_data_block * num_amp_channels * 2 (uint16)
    bytes_per_block += num_samples_per_data_block * num_amplifier_channels * 2
    # Aux input: (num_samples_per_data_block / 4) * num_aux_channels * 2
    bytes_per_block += (num_samples_per_data_block // 4) * num_aux_input_channels * 2
    # Supply voltage: 1 * num_supply_channels * 2
    bytes_per_block += 1 * num_supply_voltage_channels * 2
    # Temp sensors: 1 * num_temp_sensor_channels * 2
    bytes_per_block += 1 * num_temp_sensor_channels * 2
    # Board ADC: num_samples_per_data_block * num_adc_channels * 2
    bytes_per_block += num_samples_per_data_block * num_board_adc_channels * 2
    # Board digital in: num_samples_per_data_block * 1 * 2 (packed into uint16)
    if num_board_dig_in_channels > 0:
        bytes_per_block += num_samples_per_data_block * 2
    # Board digital out: num_samples_per_data_block * 1 * 2
    if num_board_dig_out_channels > 0:
        bytes_per_block += num_samples_per_data_block * 2

    bytes_remaining = filesize - header_size
    if bytes_per_block > 0:
        num_blocks = bytes_remaining // bytes_per_block
    else:
        num_blocks = 0

    num_samples = num_samples_per_data_block * num_blocks

    header = {
        'version': version,
        'sample_rate': float(sample_rate),
        'num_samples_per_data_block': num_samples_per_data_block,
        'frequency_parameters': freq,
        'notes': notes,
        'num_temp_sensor_channels': num_temp_sensor_channels,
        'eval_board_mode': eval_board_mode,
        'reference_channel': reference_channel,
        'amplifier_channels': amplifier_channels,
        'aux_input_channels': aux_input_channels,
        'supply_voltage_channels': supply_voltage_channels,
        'board_adc_channels': board_adc_channels,
        'board_dig_in_channels': board_dig_in_channels,
        'board_dig_out_channels': board_dig_out_channels,
        'num_amplifier_channels': num_amplifier_channels,
        'num_aux_input_channels': num_aux_input_channels,
        'num_supply_voltage_channels': num_supply_voltage_channels,
        'num_board_adc_channels': num_board_adc_channels,
        'num_board_dig_in_channels': num_board_dig_in_channels,
        'num_board_dig_out_channels': num_board_dig_out_channels,
        'num_samples': num_samples,
        'header_size': header_size,
    }

    return header
