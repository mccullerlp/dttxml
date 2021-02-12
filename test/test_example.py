import numpy as np
from matplotlib import pyplot as plt

import pydarm_measurement as measurement


def test_example_1(fpath_join, tpath_join, plot, pprint):
    """
    Example code on how to use the following methods from measurement.py:
        - get_raw_tf
        - get_set_of_channels
        - get_raw_asd
    """
    # EXAMPLE 1: Dealing with a SweptSine measurement file.

    # These are the xml files we want to get our data from.
    measurement_file_1 = fpath_join('data', '2020-01-03_H1_DARM_OLGTF_LF_SS_5to1100Hz_15min.xml')

    meas_obj_1 = measurement.Measurement(measurement_file_1)
    channelA_1 = 'H1:LSC-DARM1_IN2'
    channelB_1 = 'H1:LSC-DARM1_IN1'
    temp_freq, temp_tf, temp_coh, temp_unc = meas_obj_1.get_raw_tf(channelA_1, channelB_1)

    # print(temp_raw_tf)

    plt.figure(1)
    plt.subplot(211)
    plt.loglog(temp_freq, np.abs(temp_tf), 'ro')

    plt.subplot(212)
    plt.semilogx(temp_freq, np.angle(temp_tf, deg=True), 'ro')
    if plot:
        plt.savefig(tpath_join('DARM.pdf'), format='pdf')
    #plt.show(block=False)

    # Examples of other information you can get from the measurement class:
    pprint('----------------------------------------------------')
    pprint('Other information in file ', measurement_file_1)
    pprint('GPS of measurement is ', meas_obj_1.gps_time)
    pprint('Navg of measurement is ', meas_obj_1.averages)
    pprint('Channels in measurement file are:', meas_obj_1.get_set_of_channels())
    pprint('----------------------------------------------------')


def test_example_2(fpath_join, tpath_join, plot, pprint):
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------

    # EXAMPLE 2: Dealing with an FFT dtt file.

    # The following lines show an example of ASD extraction from a dtt
    # file that contains FFT (or BroadBand data)

    # These are the xml files we want to get our data from.
    measurement_file_2 = fpath_join('data', '2019-03-27_H1DARM_OLGTF_BB.xml')

    meas_obj_2 = measurement.Measurement(measurement_file_2)
    channelA_2 = 'H1:LSC-DARM1_IN2'
    channelB_2 = 'H1:LSC-DARM1_IN1'
    channelA_freq, channelA_asd = meas_obj_2.get_raw_asd(channelA_2)
    channelB_freq, channelB_asd = meas_obj_2.get_raw_asd(channelB_2)

    # print(channelA_asd)

    plt.figure(2)
    plt.loglog(channelA_freq, channelA_asd, 'k', channelB_freq, channelB_asd, 'r')
    if plot:
        plt.savefig(tpath_join('DARM.pdf'))
    #plt.show(block=True)
    
    pprint('----------------------------------------------------')
    pprint('Other information in measurement file: ', measurement_file_2)
    pprint('GPS of measurement is ', meas_obj_2.gps_time)
    pprint('Navg of measurement is ', meas_obj_2.averages)
    pprint('Channels in measurement file are:', meas_obj_2.get_set_of_channels())
    pprint('----------------------------------------------------')
    # ----------------------------------------------------------------------
