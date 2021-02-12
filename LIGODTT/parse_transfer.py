"""
"""
import base64
import numpy as np
import re

from .bunch import Bunch


def parse_transfer(LW_node):
    specbunch = Bunch()

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
                0 : 'Uniform',
                1 : 'Hanning',
                2 : 'Flat-top',
                3 : 'Welch',
                4 : 'Bartlett',
                5 : 'BMH',
                6 : 'Hamming',
                7 : 'Kaiser',
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
            M = int(sparam.text)
        elif spname == 'N':
            N = int(sparam.text)
        elif spname == 'f0':
            specbunch.f0 = float(sparam.text)
        elif spname == 'df':
            specbunch.df = float(sparam.text)
        elif spname == 'ChannelA':
            specbunch.channelA = sparam.text
        elif spname.startswith('ChannelB'):
            RefNMatch = re.match(r'ChannelB\[(\d+)\]', spname)
            chn_num = int(RefNMatch.group(1))
            chn_map = specbunch.setdefault('channelB', {})
            chn_map[chn_num] = sparam.text
        else:
            pass


    chanB = specbunch.setdefault('channelB', {})
    sarg = np.argsort(list(chanB.keys()))
    specbunch.channelB = np.take(list(chanB.values()), sarg)
    specbunch.channelB_inv = {}
    for idx, chn_name in enumerate(specbunch.channelB):
        specbunch.channelB_inv[chn_name] = idx

    ####
    ##Now interpret the data
    streambuff = base64.b64decode(LW_node.findall('Array/Stream')[0].text)

    if specbunch.subtype_raw == 0:
        specbunch.subtype = 'transfer function B/A in format (Y)'
        specbunch.type_name = 'TF'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.xfer = data.reshape(M, -1)
    elif specbunch.subtype_raw == 1:
        specbunch.subtype = 'transfer function A in format (Y)'
        specbunch.type_name = 'STF'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.response = data.reshape(M, -1)
    elif specbunch.subtype_raw == 2:
        specbunch.subtype = 'coherence B/A in format (Y)'
        specbunch.type_name = 'COH'
        data = np.frombuffer(streambuff, dtype='f4')
        specbunch.coherence = data.reshape(M, -1)
    elif specbunch.subtype_raw == 3:
        specbunch.subtype = 'transfer function B/A in format (f,Y)'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.type_name = 'TF'
        specbunch.FHz = data[:N].real
        specbunch.xfer = data[N:].reshape(M, -1)
    elif specbunch.subtype_raw == 4:
        specbunch.subtype = 'transfer function A in format (f,Y)'
        specbunch.type_name = 'STF'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.FHz = data[:N].real
        specbunch.response = data[N:].reshape(M, -1)
    elif specbunch.subtype_raw == 5:
        specbunch.subtype = 'coherence B/A in format (f, Y)'
        specbunch.type_name = 'COH'
        data = np.frombuffer(streambuff, dtype='f4')
        specbunch.FHz = data[:N]
        specbunch.coherence = data[N:].reshape(M, -1)
    else:
        specbunch.subtype = "unknown"
    return specbunch

