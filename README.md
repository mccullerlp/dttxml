# dttxml 

Utilities for extracting data from LIGO Diagnostics Test Tools xml format.

If h5py is installed, there is also a command line tool dtt2hdf.

dtt2hdf -h

Otherwise, import dttxml. 

There is a high-level usage 

acc = dttxml.DiagAccess('fname.xml')

which provides a reader object and you can explore the methods to discover the data it returns.

there is also a low-level interface that returns exactly the data contained in the files

dttxml.dtt_read('fname.xml') 

This returns a nested dictionary full of the measurements. The format of the
dictionary depends on the measurement type in the dtt file. The dictionaries are
wrapped in the "Bunch" type that allows attribute access to the elements, much
like a Matlab struct.

