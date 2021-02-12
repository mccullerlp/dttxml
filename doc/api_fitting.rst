.. _api:

Fitting API
============

The library using a versioning scheme to preserve old heuristics in future versions. There will be an IIRrational.vN submodule that is **larger** Than the current full version number. This one will _not_ be api stable or heuristics stable. The versions equal or below the current full version will be preserved.

.. module:: IIRrational.v2

---------------------
v2 fitting interface
---------------------

.. autofunction:: data2filter

---------------------
Results Objects
---------------------

.. autofunction:: IIRrational.v2.ResultsAidAdv


