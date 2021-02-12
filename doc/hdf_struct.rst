.. _hdf_struct:

GWINC HDF Struct
====================================================

This is a module interface for the :class:`gwonc.utilities.hdf_struct.HDFStruct` class.
This class wraps :mod:`h5py` and provides a transparent struct-like interface into the file.
It wraps input and output array assignments into numpy arrays, so that the user can treat the
HDF structure like a native python structure.


.. autoclass:: gwonc.utilities.hdf_struct.HDFStruct

