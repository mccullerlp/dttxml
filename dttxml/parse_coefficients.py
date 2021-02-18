"""
"""

import base64
import numpy as np
from .bunch import Bunch
import re


def parse_coefficients(
    LW_node,
    entry_type = None,
    entry_num = None,
    entry_text = None
):
    if entry_type == 'TransferMatrix':
        return None
    specbunch = Bunch()
    specbunch.channelA = {}
    specbunch.channelB = {}
    specbunch.channels = {}

    for sparam in LW_node.findall('Time'):
        if sparam.attrib["Name"] == 't0':
            specbunch.gps_second = float(sparam.text)
    for sparam in LW_node.findall('Param'):
        spname = sparam.attrib["Name"]
        if spname == 'Subtype':
            specbunch.subtype_raw = int(sparam.text)
        elif spname == 'Window':
            specbunch.window_raw = int(sparam.text)
            specbunch.window = {
                0 : 'uniform',
                1 : 'hanning',
                2 : 'flat-top',
                3 : 'welch',
                4 : 'bartlett',
                5 : 'bmh',
                6 : 'hamming',
                7 : 'kaiser',
            }.get(specbunch.window_raw, "unknown")
        elif spname == 'AverageType':
            specbunch.avgtype_raw = int(sparam.text)
            specbunch.avgtype = {
                0 : 'Fixed',
                1 : 'Exponential',
                2 : 'Single',
            }.get(specbunch.avgtype_raw, "unknown")
        elif spname == 'Averages':
            specbunch.averages = int(sparam.text)
        elif spname == 'BW':
            specbunch.BW = float(sparam.text)
        elif spname == 'M':
            specbunch.M = int(sparam.text)
        elif spname == 'N':
            specbunch.N = int(sparam.text)
        elif spname == 'f0':
            specbunch.f0 = float(sparam.text)
        elif spname == 'df':
            specbunch.df = float(sparam.text)
        elif spname.startswith('ChannelA'):
            RefNMatch = re.match(r'ChannelA\[(\d+)\]', spname)
            chn_num = int(RefNMatch.group(1))
            specbunch.channelA[chn_num] = sparam.text
            specbunch.channels[chn_num] = sparam.text
        elif spname.startswith('ChannelB'):
            RefNMatch = re.match(r'ChannelB\[(\d+)\]', spname)
            chn_num = int(RefNMatch.group(1))
            specbunch.channelB[chn_num] = sparam.text
            specbunch.channels[chn_num] = sparam.text
        else:
            pass

    chn_dict = specbunch.setdefault('channelA', {})
    specbunch.channelA_inv = {}
    for idx, chn_name in chn_dict.items():
        specbunch.channelA_inv[chn_name] = idx

    chn_dict = specbunch.setdefault('channelB', {})
    specbunch.channelB_inv = {}
    for idx, chn_name in chn_dict.items():
        specbunch.channelB_inv[chn_name] = idx

    chn_dict = specbunch.setdefault('channels', {})
    specbunch.channels_inv = {}
    for idx, chn_name in chn_dict.items():
        specbunch.channels_inv[chn_name] = idx

    ####
    ##Now interpret the data
    array_node = LW_node.findall('Array')[0]
    dims = [int(d.text) for d in array_node.findall('Dim')]
    streambuff = base64.b64decode(array_node.findall('Stream')[0].text)
    stream_type = array_node.attrib['Type']
    if stream_type == 'float':
        data = np.frombuffer(streambuff, dtype='f4')
    elif stream_type == 'floatComplex':
        data = np.frombuffer(streambuff, dtype='c8')
    data = data.reshape(*dims)

    specbunch.data_raw = data
    specbunch.FHz = np.real(data[:, 0])
    specbunch.coeffs = data[:, 1:]

    if entry_type == 'CoherenceCoefficients':
        specbunch.coeffs = np.real(specbunch.coeffs)

    #specbunch.FHz = data[:N].real
    if specbunch.subtype_raw == 0:
        specbunch.subtype = "1-D fixed bin spacing histogram"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 1:
        specbunch.subtype = "1-D variable bin spacing histogram"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 2:
        specbunch.subtype = "2-D fixed bin spacing histogram"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 3:
        specbunch.subtype = "2-D variable bin spacing histogram"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 4:
        specbunch.subtype = "3-D fixed bin spacing histogram"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 5:
        specbunch.subtype = "3-D varibale bin spacing histogram"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 6:
        specbunch.subtype = "1-D fixed bin spacing histogram with errors"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 7:
        specbunch.subtype = "1-D variable bin spacing histogram with errors"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 8:
        specbunch.subtype = "2-D fixed bin spacing histogram with errors"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 9:
        specbunch.subtype = "2-D variable bin spacing histogram with errors"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 10:
        specbunch.subtype = "3-D fixed bin spacing histogram with errors"
        specbunch.type_name = entry_type
    elif specbunch.subtype_raw == 11:
        specbunch.subtype = "3-D variable bin spacing histogram with errors"
        specbunch.type_name = entry_type
    else:
        specbunch.subtype = "unknown"
    return specbunch


