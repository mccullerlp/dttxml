import unittest
import numpy as np
from numpy.testing import assert_allclose

import pydarm_measurement as measurement


def test_get_raw_tf(fpath_join, tpath_join):
    data_from_dtt = np.genfromtxt(
        fpath_join('data', '2020-01-03_H1_'
                   'DARM_OLGTF_LF_SS_A_DARMIN2_B_DARMIN1_tf.txt'),
        dtype='float',
        delimiter=None
    )

    freq_from_dtt = data_from_dtt[:, 0]
    mag_from_dtt = np.abs(data_from_dtt[:, 1]+1j*data_from_dtt[:, 2])
    angle_from_dtt = np.angle(
        data_from_dtt[:, 1] + 1j*data_from_dtt[:, 2],
        deg=True
    )

    measurement_file = fpath_join('data', '2020-01-03_H1_'
                                  'DARM_OLGTF_LF_SS_5to1100Hz_15min.xml')
    channelA = 'H1:LSC-DARM1_IN2'
    channelB = 'H1:LSC-DARM1_IN1'
    meas_object = measurement.Measurement(measurement_file)
    freq, tf, coh, unc = meas_object.get_raw_tf(channelA, channelB)

    # Note: For some reason, the txt file is missing one frequency.
    # This is unrelated to the coherence, at least of this TF.
    freq_from_xml = freq
    freq_from_xml = np.delete(freq_from_xml, 22)
    mag_from_xml = np.abs(tf)
    mag_from_xml = np.delete(mag_from_xml, 22)
    angle_from_xml = np.angle(tf, deg=True)
    angle_from_xml = np.delete(angle_from_xml, 22)

    assert_allclose(freq_from_dtt, freq_from_xml, atol=1e-4)
    assert_allclose(mag_from_dtt, mag_from_xml, atol=1e-4)
    assert_allclose(angle_from_dtt, angle_from_xml, atol=1e-4)


def test_get_raw_asd(fpath_join, pprint):
    data_from_dtt = np.genfromtxt(
        fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.txt'),
        dtype='float',
        delimiter=None
    )

    freq_from_dtt = data_from_dtt[:, 0]
    asd_from_dtt = data_from_dtt[:, 1]

    measurement_file = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.xml')
    channelA = 'H1:LSC-DARM1_IN2'
    meas_object = measurement.Measurement(measurement_file)
    freq, asd = meas_object.get_raw_asd(channelA)

    freq_from_xml = freq
    asd_from_xml = asd

    pprint(asd_from_dtt, asd_from_xml)
    assert_allclose(freq_from_dtt, freq_from_xml)
    assert_allclose(asd_from_dtt, asd_from_xml)


def test_get_set_of_channels(fpath_join):
    channels_to_compare = [
        'H1:LSC-DARM1_EXC',
        'H1:LSC-DARM1_IN1',
        'H1:LSC-DARM1_IN2']

    measurement_file = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.xml')
    meas_object = measurement.Measurement(measurement_file)
    set_of_channels = meas_object.get_set_of_channels()

    assert(not (set(set_of_channels) ^ set(channels_to_compare)))
