"""
"""

import base64
import numpy as np
from .bunch import Bunch


def parse_timeseries(
    LW_node,
):
    timebunch = Bunch()

    for sparam in LW_node.findall('Time'):
        if sparam.attrib["Name"] == 't0':
            timebunch.gps_second = float(sparam.text)
    for sparam in LW_node.findall('Param'):
        spname = sparam.attrib["Name"]
        if spname == 'Subtype':
            timebunch.subtype_raw = int(sparam.text)
        elif spname == 'AverageType':
            timebunch.avgtype_raw = int(sparam.text)
            timebunch.avgtype = {
                0 : 'Fixed',
                1 : 'Exponential',
                2 : 'Single',
            }.get(timebunch.avgtype_raw, "unknown")
        elif spname == 'Averages':
            timebunch.averages = int(sparam.text)
        elif spname == 'N':
            timebunch.N = int(sparam.text)
        elif spname == 'f0':
            timebunch.f0 = float(sparam.text)
        elif spname == 'dt':
            timebunch.dt = float(sparam.text)
        elif spname == 'Channel':
            timebunch.channel = sparam.text
        elif spname == "Decimation1":
            timebunch.decimation1 = int(sparam.text)
        elif spname == "DecimationType":
            timebunch.decimation_rawtype = int(sparam.text)
        elif spname == "DecimationDelay":
            timebunch.decimation_delay_s = float(sparam.text)
        elif spname == "TimeDelay":
            timebunch.time_delay_s = float(sparam.text)
        elif spname == "DelayTaps":
            timebunch.delay_taps_num = int(sparam.text)
        elif spname == "DecimationFilter":
            timebunch.decimation_filter = sparam.text
        else:
            pass

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

    timebunch.data_raw = data

    timebunch.type_name = 'TS'
    if timebunch.subtype_raw == 0:
        timebunch.subtype = "normal time series in format (Y)"
        timebunch.timeseries = data
    elif timebunch.subtype_raw == 1:
        timebunch.subtype = "down-converted time series in format (Y)"
        timebunch.timeseries = data
    elif timebunch.subtype_raw == 2:
        timebunch.subtype = "averaged time series in format (Y)"
        timebunch.timeseries = data
    elif timebunch.subtype_raw == 3:
        timebunch.subtype = "averaged time series in format (mean, std. dev., min., max., rms)"
    elif timebunch.subtype_raw == 4:
        timebunch.subtype = "normal time series in format (t,Y)"
    elif timebunch.subtype_raw == 5:
        timebunch.subtype = "down-converted time series in format (t,Y)"
    elif timebunch.subtype_raw == 6:
        timebunch.subtype = "averaged time series in format (t,Y)"
    elif timebunch.subtype_raw == 7:
        timebunch.subtype = "averaged time series in format (t, mean, std. dev., min., max., rms)"
    else:
        timebunch.subtype = "unknown"
        timebunch.type_name = "unknown"
    return timebunch


