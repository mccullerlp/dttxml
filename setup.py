#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
import os
import sys
import setup_helper

from setuptools import find_packages, setup

version = '1.1.0'
cmdclass = setup_helper.version_checker(version, 'dttxml')


setup(
    name='dttxml',
    version=version,
    url='',
    author='Lee McCuller',
    author_email='Lee.McCuller@ligo.org',
    description=(
        'Extract data from LIGO Diagnostics test tools XML format. Formerly dtt2hdf.'
    ),
    license = 'Apache v2',
    packages=find_packages(exclude=['doc']),
    extras_require   ={
        "hdf" : ["h5py"],
    },
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dtt2hdf=dttxml.dtt2hdf:main',
        ]},
    cmdclass       = cmdclass,
    zip_safe       = True,
    keywords = 'LIGO dtt diagnostics file-reader',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
