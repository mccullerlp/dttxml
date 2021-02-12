"""
"""
import xml.etree.cElementTree as etree
import numpy as np
import re

from .bunch import Bunch
from .parse_transfer import parse_transfer
from .parse_spectrum import parse_spectrum
from .parse_timeseries import parse_timeseries
from .parse_coefficients import parse_coefficients


def coherence_TF_numerator_SNR(coherence, N_averages = None, rejection_ratio = 1.5):
    #limit it to about SNR of 2000 for numerical accuracy reasons
    #coherence = np.minimum(coherence, .9999999)
    coherence = np.minimum(coherence, .99999)
    single_snr = coherence**2 / (1 - coherence**2)
    if N_averages is None:
        return single_snr
    minimum_coh = 1/N_averages**.5
    snr = single_snr * N_averages**.5
    snr[coherence < minimum_coh * rejection_ratio ] = 0
    return snr


def entry_type_num(text):
    elines = list(text.splitlines())
    elines[0]
    match_ref = re.search(r'(\w+)\[(\d+)\].*', elines[0])
    if match_ref:
        return match_ref.group(1), match_ref.group(2)
    match_ref = re.search(r'(\w+).*', elines[0])
    if match_ref:
        return match_ref.group(1), None
    return elines[0]


def dtt_read(diag_file):
    references = {}
    results = {}

    diag_tree = etree.parse(diag_file)
    entries = {}

    for xml_node in diag_tree.getroot():
        if xml_node.attrib['Name'] == 'Index':
            for subentry in xml_node:
                match_ref = re.match(r'Entry\[(\d+)\]', subentry.attrib['Name'])
                if match_ref:
                    ref_num = int(match_ref.group(1))
                    entries[ref_num] = subentry.text

    for entry_text in entries.values():
        entry_type, entry_num = entry_type_num(entry_text)
        if entry_type in (
            'TransferCoefficients',
            'HarmonicCoefficients',
            'IntermodulationCoefficients',
            'CoherenceCoefficients',
            #'TransferMatrix,
        ):
            entry_parse = re.search(r'Name\s+=\s+(\w+.*);', entry_text)
            entry_node_name = entry_parse.group(1)
            for xml_node in diag_tree.getroot().findall('LIGO_LW'):
                if xml_node.attrib['Name'] == entry_node_name:
                    break
            else:
                print("WARNING XML is funky!")
            measurement = parse_coefficients(
                LW_node = xml_node,
                entry_type = entry_type,
                entry_num = entry_num,
                entry_text = entry_text,
            )
            old = results.setdefault(entry_type, measurement)
            assert(old == measurement)

    for xml_node in diag_tree.getroot():
        match_ref = re.match(r'Reference\[(\d+)\]', xml_node.attrib['Name'])
        if match_ref:
            ref_num = int(match_ref.group(1))
            typename = xml_node.attrib['Type']
            if typename == "TransferFunction":
                ref = parse_transfer(xml_node)
                references[ref_num] = ref
            elif typename == "Spectrum":
                ref = parse_spectrum(xml_node)
                references[ref_num] = ref
            elif typename == "TimeSeries":
                ref = parse_timeseries(xml_node)
                references[ref_num] = ref
        match_ref = re.match(r'Result\[(\d+)\]', xml_node.attrib['Name'])
        if match_ref:
            ref_num = int(match_ref.group(1))
            typename = xml_node.attrib['Type']
            ref = None
            if typename == "TransferFunction":
                ref = parse_transfer(xml_node)
            elif typename == "Spectrum":
                ref = parse_spectrum(xml_node)
            elif typename == "TimeSeries":
                ref = parse_timeseries(xml_node)
            if ref is not None:
                try:
                    if ref.type_name in ('COH', 'STF', 'TF', 'PSD', 'FFT', 'CSD'):
                        results.setdefault(ref.type_name, {})[ref.channelA] = ref
                    elif ref.type_name in ('TS',):
                        results.setdefault(ref.type_name, {})[ref.channel] = ref
                    else:
                        #Check that these routines aren't returning something unaccounted-for
                        assert(False)
                except KeyError:
                    continue

    Items = Bunch()
    Items.references = Bunch(references)
    Items.results = Bunch(results)
    return Items


