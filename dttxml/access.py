"""
"""
import numpy as np
from .parse import dtt_read


class DiagMeasurementHolder(object):
    _copy_elements = ('gps_second', 'window', 'averages', 'BW')

    gps_second  = None
    window      = None
    averages    = None
    BW          = None
    diag_access = None

    def _metadata_mirror(self, other):
        for attr_name in self._copy_elements:
            setattr(self, attr_name, getattr(other, attr_name))
        return

    def metadata_check(self, other):
        for attr_name in self._copy_elements:
            a = getattr(self, attr_name)
            b = getattr(other, attr_name)
            if a != b:
                raise RuntimeError(
                    ("Metadata field {0} doesn't match ({1} != {2})"
                     ).format(attr_name, a, b)
                )
        return

    @property
    def utc_time(self):
        """
        Add the GPS to UTC epoch time difference, with the leap seconds included
        """
        return self.gps_second + 315964784


class DiagFreqMeasurementHolder(DiagMeasurementHolder):
    def _metadata_mirror(self, other):
        super(DiagFreqMeasurementHolder, self)._metadata_mirror(other)
        self.FHz = other.FHz
        return

    def metadata_check(self, other):
        super(DiagFreqMeasurementHolder, self).metadata_check(other)
        if not all(other.FHz == self.FHz):
            raise RuntimeError("Freqs supposed to be the same")
        return


class DiagCoherenceHolder(DiagFreqMeasurementHolder):
    def __init__(self, daccess, chn1, chn2):
        self.daccess = daccess
        self.chn1 = chn1
        self.chn2 = chn2
        try:
            chn1_coh = self.daccess.results['COH'][chn1]
            self._metadata_mirror(chn1_coh)
            idx = chn1_coh.channelB_inv[chn2]
            self.coh = chn1_coh.coherence[idx].reshape(-1)
        except KeyError:
            chn2_coh = self.daccess.results['COH'][chn2]
            self._metadata_mirror(chn2_coh)
            idx = chn2_coh.channelB_inv[chn1]
            self.coh = chn2_coh.coherence[idx].reshape(-1)

    _coh_phased = None
    @property
    def coh_phased(self):
        if self._coh_phased is not None:
            return self._coh_phased
        m_csd = self.daccess.csd(self.chn1, self.chn2)
        self.metadata_check(m_csd)
        self._coh_phased = self.coh * m_csd.csd / abs(m_csd.csd)
        return self._coh_phased

    @property
    def statistical_minimum(self):
        return 1/self.averages**.5


class DiagCSDHolder(DiagFreqMeasurementHolder):
    def __init__(self, daccess, chn1, chn2):
        self.daccess = daccess
        self.chn1 = chn1
        self.chn2 = chn2
        try:
            chn1_csd = self.daccess.results['CSD'][chn1]
            self._metadata_mirror(chn1_csd)
            idx = chn1_csd.channelB_inv[chn2]
            self.csd = chn1_csd.CSD[idx].reshape(-1)
        except KeyError:
            chn2_csd = self.daccess.results['CSD'][chn2]
            self._metadata_mirror(chn2_csd)
            idx = chn2_csd.channelB_inv[chn1]
            self.csd = chn2_csd.CSD[idx].reshape(-1)


class DiagASDHolder(DiagFreqMeasurementHolder):
    def __init__(self, daccess, chn):
        self.daccess = daccess
        self.chn = chn
        chn_asd = self.daccess.results['PSD'][chn]
        self._metadata_mirror(chn_asd)
        self.asd = chn_asd.PSD.reshape(-1)


class DiagXferHolder(DiagFreqMeasurementHolder):
    def __init__(self, daccess, chn_num, chn_den):
        self.daccess = daccess
        self.chn_num = chn_num
        self.chn_den = chn_den

        self.xfer = None
        try:
            self.chn_den_TF = self.daccess.results['TF'][self.chn_den]
            self._metadata_mirror(self.chn_den_TF)
            idx = self.chn_den_TF.channelB_inv[self.chn_num]
            self.xfer = self.chn_den_TF.xfer[idx].reshape(-1)
        except KeyError:
            pass

        if self.xfer is None:
            try:
                self.chn_num_TF = self.daccess.results['TF'][self.chn_num]
                self._metadata_mirror(self.chn_num_TF)
                idx = self.chn_num_TF.channelB_inv[self.chn_den]
                self.xfer = 1./self.chn_num_TF.xfer[idx].reshape(-1)
            except KeyError:
                pass

        #if the measurment aborts before it completes, it pads the freq data with zeros
        #if self.xfer is not None:
            #freq_good_idx = self.FHz > 0.
            #self.xfer = self.xfer[freq_good_idx]
            #self.FHz = self.FHz[freq_good_idx]

        if self.xfer is None:
            try:
                self._metadata_mirror(self.csd_obj)
                self.metadata_check(self.asd_den_obj)
                self.xfer = self.csd_obj.csd / self.asd_den_obj.asd**2
            except KeyError:
                raise
                raise RuntimeError("Diag file does not seem to carry this xfer function")

    _coh_obj = None
    @property
    def coh_obj(self):
        if self._coh_obj is not None:
            return self._coh_obj
        self._coh_obj = self.daccess.coherence(self.chn_num, self.chn_den)
        self.metadata_check(self._coh_obj)
        return self._coh_obj

    @property
    def coh(self):
        return self.coh_obj.coh

    @property
    def SNR_estimate(self):
        return self.coh**2/(1-self.coh**2) * self.averages
        try:
            P = (self.asd_num / self.asd_den)**2
            M = self.csd / self.asd_den**2
            single_snr = abs(M)**2/(P - abs(M)**2)
            maxed_vals = (single_snr > 10e6) | ~np.isfinite(single_snr) | (single_snr < 0)
            single_snr[maxed_vals] = 10e6
            #print max(single_snr)
            #print min(single_snr)
            return single_snr * self.averages
        except KeyError:
            pass
        return self.coh**2/(1-self.coh**2)

    _csd_obj = None
    @property
    def csd_obj(self):
        if self._csd_obj is None:
            self._csd_obj = self.daccess.csd(self.chn_num, self.chn_den)
        return self._csd_obj

    @property
    def csd(self):
        return self.csd_obj.csd

    _asd_num_obj = None
    @property
    def asd_num_obj(self):
        if self._asd_num_obj is not None:
            return self._asd_num_obj
        self._asd_num_obj = self.daccess.asd(self.chn_num)
        self.metadata_check(self._asd_num_obj)
        return self._asd_num_obj

    @property
    def asd_num(self):
        return self.asd_num_obj.asd

    _asd_den_obj = None
    @property
    def asd_den_obj(self):
        if self._asd_num_obj is None:
            self._asd_den_obj = self.daccess.asd(self.chn_den)
        return self._asd_den_obj

    @property
    def asd_den(self):
        return self._asd_den_obj.asd


class DiagXferViaHolder(DiagFreqMeasurementHolder):

    def __init__(self, daccess, chn_num, chn_den, chn_via):
        self.daccess = daccess
        self._xfer_num_obj = self.daccess.xfer(chn_num, chn_via)
        self._xfer_den_obj = self.daccess.xfer(chn_den, chn_via)
        self._metadata_mirror(self._xfer_num_obj)
        self.metadata_check(self._xfer_den_obj)
        self.xfer = self._xfer_num_obj.xfer / self._xfer_den_obj.xfer

    @property
    def SNR_estimate(self):
        snr_num = self._xfer_num_obj.SNR_estimate
        snr_den = self._xfer_den_obj.SNR_estimate
        return 1/(1/snr_den + 1/snr_num)

    _coh_nv_obj = None
    @property
    def coh_nv_obj(self):
        if self._coh_nv_obj is not None:
            return self._coh_nv_obj
        self._coh_nv_obj = self.daccess.coherence(self.chn1, self.chn2)
        self.metadata_check(self._coh_nv_obj)
        return self._coh_nv_obj

    @property
    def coh_nv(self):
        return self._coh_nv_obj.coh

    _coh_dv_obj = None
    @property
    def coh_dv_obj(self):
        if self._coh_dv_obj is not None:
            return self._coh_dv_obj
        self._coh_dv_obj = self.daccess.coherence(self.chn1, self.chn2)
        self.metadata_check(self._coh_dv_obj)
        return self._coh_dv_obj

    @property
    def coh_dv(self):
        return self._coh_dv_obj.coh

    _coh_nd_obj = None
    @property
    def coh_nd_obj(self):
        if self._coh_nd_obj is not None:
            return self._coh_nd_obj
        self._coh_nd_obj = self.daccess.coherence(self.chn1, self.chn2)
        self.metadata_check(self._coh_nd_obj)
        return self._coh_nd_obj

    @property
    def coh_nd(self):
        return self._coh_nd_obj.coh

    @property
    def asd_num_obj(self):
        return self._xfer_num_obj.asd_num_obj

    @property
    def asd_via_obj(self):
        return self._xfer_num_obj.asd_den_obj

    @property
    def asd_den_obj(self):
        return self._xfer_den_obj.asd_num_obj

    @property
    def asd_num(self):
        return self.asd_num_obj.asd

    @property
    def asd_den(self):
        return self.asd_den_obj.asd

    @property
    def asd_via(self):
        return self.asd_via_obj.asd


class DiagSineResponseCoefficients(DiagMeasurementHolder):
    def __init__(self, daccess, chn_list, chn_wrt = None, freq_idx = 0):
        self.daccess = daccess
        self.chn_list = np.asarray(chn_list)
        self.chn_map = {}
        for idx, chn in enumerate(self.chn_list):
            self.chn_map[idx] = chn
            self.chn_map[chn] = idx
        self.chn_wrt = chn_wrt

        diag_TC = self.daccess.results['TransferCoefficients']
        diag_CC = self.daccess.results['CoherenceCoefficients']
        self._metadata_mirror(diag_TC)
        self.metadata_check(diag_CC)
        self.FHz = diag_TC.FHz[freq_idx]
        if not np.all(self.FHz == diag_CC.FHz[freq_idx]):
            raise RuntimeError("Tranfer and Coherence coefficient frequencies inconsistent")

        if chn_wrt is not None:
            diag_idx_wrt = diag_TC.channels_inv[chn_wrt]
            self.coeff_wrt = diag_TC.coeffs[freq_idx, diag_idx_wrt]
            self.coh_wrt = diag_CC.coeffs[freq_idx, diag_idx_wrt]
        else:
            self.coeff_wrt = 1.
            self.coh_wrt   = 1.

        self.coeffs = np.empty(len(self.chn_list), dtype = complex)
        self.coeffs_dict = {}
        self.cohs = np.empty(len(self.chn_list), dtype = float)
        self.cohs_dict = {}
        for idx, chn in enumerate(self.chn_list):
            diag_idx = diag_TC.channels_inv[chn]
            coeff = diag_TC.coeffs[freq_idx, diag_idx] / self.coeff_wrt
            self.coeffs[idx] = coeff
            self.coeffs_dict[chn] = coeff
            diag_idx = diag_CC.channels_inv[chn]
            coh = diag_CC.coeffs[freq_idx, diag_idx]
            self.cohs[idx] = coh
            self.cohs_dict[chn] = coh


class DiagHarmonicResponseCoefficients(DiagMeasurementHolder):
    def __init__(self, daccess, chn_list, chn_wrt = None, chn_wrt_freq = 1):
        self.daccess = daccess
        self.chn_list = np.asarray(chn_list)
        self.chn_map = {}
        for idx, chn in enumerate(self.chn_list):
            self.chn_map[idx] = chn
            self.chn_map[chn] = idx
        self.chn_wrt = chn_wrt
        self.chn_wrt_freq = chn_wrt_freq

        diag_HC = self.daccess.results['HarmonicCoefficients']
        self._metadata_mirror(diag_HC)
        self.FHz = diag_HC.FHz

        if chn_wrt is not None:
            diag_idx_wrt = diag_HC.channels_inv[chn_wrt]
            self.coeff_wrt = diag_HC.coeffs[chn_wrt_freq, diag_idx_wrt]
        else:
            self.coeff_wrt = 1.
            self.coh_wrt   = 1.
        fs = len(self.FHz)
        l = len(self.chn_list)
        self.coeffs = np.empty((l, fs), dtype = complex)
        self.coeffs_dict = {}
        self.coeffs_2x = np.empty(l, dtype = complex)
        self.coeffs_2x_dict = {}
        for idx, chn in enumerate(self.chn_list):
            diag_idx = diag_HC.channels_inv[chn]
            coeff = diag_HC.coeffs[:, diag_idx] / self.coeff_wrt
            self.coeffs[idx] = coeff
            self.coeffs_dict[chn] = coeff
            coeff_2x = coeff[2] / coeff[1]
            self.coeffs_2x[idx] = coeff_2x
            self.coeffs_2x_dict[chn] = coeff_2x


class DiagAccess(object):
    """
    Test watch
    """
    def __init__(
            self,
            fname,
    ):
        # Parse the file
        raw = dtt_read(fname)
        self.references = raw.references
        self.results    = raw.results

        # Add the reference traces to the externally-accessible results dict
        # Channel naming convention follows the DTT convention: "CHN_NAME(REF#)"
        for idx_ref, ref in self.references.items():
            type_ref = ref['type_name']
            if type_ref in ('PSD', 'CSD', 'COH', 'TF'):
                chn_ref = '{}(REF{})'.format(ref['channelA'], idx_ref)
                if type_ref not in self.results:
                    self.results[type_ref] = dict()
                self.results[type_ref][chn_ref] = ref

    def coherence(self, chn1, chn2):
        return DiagCoherenceHolder(self, chn1, chn2)

    def coh(self, chn1, chn2):
        return DiagCoherenceHolder(self, chn1, chn2)

    def csd(self, chn1, chn2):
        return DiagCSDHolder(self, chn1, chn2)

    def asd(self, chn):
        return DiagASDHolder(self, chn)

    def xfer(self, chn_num, chn_den):
        return DiagXferHolder(self, chn_num, chn_den)

    def xfer_via(self, chn_num, chn_den, chn_via):
        return DiagXferViaHolder(self, chn_num, chn_den, chn_via)

    def sine_response(self, chn_list, chn_wrt = None, freq_idx = 0):
        return DiagSineResponseCoefficients(
            self,
            chn_list = chn_list,
            chn_wrt = chn_wrt,
            freq_idx = freq_idx
        )

    def harmonic_response(self, chn_list, chn_wrt = None):
        return DiagHarmonicResponseCoefficients(
            self,
            chn_list = chn_list,
            chn_wrt = chn_wrt,
        )

    def channels(self):
        channels_A = set()
        channels_B = set()
        for res_key, res_obj in self.results.items():
            if res_key in (
                'HarmonicCoefficients',
                'CoherenceCoefficients',
                'TransferCoefficients',
                'TransferMatrix',
            ):
                channels_A.update(list(res_obj.channels.values()))
            if res_key in ('TS',):
                channels_A.update(list(res_obj.keys()))
            else:
                for chn_key, chn_obj in res_obj.items():
                    channels_A.add(chn_key)
                    channels_B.update(list(chn_obj.channelB_inv.keys()))
        #reduce the B channels to being the unique ones
        channels_B = channels_B - channels_A
        return channels_A, channels_B

    def channels_print(self):
        channels_A, channels_B = self.channels()
        channels_A = sorted(channels_A)
        print("A-Channels:")
        for chn in channels_A:
            print("\t", chn)
        if channels_B:
            channels_B = sorted(channels_B)
            print("Non-A, B-Channels:")
            for chn in channels_B:
                print("\t", chn)


