"""
Utility to convert diaggui XML output into easily readable and introspectable HDF5 [.h5] file formats. HDF5 may be read from python using the h5py module or in matlab using the commands h5read, h5disp and similar (refer to http://www.mathworks.com/help/matlab/high-level-functions.html).

If you have hdf5 command line tools (h5ls) then you can list the datasets with

h5ls -r filename.h5
"""
import argparse
import os.path as path

import h5py
from .declarative.hdf_deep_bunch import HDFDeepBunch

from .dtt2bunch import dtt2bunch


def main(args = None):
    parser = argparse.ArgumentParser(
        prog = 'dtt2hdf5',
        description=__doc__,
    )

    parser.add_argument(
        #'--control-A',
        dest     = 'file_from',
        metavar  = 'from-file',
        type     = str,
        help     = 'diaggui xml file to parse'
    )

    parser.add_argument(
        #'--control-A',
        dest     = 'file_to',
        metavar  = 'to-file',
        type     = str,
        nargs    = '?',
        default  = None,
        help     = 'HDF5 file to insert to. Will rename the input to a .h5 if not given.'
    )

    parser.add_argument(
        '-q, --quiet',
        dest     = 'quiet',
        action   = 'store_true',
        help     = 'Quiet the output',
    )

    args = parser.parse_args(args = args)

    ffrom_base, ffrom_ext = path.splitext(args.file_from)
    if args.file_to is None:
        file_to = ffrom_base + '.h5'
    else:
        file_to = args.file_to

    if not args.quiet:
        print(file_to)

    #parser.add_argument(
    #    '-E',
    #    dest='control_A',
    #    type=int,
    #    required=True,
    #    help='Exclude Channels'
    #)

    diag_DB = dtt2bunch(fpath = args.file_from, verbose = not args.quiet)

    #write the file out, it is cleared first due to the 'w' flag. Could do this using append operations with 'a'
    with h5py.File(file_to, 'w') as F_hdf:
        hdf = HDFDeepBunch(F_hdf, writeable = True)
        hdf.update_recursive(diag_DB)


if __name__ == '__main__':
    main()
