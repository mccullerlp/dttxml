"""
"""
from __future__ import print_function, division

import warnings
import numpy as np

from .deep_bunch import DeepBunch
from .access import DiagAccess


class DiagFileError(ValueError):
    pass


def dtt2bunch(
    fpath,
    channels         = None,
    no_remap         = True,
    channel_map      = {},
    channels_exclude = set(),
    verbose          = False,
):
    try:
        daccess = DiagAccess(fpath)
    except Exception:
        raise DiagFileError("Diag File malformed (xml syntax error)")
    def insert_refs(dbunch):
        for k, v in daccess.references.items():
            dbunch.REFS[str(k)] = v

    Achns, Bchns = daccess.channels()
    allchns_raw = set(Achns)
    allchns_raw.update(Bchns)
    allchns_raw = list(allchns_raw)
    allchns_raw.sort()

    spectra_bunch = DeepBunch()
    spectra_bunch.type = 'spectra',
    #PSD type
    xsd_current = None
    xsd_prev    = None
    xfer_current = None
    xfer_prev    = None
    for idx_A in range(len(allchns_raw)):
        chn_A_raw = allchns_raw[idx_A]
        if chn_A_raw in channels_exclude:
            continue
        try:
            chn_A = channel_map[chn_A_raw]
        except KeyError:
            if no_remap:
                chn_A = chn_A_raw
            else:
                continue
        if channels is not None and chn_A not in channels:
            continue
        if chn_A in channels_exclude:
            continue
        for idx_B in range(len(allchns_raw)):
            chn_B_raw = allchns_raw[idx_B]
            if chn_B_raw in channels_exclude:
                continue
            try:
                chn_B = channel_map[chn_B_raw]
            except KeyError:
                if no_remap:
                    chn_B = chn_B_raw
                else:
                    continue
            if channels is not None and chn_B not in channels:
                continue

            if chn_B in channels_exclude:
                continue

            if verbose:
                print(chn_A, chn_B)
            if chn_A == chn_B:
                try:
                    xsd_current = daccess.asd(chn_A_raw)
                    value = xsd_current.asd
                    prev = spectra_bunch.ASD.setdefault(chn_A, value)
                    if prev is not value:
                        if not all(prev == value):
                            warnings.warn((
                                "Multiple Mappings from raw to real channel are not consistent for ASD of chn: {0}"
                            ).format(chn_A)
                            )
                except KeyError:
                    continue
            else:
                try:
                    chn_A_dict = spectra_bunch.CSD.setdefault(chn_A, {})
                    xsd_current = daccess.csd(chn_A_raw, chn_B_raw)
                    value = xsd_current.csd
                    prev = chn_A_dict.setdefault(chn_B, value)
                    if prev is not value:
                        if not all(prev == value):
                            warnings.warn((
                                "Multiple Mappings from raw to real channel are not consistent for CSD between chns: {0} and {1}"
                            ).format(chn_A, chn_B)
                            )
                    if verbose:
                        print("GOOD: ", chn_A, chn_B)
                except KeyError:
                    pass

                try:
                    chn_A_dict = spectra_bunch.XFER.setdefault(chn_A, {})
                    xfer_current = daccess.xfer(chn_A_raw, chn_B_raw)
                    value = xfer_current.xfer
                    prev = chn_A_dict.setdefault(chn_B, value)
                    if prev is not value:
                        if not all(prev == value):
                            warnings.warn((
                                "Multiple Mappings from raw to real channel are not consistent for XFER between chns: {0} and {1}"
                            ).format(chn_A, chn_B)
                            )
                except KeyError:
                    print("BAD: ", chn_A, chn_B)
                    continue

                chn_A_dict = spectra_bunch.COH.setdefault(chn_A, {})
                value = daccess.coh(chn_A_raw, chn_B_raw).coh
                prev = chn_A_dict.setdefault(chn_B, value)
                if prev is not value:
                    if not all(prev == value):
                        warnings.warn((
                            "Multiple Mappings from raw to real channel are not consistent for COH between chns: {0} and {1}"
                        ).format(chn_A, chn_B)
                        )
                chn_A_dict = spectra_bunch.XFER_SNR_EST.setdefault(chn_A, {})
                value = daccess.xfer(chn_A_raw, chn_B_raw).SNR_estimate
                value = np.maximum(value**2 - 1, 0)
                prev = chn_A_dict.setdefault(chn_B, value)
                if prev is not value:
                    if not all(prev == value):
                        warnings.warn((
                            "Multiple Mappings from raw to real channel are not consistent for XFER_SNR_EST between chns: {0} and {1}"
                        ).format(chn_A, chn_B)
                        )
            if xsd_prev is not None:
                xsd_prev.metadata_check(xsd_current)
            xsd_prev = xsd_current

            if xfer_prev is not None:
                xfer_prev.metadata_check(xfer_current)
            xfer_prev = xfer_current

    if xsd_current is not None:
        spectra_bunch.gps_second   = xsd_current.gps_second,
        spectra_bunch.window       = xsd_current.window,
        spectra_bunch.averages     = xsd_current.averages,
        spectra_bunch.BW           = xsd_current.BW,
        spectra_bunch.FHz          = xsd_current.FHz.squeeze(),
        insert_refs(spectra_bunch)
        return spectra_bunch
    elif xfer_current is not None:
        spectra_bunch.gps_second   = xfer_current.gps_second,
        #spectra_bunch.window       = xfer_current.window,
        spectra_bunch.averages     = xfer_current.averages,
        #spectra_bunch.BW           = xfer_current.BW,
        spectra_bunch.FHz          = xfer_current.FHz.squeeze(),
        insert_refs(spectra_bunch)
        return spectra_bunch

    TS_bunch = DeepBunch()
    TS_bunch.type = 'timeseries',
    try:
        diag_TS = daccess.results.TS
    except (KeyError, AttributeError):
        raise DiagFileError("No Channels Found in TS")
    ts_current = None
    ts_prev = None
    for idx_A in range(len(allchns_raw)):
        chn_A_raw = allchns_raw[idx_A]
        if chn_A_raw in channels_exclude:
            continue
        try:
            chn_A = channel_map[chn_A_raw]
        except KeyError:
            if no_remap:
                chn_A = chn_A_raw
            else:
                continue
        if channels is not None and chn_A not in channels:
            continue
        if chn_A in channels_exclude:
            continue
        try:
            ts_current = diag_TS[chn_A_raw]
        except KeyError:
            pass
        else:
            value = ts_current.timeseries
            prev = TS_bunch.TS.setdefault(chn_A, value)
            ts_prev = ts_current
            if prev is not value:
                if not all(prev == value):
                    warnings.warn((
                        "Multiple Mappings from raw to real channel are not consistent for TS of chn: {0}"
                    ).format(chn_A)
                    )
    if ts_current is not None:
        TS_bunch.gps_second    = ts_current.gps_second,
        TS_bunch.time_delay_s  = ts_current.time_delay_s,
        TS_bunch.avgtype       = ts_current.avgtype,
        TS_bunch.dt            = ts_current.dt,
        insert_refs(TS_bunch)
        return TS_bunch
    else:
        raise DiagFileError("No Channels Found in TS")


