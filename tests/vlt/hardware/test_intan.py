"""Tests for vlt.hardware.intan module."""

import os
import struct
import tempfile

import pytest

from vlt.hardware.intan import read_Intan_RHD2000_header


def _write_qstring(fid, s):
    """Write a Qt-style QString to a binary file."""
    if not s:
        fid.write(struct.pack('<I', 0xFFFFFFFF))
    else:
        encoded = s.encode('utf-16-le')
        fid.write(struct.pack('<I', len(encoded)))
        fid.write(encoded)


def _write_channel(fid, native_name, custom_name, native_order, custom_order,
                   signal_type, channel_enabled, chip_channel, board_stream):
    """Write a single channel definition to the binary file."""
    _write_qstring(fid, native_name)
    _write_qstring(fid, custom_name)
    fid.write(struct.pack('<hhhhhh', native_order, custom_order,
                          signal_type, channel_enabled, chip_channel, board_stream))
    # Trigger settings
    fid.write(struct.pack('<hhhh', 0, 0, 0, 0))
    # Impedance
    fid.write(struct.pack('<ff', 0.0, 0.0))


def create_synthetic_rhd(filepath, sample_rate=20000.0, num_amp_channels=2,
                         num_aux_channels=3, num_supply_channels=1,
                         num_adc_channels=0, num_dig_in_channels=0,
                         num_dig_out_channels=0, num_data_blocks=1000,
                         version_major=1, version_minor=3):
    """Create a synthetic .rhd file for testing.

    With version 1.x, each data block contains 60 samples.
    """
    num_samples_per_block = 60 if version_major <= 1 else 128

    with open(filepath, 'wb') as fid:
        # Magic number
        fid.write(struct.pack('<I', 0xC6912702))
        # Version
        fid.write(struct.pack('<hh', version_major, version_minor))
        # Sample rate
        fid.write(struct.pack('<f', sample_rate))
        # Frequency parameters: dsp_enabled(h) + 6 floats
        fid.write(struct.pack('<hffffff', 1, 1.0, 1.0, 7500.0, 1.0, 1.0, 7500.0))
        # Notch filter mode
        fid.write(struct.pack('<h', 2))  # 60 Hz
        # Impedance test frequencies
        fid.write(struct.pack('<ff', 1000.0, 1000.0))
        # Notes
        _write_qstring(fid, '')
        _write_qstring(fid, '')
        _write_qstring(fid, '')
        # Num temp sensor channels (version >= 1.1)
        num_temp_channels = 1
        fid.write(struct.pack('<h', num_temp_channels))
        # Eval board mode (version >= 1.3)
        fid.write(struct.pack('<h', 0))
        # Reference channel (version >= 2.0)
        if version_major > 1:
            _write_qstring(fid, '')

        # Signal groups: put all channels in one group
        total_channels = (num_amp_channels + num_aux_channels +
                          num_supply_channels + num_adc_channels +
                          num_dig_in_channels + num_dig_out_channels)
        fid.write(struct.pack('<h', 1))  # 1 signal group

        _write_qstring(fid, 'Port A')
        _write_qstring(fid, 'A')
        fid.write(struct.pack('<hhh', 1, total_channels, 0))

        order = 0
        for i in range(num_amp_channels):
            _write_channel(fid, f'A-{i:03d}', f'A-{i:03d}', order, order, 0, 1, i, 0)
            order += 1
        for i in range(num_aux_channels):
            _write_channel(fid, f'AUX-{i}', f'AUX-{i}', order, order, 1, 1, i, 0)
            order += 1
        for i in range(num_supply_channels):
            _write_channel(fid, f'VDD-{i}', f'VDD-{i}', order, order, 2, 1, i, 0)
            order += 1
        for i in range(num_adc_channels):
            _write_channel(fid, f'ADC-{i}', f'ADC-{i}', order, order, 3, 1, i, 0)
            order += 1
        for i in range(num_dig_in_channels):
            _write_channel(fid, f'DIN-{i}', f'DIN-{i}', order, order, 4, 1, i, 0)
            order += 1
        for i in range(num_dig_out_channels):
            _write_channel(fid, f'DOUT-{i}', f'DOUT-{i}', order, order, 5, 1, i, 0)
            order += 1

        header_size = fid.tell()

        # Compute bytes per data block and write dummy data
        bytes_per_block = 0
        bytes_per_block += num_samples_per_block * 4  # timestamps
        bytes_per_block += num_samples_per_block * num_amp_channels * 2  # amplifier
        bytes_per_block += (num_samples_per_block // 4) * num_aux_channels * 2  # aux
        bytes_per_block += 1 * num_supply_channels * 2  # supply voltage
        bytes_per_block += 1 * num_temp_channels * 2  # temp sensors
        bytes_per_block += num_samples_per_block * num_adc_channels * 2  # ADC
        if num_dig_in_channels > 0:
            bytes_per_block += num_samples_per_block * 2  # digital in
        if num_dig_out_channels > 0:
            bytes_per_block += num_samples_per_block * 2  # digital out

        # Write dummy data blocks
        fid.write(b'\x00' * (bytes_per_block * num_data_blocks))

    return header_size


class TestReadIntanRHD2000Header:
    """Tests for read_Intan_RHD2000_header."""

    def test_basic_header_reading(self, tmp_path):
        """Test reading a synthetic RHD file with known parameters."""
        filepath = str(tmp_path / 'test.rhd')
        create_synthetic_rhd(filepath, sample_rate=20000.0,
                             num_amp_channels=2, num_data_blocks=1000)

        header = read_Intan_RHD2000_header(filepath)

        assert header['sample_rate'] == 20000.0
        assert header['num_amplifier_channels'] == 2
        assert header['num_aux_input_channels'] == 3
        assert header['num_supply_voltage_channels'] == 1
        # 1000 blocks * 60 samples/block = 60000 samples
        assert header['num_samples'] == 60000

    def test_sample_rate_and_num_samples(self, tmp_path):
        """Test that sample_rate and num_samples are correct for t0_t1 computation.

        With 1000 data blocks at 60 samples/block = 60000 samples,
        t0 = 0, t1 = (60000 - 1) / 20000 = 2.99995
        """
        filepath = str(tmp_path / 'test.rhd')
        create_synthetic_rhd(filepath, sample_rate=20000.0, num_data_blocks=1000)

        header = read_Intan_RHD2000_header(filepath)

        t0 = 0
        t1 = (header['num_samples'] - 1) / header['sample_rate']
        assert t0 == 0
        assert abs(t1 - 2.99995) < 1e-10

    def test_channel_info_populated(self, tmp_path):
        """Test that channel info dicts contain expected fields."""
        filepath = str(tmp_path / 'test.rhd')
        create_synthetic_rhd(filepath, num_amp_channels=4)

        header = read_Intan_RHD2000_header(filepath)

        assert len(header['amplifier_channels']) == 4
        ch = header['amplifier_channels'][0]
        assert 'native_channel_name' in ch
        assert 'custom_channel_name' in ch
        assert 'chip_channel' in ch
        assert ch['signal_type'] == 0

    def test_frequency_parameters(self, tmp_path):
        """Test that frequency parameters are read correctly."""
        filepath = str(tmp_path / 'test.rhd')
        create_synthetic_rhd(filepath, sample_rate=20000.0)

        header = read_Intan_RHD2000_header(filepath)

        freq = header['frequency_parameters']
        assert freq['amplifier_sample_rate'] == 20000.0
        assert freq['aux_input_sample_rate'] == 5000.0
        assert freq['notch_filter_frequency'] == 60
        assert freq['dsp_enabled'] == 1

    def test_invalid_magic_number(self, tmp_path):
        """Test that an invalid magic number raises ValueError."""
        filepath = str(tmp_path / 'bad.rhd')
        with open(filepath, 'wb') as f:
            f.write(struct.pack('<I', 0xDEADBEEF))
            f.write(b'\x00' * 100)

        with pytest.raises(ValueError, match='Not a valid Intan RHD file'):
            read_Intan_RHD2000_header(filepath)

    def test_version_2(self, tmp_path):
        """Test reading a version 2.x file (128 samples per block)."""
        filepath = str(tmp_path / 'test_v2.rhd')
        create_synthetic_rhd(filepath, sample_rate=30000.0,
                             num_amp_channels=1, num_aux_channels=1,
                             num_supply_channels=1, num_data_blocks=100,
                             version_major=2, version_minor=0)

        header = read_Intan_RHD2000_header(filepath)

        assert header['sample_rate'] == 30000.0
        assert header['num_amplifier_channels'] == 1
        # 100 blocks * 128 samples/block = 12800 samples
        assert header['num_samples'] == 12800
        assert header['num_samples_per_data_block'] == 128

    def test_no_data_blocks(self, tmp_path):
        """Test reading a file with header only (no data)."""
        filepath = str(tmp_path / 'header_only.rhd')
        create_synthetic_rhd(filepath, num_data_blocks=0)

        header = read_Intan_RHD2000_header(filepath)

        assert header['num_samples'] == 0
        assert header['sample_rate'] == 20000.0
