#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
import os
import sys
from distutils.sysconfig import get_python_lib
import setup_helper

from setuptools import find_packages, setup


version = '1.0.1'
cmdclass = setup_helper.version_checker(version, 'dtt2hdf')


setup(
    name='dtt2hdf',
    version=version,
    url='',
    author='Lee McCuller',
    author_email='Lee.McCuller@ligo.org',
    description=(
        'Extract data from LIGO Diagnostics test tools XML format.'
    ),
    license = 'Apache v2',
    packages=find_packages(exclude=['doc']),
    #include_package_data=True,
    #scripts=[''],
    entry_points={
        'console_scripts': [
            'dtt2hdf=dtt2hdf.dtt2hdf:main',
        ]},
    install_requires=[
        'declarative[hdf]',
    ],
    cmdclass       = cmdclass,
    extras_require = {},
    zip_safe       = False,
    keywords = 'LIGO diagnostics file reader',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

