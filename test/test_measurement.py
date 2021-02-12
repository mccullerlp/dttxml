import unittest
import pydarm
import numpy as np

import pydarm_measurement


class TestGetRawTF(unittest.TestCase):

    def setUp(self):
        data_from_dtt = np.genfromtxt(
                       ('./test/2020-01-03_H1_'
                        'DARM_OLGTF_LF_SS_A_DARMIN2_B_DARMIN1_tf.txt'),
                       dtype='float',
                       delimiter=None
        )

        self.freq_from_dtt = data_from_dtt[:, 0]
        self.mag_from_dtt = np.abs(data_from_dtt[:, 1]+1j*data_from_dtt[:, 2])
        self.angle_from_dtt = np.angle(data_from_dtt[:, 1]
                                       + 1j*data_from_dtt[:, 2],
                                       deg=True)

        measurement_file = ('./test/2020-01-03_H1_'
                            'DARM_OLGTF_LF_SS_5to1100Hz_15min.xml')
        channelA = 'H1:LSC-DARM1_IN2'
        channelB = 'H1:LSC-DARM1_IN1'
        meas_object = pydarm_measurement.Measurement(measurement_file)
        freq, tf, coh, unc = meas_object.get_raw_tf(channelA, channelB)

        # Note: For some reason, the txt file is missing one frequency.
        # This is unrelated to the coherence, at least of this TF.
        self.freq_from_xml = freq
        self.freq_from_xml = np.delete(self.freq_from_xml, 22)
        self.mag_from_xml = np.abs(tf)
        self.mag_from_xml = np.delete(self.mag_from_xml, 22)
        self.angle_from_xml = np.angle(tf, deg=True)
        self.angle_from_xml = np.delete(self.angle_from_xml, 22)

    def tearDown(self):
        del self.freq_from_dtt
        del self.mag_from_dtt
        del self.angle_from_dtt

        del self.freq_from_xml
        del self.mag_from_xml
        del self.angle_from_xml

    def test_measurement_class(self):
        for n in range(len(self.freq_from_dtt)):
            self.assertAlmostEqual(self.freq_from_dtt[n],
                                   self.freq_from_xml[n], places=4)
            self.assertAlmostEqual(self.mag_from_dtt[n],
                                   self.mag_from_xml[n], places=5)
            self.assertAlmostEqual(self.angle_from_dtt[n],
                                   self.angle_from_xml[n], places=4)

class TestGetRawASD(unittest.TestCase):

    def setUp(self):
        data_from_dtt = np.genfromtxt(
                       ('./test/2019-03-27_H1DARM_OLGTF_BB.txt'),
                       dtype='float',
                       delimiter=None
        )

        self.freq_from_dtt = data_from_dtt[:, 0]
        self.asd_from_dtt = data_from_dtt[:, 1]

        measurement_file = ('./test/2019-03-27_H1DARM_OLGTF_BB.xml')
        channelA = 'H1:LSC-DARM1_IN2'
        meas_object = pydarm.measurement.Measurement(measurement_file)
        freq, asd = meas_object.get_raw_asd(channelA)

        self.freq_from_xml = freq
        self.asd_from_xml = asd

    def tearDown(self):
        del self.freq_from_dtt
        del self.asd_from_dtt

        del self.freq_from_xml
        del self.asd_from_xml

    def test_measurement_class(self):
        for n in range(len(self.freq_from_dtt)):
            # print(self.freq_from_dtt[n], self.freq_from_xml[n])
            print(self.asd_from_dtt[n], self.asd_from_xml[n])
            self.assertAlmostEqual(self.freq_from_dtt[n],
                                   self.freq_from_xml[n], places=0)
            self.assertAlmostEqual(self.asd_from_dtt[n],
                                   self.asd_from_xml[n], places=5)
"""
class TestGetSetOfChannels(unittest.TestCase):

    def setUp(self):
        self.channels_to_compare = ['H1:LSC-DARM1_EXC',
                                    'H1:LSC-DARM1_IN1',
                                    'H1:LSC-DARM1_IN2']

        measurement_file = ('./test/2019-03-27_H1DARM_OLGTF_BB.xml')
        meas_object = pydarm.measurement.Measurement(measurement_file)
        self.set_of_channels = meas_object.get_set_of_channels()

    def tearDown(self):
        del self.channels_to_compare
        del self.set_of_channels

    def test_measurement_class(self):
        i = 0
        for channel in self.set_of_channels:
            print(self.channels_to_compare[i])
            print(channel)
            self.assertEqual(self.channels_to_compare[i],
                             channel)
            i = i+1
"""
if __name__ == '__main__':
    unittest.main()
