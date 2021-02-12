#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

from .bunch import Bunch
from .deep_bunch import DeepBunch
from .overridable_object import OverridableObject

def first_non_none(*args):
    for a in args:
        if a is not None:
            return a
    return None
