#!/usr/bin/env python
"""
"""
import subprocess
import tempfile
import os


script_reset_template = (
"""
open
awg clear {dcuid} *
tp clear {dcuid} *
exit
"""
)


def diag_clear(dcuid):
    script_f = tempfile.NamedTemporaryFile(suffix = '.diag')
    script_f.file.write(
        script_reset_template.format(dcuid = dcuid)
    )
    script_f.file.flush()
    diag_process = subprocess.Popen(["diag", "-f", script_f.name])
    return diag_process.wait()


if __name__=='__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dcuid',
        type=int,
        help = 'DCUID to reset',
    )
    args = parser.parse_args()
    retval = diag_clear(args.dcuid)
    sys.exit(retval)






