try:
    from framecpp import frameCPP
except ImportError:
    frameCPP = None

if frameCPP is None:
    try:
        import frameCPP
    except ImportError:
        pass

if frameCPP is None:
    from LDAStools import frameCPP

class FrameCPPDataReader:
    def __init__(self, fname):
        self.IFrame = frameCPP.IFrameFStream(fname)
        self.TOC = self.IFrame.GetTOC()
        self.channel_names = frozenset(iter(self.TOC.GetADC().keys()))

    def sample_rate_get(self, channel_name):
        """
        :return: sample rate of channel or None if channel doesn't exist
        """
        if channel_name in self.channel_names:
            ADC = self.IFrame.ReadFrAdcData(0, channel_name)
            return ADC.GetSampleRate()
        else:
            return None

    def timeseries_get(self, channel_name):
        ADC = self.IFrame.ReadFrAdcData(0, channel_name)
        ADC_data = ADC.RefData()
        data = ADC_data[0]
        return data.GetDataArray()

    def len_get(self, channel_name):
        ADC = self.IFrame.ReadFrAdcData(0, channel_name)
        ADC_data = ADC.RefData()
        data = ADC_data[0]
        return data.GetDim(0).GetNx()
