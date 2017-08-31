#!/usr/bin/env python
"""
"""
import subprocess
import tempfile
import os

from .diag_clear import diag_clear


class DiagCrash(RuntimeError):
    pass


script_template = (
"""
restore {file_in}
run -wq
save {file_out}
"""
)

def diag_run(
        f_in,
        f_out,
        crash_repeat = 3,
        clear = None,
):
    converted_diag_f = tempfile.NamedTemporaryFile(suffix = '.xml')
    if f_in == '-':
        infile_txt = sys.stdin.read()
    else:
        with open(f_in) as infile:
            infile_txt = infile.read()
    #can transform the input file arbitrarily
    #infile_txt = infile_txt.replace(*settings.replace_call)
    converted_diag_f.write(infile_txt)
    del infile_txt
    converted_diag_f.file.flush()
    script_f = tempfile.NamedTemporaryFile(suffix = '.diag')
    script_f.file.write("open\n")
    script_f.file.write(
        script_template.format(
            file_in = converted_diag_f.name,
            file_out = f_out
        )
    )
    script_f.file.write("exit\n")
    script_f.file.flush()
    num_crashes = 0
    try:
        while True:
            diag_process = subprocess.Popen(["diag", "-f", script_f.name])
            diag_process.wait()
            if diag_process.returncode == 0:
                return 0
            elif diag_process.returncode > 0:
                return diag_process.returncode
            else:
                num_crashes += 1
                if num_crashes > crash_repeat:
                    raise DiagCrash()
                else:
                    continue
    except Exception:
        if clear is not None:
            diag_clear(clear)
        raise
    except KeyboardInterrupt:
        if clear is not None:
            diag_clear(clear)
        raise
    return


if __name__=='__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(prog='autodiag')
    parser.add_argument(
        '-r','--repeat',
        type=int,
        default=3,
        help='Repeat Measurement on crash'
    )
    parser.add_argument(
        '-c','--clear',
        type=int,
        default=None,
        help='Clear this DCU on error or interrrupt'
    )
    parser.add_argument(
        'from_file',
        help = 'source file to run',
    )
    parser.add_argument(
        'to_file',
        help = 'File to store result',
        default = None,
    )
    args = parser.parse_args()
    if args.to_file is None:
        args.to_file = args.from_file

    try:
        retval = diag_run(
            args.from_file,
            args.to_file,
            crash_repeat = args.repeat,
            clear = args.clear,
        )
    except DiagCrash:
        sys.exit(-1)
    sys.exit(retval)






