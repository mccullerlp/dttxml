"""
Utility to convert diaggui XML output into easily readable and introspectable HDF5 [.h5] file formats. HDF5 may be read from python using the h5py module or in matlab using the commands h5read, h5disp and similar (refer to http://www.mathworks.com/help/matlab/high-level-functions.html).

If you have hdf5 command line tools (h5ls) then you can list the datasets with

h5ls -r filename.h5
"""
from . import dtt2hdf

if __name__ == '__main__':
    dtt2hdf.main()
