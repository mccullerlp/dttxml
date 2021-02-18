import dttxml

import numpy as np
import matplotlib.pyplot as plt

def test_frequency_array1(fpath_join, tpath_join, plot):
    meas_file = fpath_join('data', 'test_DTT_20_f_pts.xml')

    channelA = 'H1:PEM-EX_SEIS_VEA_FLOOR_Z_DQ'
    # channelA = 'H1:CAL-PCALX_TX_PD_OUT_DQ'
    data_access = dttxml.DiagAccess(meas_file)

    asd_holder = data_access.asd(channelA)

    freq = np.array(asd_holder.FHz)
    asd = np.array(asd_holder.asd)

    data_from_dtt = np.genfromtxt(
        fpath_join('data', 'test_DTT_20_f_pts.txt'),
        dtype='float',
        delimiter=None
    )

    plt.figure(1)
    # plt.loglog(freq,asd,'r',data_from_dtt[:,0],data_from_dtt[:,1]*2,'k')
    plt.plot(freq, (data_from_dtt[:, 0]-freq), 'r')
    if plot:
        plt.savefig(tpath_join('residual1.pdf'))


def test_frequency_array2(fpath_join, tpath_join, plot, pprint):
    meas_file_2 = fpath_join('data', 'test_DTT_21_f_pts.xml')
    channelA_2 = 'H1:PEM-EX_SEIS_VEA_FLOOR_Z_DQ'

    data_access_2 = dttxml.DiagAccess(meas_file_2)
    asd_holder_2 = data_access_2.asd(channelA_2)

    freq_2 = asd_holder_2.FHz

    data_from_dtt_2 = np.genfromtxt(
        fpath_join('data', 'test_DTT_21_f_pts.txt'),
        dtype='float',
        delimiter=None
    )

    for i in range(len(freq_2)):
        pprint(freq_2[i], data_from_dtt_2[i, 0])

    plt.figure(2)
    plt.plot(freq_2, np.abs(data_from_dtt_2[:, 0]-freq_2))
    if plot:
        plt.savefig(tpath_join('residual2.pdf'))

