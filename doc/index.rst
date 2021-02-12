.. _opt_index:

GWINC Optimizer Tools
====================================================

The GWINC optimizer is a subtool of gwonc which 

Capabilities
-------------
 * Optimizing with upper and lower bounds

   - currently using the Nelder-Mead Simplex method from scipy.minimize
   - Remaps variables with functions enforcing the constraints
   - Optimizers currently must be "derivative free"
   - Considering adding the pyswarm optimizer

 * Monte-Carlo study system to randomly vary interferometer parameters

   - combines with optimizer to vary-then-optimize 
   - can additionally sweep a 1d or 2d parameter space

 * storing (`memoizing <https://en.wikipedia.org/wiki/Memoization>`_) noise curves
   that a given study does not change, for speed.

   - suggests which curves to store
   - occasionally checks that stored constraints indeed haven't changed

Usage
-------------

Like GWINC Core, the optimizer is exposed as both a program and function
interface for notebooks. The program interface may be called from its module
location as::

   $ python -m gwonc.tools.optimizer -h

.. cat this into a file and use .. literalinclude

.. code-block:: text

  gwonc-opt [-h] [-fl FLO] [-fh FHI] [-fn NPOINTS] [-nT N_TOTAL]
                  [-n1 N_ITER_SWEEP] [-n2 N_ITER_SWEEP2] [-nMC N_ITER_MC]
                  [-t TITLE] [-M FOM] [-D] [-O OUTPUT] [--save SAVE | -np | -p]
                  [-I IFO]
                  OPT

  Plot GWINC noise budget for specified IFO.

  Available included IFOs: 'CEcryo', 'Voyager', 'A+', 'aLIGO'

  positional arguments:
    OPT                   Optimizer overlay description file path (.yaml). It
                          may specify a default IFO

  optional arguments:
    -h, --help            show this help message and exit
    -fl FLO, --flo FLO    lower frequency bound in Hz [10]
    -fh FHI, --fhi FHI    upper frequency bound in Hz [2000]
    -fn NPOINTS, --npoints NPOINTS
                          number of frequency points [500]
    -nT N_TOTAL, --N_total N_TOTAL
                          Total number of iterations for MC and sweeps
    -n1 N_ITER_SWEEP, --N_iter_sweep N_ITER_SWEEP
                          Number of iterations of the sweep
    -n2 N_ITER_SWEEP2, --N_iter_sweep2 N_ITER_SWEEP2
                          Number of iterations of the 2D sweep
    -nMC N_ITER_MC, --N_iter_MC N_ITER_MC
                          Number of iterations for random sampling
    -t TITLE, --title TITLE
                          plot title
    -M FOM, --fom FOM     calculate inspiral range for resultant spectrum
                          ('func:param=val,param=val')
    -D, --displacement    supress adding displacement sensitivity axis
    -O OUTPUT, --output OUTPUT
                          HDF5 Format output file for the optimization sequence
                          if optimizing over many MCMC samples (use .h5
                          extension) This argument is mandatory if iterating
                          over points (otherwise data is not stored anywhere)
    --save SAVE, -s SAVE  save figure to file
    -np, --no-plot        supress plotting
    -p, --plot            ensure plotting (may make a lot of plots)
    -I IFO, --IFO IFO     IFO name or description file path (.yaml, .mat, .m) to
                          override default given in OPT

And a number of the command line arguments are specified in the config file, but the command line will override them (to allow users to parameterize things)

Example Study
---------------

The full example can  be found in the :ref:`opt_tutorial`. It will show how to use the optimizer to study how the
range is a function of the CTN reduction given also that a filter cavity will be installed and its optimization
should be a function of the CTN curve. It will demonstrate a series of sweep studies, where the coating loss angles
are swept between aLIGO loss angles and the A+ goal of 1/4 the CTN noise. 

.. figure:: coating_studies/FC_comparison.jpg
   :alt: Inspiral range as a function of CTN reduction

   Here the CTN is swept through 100 points. At each point the squeezing level and angle are optimized. The only filter cavity detuning is optimized
   on some, but others also optimize the FC transmission. This plot quickly shows that the transmission/cavity-pole of the FC does not need to be tuned.

This plot uses the A+ design in the pygwonc repository. It is not an official representation of the A+ curves as those parameters are not vetted. The
filter cavity has a round-trip loss of 60ppm for this study, showing that 100m is not sufficient for optimal improvement via the filter cavity. It also
shows that altering the cavity detuning does not help dig "more perfectly" into the coating thermal noise. This test does not include optimization of
homodyne angle, where some of these conclusions may not hold.

Requirements
-------------

Contents
------------

.. toctree::
   :maxdepth: 2

   tutorial
   config_format
   hdf_format
   developer_notes


