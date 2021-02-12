
import base64
import numpy as np
from .bunch import Bunch
import re
#import xml.etree.cElementTree as etree


def parse_spectrum(LW_node):
    specbunch = Bunch()
    specbunch.channelB = Bunch()
    specbunch.channelB_inv = Bunch()

    for sparam in LW_node.findall('Time'):
        if sparam.attrib["Name"] == 't0':
            specbunch.gps_second = float(sparam.text)
    for sparam in LW_node.findall('Param'):
        spname = sparam.attrib["Name"]
        if spname == 'Subtype':
            subtype_raw = int(sparam.text)
        elif spname == 'Window':
            window_raw = int(sparam.text)
            specbunch.window = {
                0 : 'Uniform',
                1 : 'Hanning',
                2 : 'Flat-top',
                3 : 'Welch',
                4 : 'Bartlett',
                5 : 'BMH',
                6 : 'Hamming',
                7 : 'Kaiser',
            }.get(window_raw, "unknown")
        elif spname == 'AverageType':
            avgtype_raw = int(sparam.text)
            specbunch.avgtype = {
                0 : 'Fixed',
                1 : 'Exponential',
                2 : 'Single',
            }.get(avgtype_raw, "unknown")
        elif spname == 'Averages':
            specbunch.averages = int(sparam.text)
        elif spname == 'M':
            M = int(sparam.text)
        elif spname == 'N':
            N = int(sparam.text)
        elif spname == 'f0':
            specbunch.f0 = float(sparam.text)
        elif spname == 'BW':
            specbunch.BW = float(sparam.text)
        elif spname == 'df':
            specbunch.df = float(sparam.text)
        elif spname == 'ChannelA':
            specbunch.channelA = sparam.text
        elif spname.startswith('ChannelB'):
            RefNMatch = re.match(r'ChannelB\[(\d+)\]', spname)
            chn_num = int(RefNMatch.group(1))
            specbunch.channelB[chn_num] = sparam.text
        else:
            pass

    chanB = specbunch.channelB
    sarg = np.argsort(list(chanB.keys()))
    if len(sarg) > 0:
        specbunch.channelB = np.take(list(chanB.values()), sarg)
        for idx, chn_name in enumerate(specbunch.channelB):
            specbunch.channelB_inv[chn_name] = idx

    ####
    ##Now interpret the data
    streambuff = base64.b64decode(LW_node.findall('Array/Stream')[0].text)

    if subtype_raw == 0:
        specbunch.subtype = 'FFT in format (Y)'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.FHz = np.linspace(specbunch.f0, specbunch.f0 + specbunch.df*(N-1), N)
        specbunch.type_name = 'FFT'
        specbunch.FFT = data.reshape(M, -1)
    elif subtype_raw == 1:
        specbunch.subtype = 'power spectral density in format (Y)'
        specbunch.type_name = 'PSD'
        data = np.frombuffer(streambuff, dtype='f4')
        specbunch.FHz = np.linspace(specbunch.f0, specbunch.f0 + specbunch.df*(N-1), N)
        specbunch.PSD = data.reshape(M, -1)
    elif subtype_raw == 2:
        specbunch.subtype = 'cross-power spectrum in format (Y)'
        specbunch.type_name = 'CSD'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.FHz = np.linspace(specbunch.f0, specbunch.f0 + specbunch.df*(N-1), N)
        specbunch.CSD = data.reshape(M, -1)
    elif subtype_raw == 3:
        specbunch.subtype = 'coherence in format (Y)'
        specbunch.type_name = 'COH'
        data = np.frombuffer(streambuff, dtype='f4')
        specbunch.FHz = np.linspace(specbunch.f0, specbunch.f0 + specbunch.df*(N-1), N)
        specbunch.coherence = data.reshape(M, -1)
    elif subtype_raw == 4:
        specbunch.subtype = 'FFT in format (f, Y)'
        specbunch.type_name = 'FFT'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.FHz = data[:N]
        specbunch.FFT = data[N:].reshape(M, -1)
    elif subtype_raw == 5:
        specbunch.subtype = 'power spectral density in format (f,Y)'
        specbunch.type_name = 'PSD'
        data = np.frombuffer(streambuff, dtype='f4')
        specbunch.FHz = data[:N]
        specbunch.PSD = data[N:].reshape(M, -1)
    elif subtype_raw == 6:
        specbunch.subtype = 'cross-power spectrum in format (f,Y)'
        specbunch.type_name = 'CSD'
        data = np.frombuffer(streambuff, dtype='c8')
        specbunch.FHz = data[:N].real
        specbunch.CSD = data[N:].reshape(M, -1)
    elif subtype_raw == 7:
        specbunch.subtype = 'coherence in format (f,Y)'
        specbunch.type_name = 'COH'
        data = np.frombuffer(streambuff, dtype='f4')
        specbunch.FHz = data[:N]
        specbunch.coherence = data[N:].reshape(M, -1)
    else:
        specbunch.subtype = "unknown"
    return specbunch

