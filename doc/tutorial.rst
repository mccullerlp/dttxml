.. _opt_tutorial:

Optimizer Tutorial
====================================================

This tutorial will show the basic usage of the optimizer for swept parameter
studies in 1D (and later 2D sweeps). Its goal will be to study how the reduction
of the coating thermal noise will affect the range given that the filter cavity
may also be optimized to match the quantum and thermal noise curves.

.. figure:: coating_studies/FC_comparison.jpg
   :alt: Inspiral range as a function of CTN reduction

   Here the CTN is swept through 100 points. At each point the squeezing level and angle are optimized. The only filter cavity detuning is optimized
   on some, but others also optimize the FC transmission. This plot quickly shows that the transmission/cavity-pole of the FC does not need to be tuned.


Starting Configuration
-------------------------------------------
The basic element of this tutorial is the

Create a file named ``A+coat.yaml``, with the following settings

.. code-block:: yaml

    ifo_default: 'A+'
    fom: 'sensemon_range'

    Optimizer:
      method: 'NelderMead'
      max_fev: 1000
      max_jev: 1000
      tol: 1e-1
      fatol: 1e-1
      recheck_rate: 0.02
      auto_exclude_N: 10


      N_total: 100
      #N_iter_sweep: 10
      #N_iter_sweep2: 10
      #N_iter_MC: 10


      include_curves:
        - 'Quantum Vacuum'
        - 'Coating Brownian'

      exclude_curves:
        - 'precompIFO'
        - 'Suspension Thermal'

      foms:
        ranges: True

    Ifo:
      Materials:
        Coating:
          Phihighn:               # tantala mechanical loss
            opt-param: 'sweep'
            start: 9.0e-5
            end: 36e-5
          Philown:               # silica mechanical loss
            opt-param: 'sweep'
            start: 1.25e-5
            end: 5e-5

      Squeezer:
        AmplitudedB:
          opt-param: 'optimize'
          lower_bound: 0
          upper_bound: 20
        SQZAngle:
          opt-param: 'optimize'

        # Parameters for frequency dependent squeezing
        FilterCavity:
          Te:                       # end mirror trasmission
            opt-param: 'optimize'
            lower_bound: 0
          fdetune:
            opt-param: 'optimize'

      Optics:
        SRM:
          Transmittance: 
            opt-param: 'optimize'
            lower_bound: 0


This configuration will run the ``A+`` design curve (which is packaged with
pygwonc) and it will optimize over it as it sweeps the coating thermal noise
curve. Some of the parameters to explain are

.. describe:: ifo_default

   which IFO to use. Can be overrridden at the command line.

.. describe:: fom

   the string for the figure-of-merit to optimize over. sensemon_range is easy to compute and
   monotonic with the other range measures, so it is a good default. More astrophysically relevant
   FOMs are given in the next argument.

.. describe:: foms:

   Stores some settings for common relevant figures of merit to be computed after optimization

   .. describe:: ranges

      When true, the ranges from :func:`inspiral_range.cosmological_ranges` are reported in the HDF
      foms group (this requires lalsimulation).
             
   .. describe:: minfrac_nominal

      The smallest fraction of the nominal noise curve (not useful in any particular way). The nominal 
      curve is computed from the base ifo config before any parameters are changed/optimized.
             
   .. describe:: minfrac_above_Hz

      The smallest fraction of the nominal noise curve above the configured
      frequency. To see how high-frequency may be improving

.. describe:: Optimizer:

  .. describe:: method

     currently only supports 'Nelder-Mead' simplex method, but in principle this is configurable

  .. describe:: max_fev, max_jev

     Maximum number of function or jacobian evaluations. Currently no optimizer support jacobian evals.

  .. describe:: tol, fatol

     termination tolerances for the optimizer. See `<https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html>`_

  .. describe:: recheck_rate

     how often to check that excluded noise curves have indeed not changed.

  .. describe:: auto_exclude_N

     How many iterations to perform before automatically excluding curves. If negative, curves will never
     be automatically excluded.

  .. describe:: N_total, N_iter_sweep, N_iter_sweep2, N_iter_MC

      Determines the number of iterations depending on how many sweeps and how
      many random parameters are configured. N_total is optional, but it
      one of the need parameters is missing, it will divide to keep the
      total as close but under N_total. 

      These may be overridden from the command-line.

  .. describe:: include_curves

     curves to always recompute. It is safe to put many curves in here, but the optimization may be slower.

  .. describe:: exclude_curves

     curves to always store. The user must know that the parameters do not change these curves.
     precompIFO may also be in here. This is not a noise curve, but is very slow to compute.
     Eventually GWINC and the optimizer will be smarter and and will not need to specify this
     advanced, low-level computation element.

.. describe:: Ifo:

   This section provides overriding configurations for the IFO structure. The layout models the GWINC Core config, but where the core
   config expects numbers, this configuration instead provides a dictionary tagged with the `opt-param` key. This key determines how the
   optimizer will handle the parameter, valid options are:

  .. describe:: opt-param: "optimize"

     the parameter will be bound with the optional ``lower_bound`` and
     ``upper_bound`` parameters. Note that without bounds, some parameters such as
     transmitances may misbehave!

  .. describe:: opt-param: "sweep"

     The system now will execute a sweep through its iterations, where the
     parameter will move from ``start`` to ``end``. By default it
     will be a linear sweep, but the subparameter ``mapping`` may be specified
     as 'log' to cause logarithmic spacing. Having such a parameter will activate
     sweep mode and use the ``N_iter_sweep`` parameter.

     If multiple parameters are specified as sweep, then they will move simultaneously.

  .. describe:: opt-param: "sweep2"

     just like sweep, but moves the iterations will create a 2D grid during the sweep.
     Having such a parameter will activate sweep mode and use the ``N_iter_sweep2``
     parameter.

  .. describe:: opt-param: "MC-uniform"

     During iterations, this parameter will be uniformly distributed between
     ``start`` and ``end``. Having such a parameter will activate
     the MC mode and use the N_iter_MC configuration.

  .. describe:: opt-param: "MC-normal"

     During iterations, this parameter will be normal/Guassian distributed around
     ``center`` with ``stddev``. Having such a parameter will activate
     the MC mode and use the N_iter_MC configuration.

Running the optimizer
-------------------------------------------

This config files specifies a swept optimization problem with no Monte-Carlo. The sweep affects both
of the CTN loss angle parameters coherently, so the CTN curve changes linearly. Some of the curves are
included/excluded explicitely, but the rest are done automatically and some warning is given in the stdout
of the program. This config is run using::

  $ python -m gwonc.tools.optimizer A+coat.yaml --output A+coat.h5

Which will start and generate some output like:

.. code-block:: text

  A+                                     
  /home/mcculler/local/home_sync/projects/fcdesign/pygwonc/gwonc/noise/newtonian.
    coeff = 1/(1 + 3**(gamma*(f-fk)))
  RUNNING IDX:  0
  AUTOEXCLUDE: curve 'Newtonian Gravity' hasn't changed, adding it to curves_excl
  AUTOEXCLUDE: curve 'Excess Gas' hasn't changed, adding it to curves_exclude (us
  AUTOEXCLUDE: curve 'Coating Thermo-Optic' hasn't changed, adding it to curves_e
  AUTOEXCLUDE: curve 'Substrate Brownian' hasn't changed, adding it to curves_exc
  AUTOEXCLUDE: curve 'Seismic' hasn't changed, adding it to curves_exclude (user 
  AUTOEXCLUDE: curve 'Substrate Thermo-Elastic' hasn't changed, adding it to curv
  0 322.626269558
  10 323.12701406
  20 324.524329627
  30 325.03596466
  40 325.947973208
  50 326.36064234
  60 327.885642761
  70 329.527457167
  80 329.549609412
  90 330.226119587
  100 330.355602101
  110 330.514548189
  120 330.552972046
  130 330.611052907
  Optimization terminated successfully.
          Current function value: -330.614974
          Iterations: 87
          Function evaluations: 138
  Iteration 0, FOM: 330.614973871
  RUNNING IDX:  1
  0 328.523525075
  10 325.349260227
  20 328.555639502
  Optimization terminated successfully.
          Current function value: -328.555640
          Iterations: 9
          Function evaluations: 22
  Iteration 1, FOM: 328.555639502
  RUNNING IDX:  2
  0 326.509168853
  10 323.004836419
  20 326.52177815
  ^C


.. note::
   In this example, the program was control-C killed during operation

Ok, so a file exists, but the sweep/optimization clearly didn't finish. The optimizer is designed for this and it only
opens the hdf for atomic updates between the (slowish) optimizations. It halts KeyboardInterrupts during this time to perform
the fast file write without interruption.

When it is started again later with the same command, it will resume fitting. This allows the user to start developing plots on partial datasets!

Exploring HDF output
--------------------------

Given the partial dataset generated so far, we can explore the file format using the :command:`h5ls` and :command:`h5dump` commands. These commands are typically installed
within a system hd5 package. They may be missing if your system only has hdf libraries installed.

The format documentation is detailed in full at :ref:`opt_hdf_format`.

Now inspecting the file ::

  $ h5ls -r A+coat.h5

.. code-block:: text

    /                        Group
    /extras                  Group
    /finished                Dataset {SCALAR}
    /fomopt                  Dataset {SCALAR}
    /fomoptvec               Dataset {100}
    /foms                    Group
    /foms/horizon            Dataset {100}
    /foms/minfrac_above_Hz   Dataset {100}
    /foms/minfrac_nominal    Dataset {100}
    /foms/range              Dataset {100}
    /foms/reach_50           Dataset {100}
    /foms/reach_90           Dataset {100}
    /foms/response_10        Dataset {100}
    /foms/response_50        Dataset {100}
    /ifo                     Group
    /ifo/Infrastructure.Length Dataset {SCALAR}
    /ifo/Infrastructure.ResidualGas.mass Dataset {SCALAR}
    /ifo/Infrastructure.ResidualGas.polarizability Dataset {SCALAR}
    /ifo/Infrastructure.ResidualGas.pressure Dataset {SCALAR}
    /ifo/Infrastructure.Temp Dataset {SCALAR}
    /ifo/Laser.Power         Dataset {SCALAR}
    /ifo/Laser.Wavelength    Dataset {SCALAR}
    /ifo/Materials.Coating.Alphahighn Dataset {SCALAR}
    /ifo/Materials.Coating.Alphalown Dataset {SCALAR}
    /ifo/Materials.Coating.Betahighn Dataset {SCALAR}
    /ifo/Materials.Coating.Betalown Dataset {SCALAR}
    /ifo/Materials.Coating.CVhighn Dataset {SCALAR}
    /ifo/Materials.Coating.CVlown Dataset {SCALAR}
    /ifo/Materials.Coating.Indexhighn Dataset {SCALAR}
    /ifo/Materials.Coating.Indexlown Dataset {SCALAR}
    /ifo/Materials.Coating.Phihighn Dataset {SCALAR}
    /ifo/Materials.Coating.Philown Dataset {SCALAR}
    /ifo/Materials.Coating.Sigmahighn Dataset {SCALAR}
    /ifo/Materials.Coating.Sigmalown Dataset {SCALAR}
    /ifo/Materials.Coating.ThermalDiffusivityhighn Dataset {SCALAR}
    /ifo/Materials.Coating.ThermalDiffusivitylown Dataset {SCALAR}
    /ifo/Materials.Coating.Yhighn Dataset {SCALAR}
    /ifo/Materials.Coating.Ylown Dataset {SCALAR}
    /ifo/Materials.MassRadius Dataset {SCALAR}
    /ifo/Materials.MassThickness Dataset {SCALAR}
    /ifo/Materials.Substrate.Alphas Dataset {SCALAR}
    /ifo/Materials.Substrate.MassAlpha Dataset {SCALAR}
    /ifo/Materials.Substrate.MassCM Dataset {SCALAR}
    /ifo/Materials.Substrate.MassDensity Dataset {SCALAR}
    /ifo/Materials.Substrate.MassKappa Dataset {SCALAR}
    /ifo/Materials.Substrate.MechanicalLossExponent Dataset {SCALAR}
    /ifo/Materials.Substrate.MirrorSigma Dataset {SCALAR}
    /ifo/Materials.Substrate.MirrorY Dataset {SCALAR}
    /ifo/Materials.Substrate.RefractiveIndex Dataset {SCALAR}
    /ifo/Materials.Substrate.Temp Dataset {SCALAR}
    /ifo/Materials.Substrate.c2 Dataset {SCALAR}
    /ifo/Optics.BSLoss       Dataset {SCALAR}
    /ifo/Optics.Curvature.ETM Dataset {SCALAR}
    /ifo/Optics.Curvature.ITM Dataset {SCALAR}
    /ifo/Optics.ETM.CoatingThicknessCap Dataset {SCALAR}
    /ifo/Optics.ETM.CoatingThicknessLown Dataset {SCALAR}
    /ifo/Optics.ETM.Transmittance Dataset {SCALAR}
    /ifo/Optics.ITM.CoatingAbsorption Dataset {SCALAR}
    /ifo/Optics.ITM.CoatingThicknessCap Dataset {SCALAR}
    /ifo/Optics.ITM.CoatingThicknessLown Dataset {SCALAR}
    /ifo/Optics.ITM.Transmittance Dataset {SCALAR}
    /ifo/Optics.Loss         Dataset {SCALAR}
    /ifo/Optics.PRM.Transmittance Dataset {SCALAR}
    /ifo/Optics.PhotoDetectorEfficiency Dataset {SCALAR}
    /ifo/Optics.Quadrature.dc Dataset {SCALAR}
    /ifo/Optics.SRM.CavityLength Dataset {SCALAR}
    /ifo/Optics.SRM.Transmittance Dataset {SCALAR}
    /ifo/Optics.SRM.Tunephase Dataset {SCALAR}
    /ifo/Optics.SubstrateAbsorption Dataset {SCALAR}
    /ifo/Optics.coupling     Dataset {SCALAR}
    /ifo/Optics.pcrit        Dataset {SCALAR}
    /ifo/Seismic.Beta        Dataset {SCALAR}
    /ifo/Seismic.Gamma       Dataset {SCALAR}
    /ifo/Seismic.KneeFrequency Dataset {SCALAR}
    /ifo/Seismic.LowFrequencyLevel Dataset {SCALAR}
    /ifo/Seismic.Omicron     Dataset {SCALAR}
    /ifo/Seismic.RayleighWaveSpeed Dataset {SCALAR}
    /ifo/Seismic.Rho         Dataset {SCALAR}
    /ifo/Seismic.Site        Dataset {SCALAR}
    /ifo/Seismic.TestMassHeight Dataset {SCALAR}
    /ifo/Squeezer.AmplitudedB Dataset {SCALAR}
    /ifo/Squeezer.FilterCavity.L Dataset {SCALAR}
    /ifo/Squeezer.FilterCavity.Lrt Dataset {SCALAR}
    /ifo/Squeezer.FilterCavity.Rot Dataset {SCALAR}
    /ifo/Squeezer.FilterCavity.Te Dataset {SCALAR}
    /ifo/Squeezer.FilterCavity.Ti Dataset {SCALAR}
    /ifo/Squeezer.FilterCavity.fdetune Dataset {SCALAR}
    /ifo/Squeezer.InjectionLoss Dataset {SCALAR}
    /ifo/Squeezer.SQZAngle   Dataset {SCALAR}
    /ifo/Squeezer.Type       Dataset {SCALAR}
    /ifo/Suspension.BreakStress Dataset {SCALAR}
    /ifo/Suspension.C70Steel.Alpha Dataset {SCALAR}
    /ifo/Suspension.C70Steel.C Dataset {SCALAR}
    /ifo/Suspension.C70Steel.K Dataset {SCALAR}
    /ifo/Suspension.C70Steel.Phi Dataset {SCALAR}
    /ifo/Suspension.C70Steel.Rho Dataset {SCALAR}
    /ifo/Suspension.C70Steel.Y Dataset {SCALAR}
    /ifo/Suspension.C70Steel.dlnEdT Dataset {SCALAR}
    /ifo/Suspension.Fiber.EndLength Dataset {SCALAR}
    /ifo/Suspension.Fiber.EndRadius Dataset {SCALAR}
    /ifo/Suspension.Fiber.Radius Dataset {SCALAR}
    /ifo/Suspension.FiberType Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.Alpha Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.C Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.K Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.Phi Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.Rho Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.Y Dataset {SCALAR}
    /ifo/Suspension.MaragingSteel.dlnEdT Dataset {SCALAR}
    /ifo/Suspension.Ribbon.Thickness Dataset {SCALAR}
    /ifo/Suspension.Ribbon.Width Dataset {SCALAR}
    /ifo/Suspension.Silica.Alpha Dataset {SCALAR}
    /ifo/Suspension.Silica.C Dataset {SCALAR}
    /ifo/Suspension.Silica.Dissdepth Dataset {SCALAR}
    /ifo/Suspension.Silica.K Dataset {SCALAR}
    /ifo/Suspension.Silica.Phi Dataset {SCALAR}
    /ifo/Suspension.Silica.Rho Dataset {SCALAR}
    /ifo/Suspension.Silica.Y Dataset {SCALAR}
    /ifo/Suspension.Silica.dlnEdT Dataset {SCALAR}
    /ifo/Suspension.Silicon.Alpha Dataset {SCALAR}
    /ifo/Suspension.Silicon.C Dataset {SCALAR}
    /ifo/Suspension.Silicon.Dissdepth Dataset {SCALAR}
    /ifo/Suspension.Silicon.K Dataset {SCALAR}
    /ifo/Suspension.Silicon.Phi Dataset {SCALAR}
    /ifo/Suspension.Silicon.Rho Dataset {SCALAR}
    /ifo/Suspension.Silicon.Y Dataset {SCALAR}
    /ifo/Suspension.Silicon.dlnEdT Dataset {SCALAR}
    /ifo/Suspension.Stage[0].Blade Dataset {SCALAR}
    /ifo/Suspension.Stage[0].Dilution Dataset {SCALAR}
    /ifo/Suspension.Stage[0].K Dataset {SCALAR}
    /ifo/Suspension.Stage[0].Length Dataset {SCALAR}
    /ifo/Suspension.Stage[0].Mass Dataset {SCALAR}
    /ifo/Suspension.Stage[0].NWires Dataset {SCALAR}
    /ifo/Suspension.Stage[0].WireRadius Dataset {SCALAR}
    /ifo/Suspension.Stage[1].Blade Dataset {SCALAR}
    /ifo/Suspension.Stage[1].Dilution Dataset {SCALAR}
    /ifo/Suspension.Stage[1].K Dataset {SCALAR}
    /ifo/Suspension.Stage[1].Length Dataset {SCALAR}
    /ifo/Suspension.Stage[1].Mass Dataset {SCALAR}
    /ifo/Suspension.Stage[1].NWires Dataset {SCALAR}
    /ifo/Suspension.Stage[1].WireRadius Dataset {SCALAR}
    /ifo/Suspension.Stage[2].Blade Dataset {SCALAR}
    /ifo/Suspension.Stage[2].Dilution Dataset {SCALAR}
    /ifo/Suspension.Stage[2].K Dataset {SCALAR}
    /ifo/Suspension.Stage[2].Length Dataset {SCALAR}
    /ifo/Suspension.Stage[2].Mass Dataset {SCALAR}
    /ifo/Suspension.Stage[2].NWires Dataset {SCALAR}
    /ifo/Suspension.Stage[2].WireRadius Dataset {SCALAR}
    /ifo/Suspension.Stage[3].Blade Dataset {SCALAR}
    /ifo/Suspension.Stage[3].Dilution Dataset {SCALAR}
    /ifo/Suspension.Stage[3].K Dataset {SCALAR}
    /ifo/Suspension.Stage[3].Length Dataset {SCALAR}
    /ifo/Suspension.Stage[3].Mass Dataset {SCALAR}
    /ifo/Suspension.Stage[3].NWires Dataset {SCALAR}
    /ifo/Suspension.Stage[3].WireRadius Dataset {SCALAR}
    /ifo/Suspension.Temp     Dataset {SCALAR}
    /ifo/Suspension.Type     Dataset {SCALAR}
    /ifo/TCS.SRCloss         Dataset {SCALAR}
    /ifo/TCS.s_cc            Dataset {SCALAR}
    /ifo/TCS.s_cs            Dataset {SCALAR}
    /ifo/TCS.s_ss            Dataset {SCALAR}
    /ifo/Test.Test           Dataset {SCALAR}
    /iterations              Group
    /iterations/0            Group
    /iterations/0/fomopt     Dataset {SCALAR}
    /iterations/0/foms       Group
    /iterations/0/foms/minfrac_above_Hz Dataset {SCALAR}
    /iterations/0/foms/minfrac_nominal Dataset {SCALAR}
    /iterations/0/params     Group
    /iterations/0/params/Optics.SRM.Transmittance Dataset {SCALAR}
    /iterations/0/params/Squeezer.AmplitudedB Dataset {SCALAR}
    /iterations/0/params/Squeezer.FilterCavity.Te Dataset {SCALAR}
    /iterations/0/params/Squeezer.FilterCavity.fdetune Dataset {SCALAR}
    /iterations/0/params/Squeezer.SQZAngle Dataset {SCALAR}
    /iterations/1            Group
    /iterations/1/fomopt     Dataset {SCALAR}
    /iterations/1/foms       Group
    /iterations/1/foms/minfrac_above_Hz Dataset {SCALAR}
    /iterations/1/foms/minfrac_nominal Dataset {SCALAR}
    /iterations/1/params     Group
    /iterations/1/params/Materials.Coating.Phihighn Dataset {SCALAR}
    /iterations/1/params/Materials.Coating.Philown Dataset {SCALAR}
    /iterations/1/params/Optics.SRM.Transmittance Dataset {SCALAR}
    /iterations/1/params/Squeezer.AmplitudedB Dataset {SCALAR}
    /iterations/1/params/Squeezer.FilterCavity.Te Dataset {SCALAR}
    /iterations/1/params/Squeezer.FilterCavity.fdetune Dataset {SCALAR}
    /iterations/1/params/Squeezer.SQZAngle Dataset {SCALAR}
    /iterations/2            Group
    /iterations/2/fomopt     Dataset {SCALAR}
    /iterations/2/foms       Group
    /iterations/2/foms/minfrac_above_Hz Dataset {SCALAR}
    /iterations/2/foms/minfrac_nominal Dataset {SCALAR}
    /iterations/2/params     Group
    /iterations/2/params/Materials.Coating.Phihighn Dataset {SCALAR}
    /iterations/2/params/Materials.Coating.Philown Dataset {SCALAR}
    /iterations/2/params/Optics.SRM.Transmittance Dataset {SCALAR}
    /iterations/2/params/Squeezer.AmplitudedB Dataset {SCALAR}
    /iterations/2/params/Squeezer.FilterCavity.Te Dataset {SCALAR}
    /iterations/2/params/Squeezer.FilterCavity.fdetune Dataset {SCALAR}
    /iterations/2/params/Squeezer.SQZAngle Dataset {SCALAR}
    /mc_params               Group
    /mc_params/Materials.Coating.Phihighn Dataset {100}
    /mc_params/Materials.Coating.Philown Dataset {100}
    /opt                     Group
    /opt/N_total             Dataset {SCALAR}
    /opt/auto_exclude_N      Dataset {SCALAR}
    /opt/exclude_curves[0]   Dataset {SCALAR}
    /opt/exclude_curves[1]   Dataset {SCALAR}
    /opt/fatol               Dataset {SCALAR}
    /opt/foms.minfrac_above_Hz Dataset {SCALAR}
    /opt/foms.minfrac_nominal Dataset {SCALAR}
    /opt/foms.ranges         Dataset {SCALAR}
    /opt/include_curves[0]   Dataset {SCALAR}
    /opt/include_curves[1]   Dataset {SCALAR}
    /opt/max_fev             Dataset {SCALAR}
    /opt/max_jev             Dataset {SCALAR}
    /opt/method              Dataset {SCALAR}
    /opt/recheck_rate        Dataset {SCALAR}
    /opt/tol                 Dataset {SCALAR}
    /opt_params              Group
    /opt_params/Optics.SRM.Transmittance Dataset {100}
    /opt_params/Squeezer.AmplitudedB Dataset {100}
    /opt_params/Squeezer.FilterCavity.Te Dataset {100}
    /opt_params/Squeezer.FilterCavity.fdetune Dataset {100}
    /opt_params/Squeezer.SQZAngle Dataset {100}


Ok, so this is a lot of stuff, but it can be broken down into its hierarchical sections.

.. describe:: /ifo/*

   This group contains all of the configurations for the baseline "nominal"
   interferometer. The MC, sweep and optimizations are logged as "diffs" from
   this dictionary. Note that this is not in the hierarchical format given by
   its YAML file, but rather a flattened format. This is convertible to the
   ifo-struct format using the details in :ref:`opt_dev_notes`. This format is
   to aid in programmatically iterating and diffing without needing
   depth-first-search algorithms everywhere.

.. describe:: /opt/*

   This group contains all of the configurations from the optimizer YAML
   configuration. It is also in a flattened format. If an HDF file is resumed,
   the configurations are checked for consistency. In principle, the HDF5 could
   be resumed without the original configuration given all of this data
   (functionality not yet implemented).


.. describe:: /fomopt

   String containing the range figure of merit that is optimized over. 

.. describe:: /fomoptvec

   A true dataset over the configured iterations for the optimized FOM value.
   *It is created full of NaNs*! During the optimization, it is updated at each
   iteration. *This is the vector that determines which iteration to continue
   at* Every iteration in this vector storing a NaN will be optimized on. It is
   possible to optimize out-of-order to sample iterations since the montecarlo
   values are generated at file creation rather than at the end.

Here it is useful to pause and inspect this variable after these three iterations::

  $ h5dump -d /fomoptvec A+coat.h5

.. code-block:: text

    HDF5 "A+coat.h5" {
    DATASET "/fomoptvec" {
      DATATYPE  H5T_IEEE_F64LE
      DATASPACE  SIMPLE { ( 100 ) / ( 100 ) }
      DATA {
      (0): 330.615, 328.556, 326.58, nan, nan, nan, nan, nan, nan, nan, nan,
      (11): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (24): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (37): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (50): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (63): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (76): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (89): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan
      }
    }
    }

.. describe:: /mc_params/*

   This vector contains the stored sweep and MC parameter variations applied
   during the iterations. These are computed at file creation time
   and then pulled from these vectors.

Just to make it real, lets dump it::

     $ h5dump -d /mc_params/Materials.Coating.Phihighn A+coat.h5

.. code-block:: text

     HDF5 "A+coat.h5" {
     DATASET "/mc_params/Materials.Coating.Phihighn" {
       DATATYPE  H5T_IEEE_F64LE
       DATASPACE  SIMPLE { ( 100 ) / ( 100 ) }
       DATA {
       (0): 9e-05, 9.27273e-05, 9.54545e-05, 9.81818e-05, 0.000100909,
       (5): 0.000103636, 0.000106364, 0.000109091, 0.000111818, 0.000114545,
       (10): 0.000117273, 0.00012, 0.000122727, 0.000125455, 0.000128182,
       (15): 0.000130909, 0.000133636, 0.000136364, 0.000139091, 0.000141818,
       (20): 0.000144545, 0.000147273, 0.00015, 0.000152727, 0.000155455,
       (25): 0.000158182, 0.000160909, 0.000163636, 0.000166364, 0.000169091,
       (30): 0.000171818, 0.000174545, 0.000177273, 0.00018, 0.000182727,
       (35): 0.000185455, 0.000188182, 0.000190909, 0.000193636, 0.000196364,
       (40): 0.000199091, 0.000201818, 0.000204545, 0.000207273, 0.00021,
       (45): 0.000212727, 0.000215455, 0.000218182, 0.000220909, 0.000223636,
       (50): 0.000226364, 0.000229091, 0.000231818, 0.000234545, 0.000237273,
       (55): 0.00024, 0.000242727, 0.000245455, 0.000248182, 0.000250909,
       (60): 0.000253636, 0.000256364, 0.000259091, 0.000261818, 0.000264545,
       (65): 0.000267273, 0.00027, 0.000272727, 0.000275455, 0.000278182,
       (70): 0.000280909, 0.000283636, 0.000286364, 0.000289091, 0.000291818,
       (75): 0.000294545, 0.000297273, 0.0003, 0.000302727, 0.000305455,
       (80): 0.000308182, 0.000310909, 0.000313636, 0.000316364, 0.000319091,
       (85): 0.000321818, 0.000324545, 0.000327273, 0.00033, 0.000332727,
       (90): 0.000335455, 0.000338182, 0.000340909, 0.000343636, 0.000346364,
       (95): 0.000349091, 0.000351818, 0.000354545, 0.000357273, 0.00036
       }
     }
     }


.. describe:: /opt_params/*

   This vector contains the stored optimized parameters. It is filled with NaNs
   and updated through the optimization process.
             
checking it out too::

  $ h5dump -d /opt_params/Squeezer.AmplitudedB A+coat.h5

.. code-block:: text

    HDF5 "A+coat.h5" {
    DATASET "/opt_params/Squeezer.AmplitudedB" {
      DATATYPE  H5T_IEEE_F64LE
      DATASPACE  SIMPLE { ( 100 ) / ( 100 ) }
      DATA {
      (0): 16.7105, 16.5589, 16.3288, nan, nan, nan, nan, nan, nan, nan, nan,
      (11): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (24): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (37): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (50): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (63): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (76): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan,
      (89): nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan
      }
    }
    }


.. describe:: /foms/*

   Stores the additional range calculations which were not necessarily optimized over. This are the better parameters to plot as they are in astrophysically
   significant units. These come from :func:`inspiral_range.cosmological_ranges`:

    * /foms/horizon
    * /foms/range         
    * /foms/reach_50      
    * /foms/reach_90      
    * /foms/response_10   
    * /foms/response_50   

   These will be computed or shown depending on the ``Opt.Optimizer.foms.*`` configurations.

.. describe:: /iterations/N/*

   These are bunches of data computed at each iteration. These are largely
   redundant with the opt_params, mc_params and other vectors of data. These are
   collected for debugging purposes, and to complement the functional interface
   to the library, which is too fluid to store its samples in the aforementioned
   vector collections.

   The ``params/`` subgroup stores the diffence from the nominal configuration,
   including all MC and optimized parameters.

.. describe:: /extra/*

   These are bunches of data for samples computed outside of the command-line
   iteration-based interface. They have the same internal format as the
   ``/iterations/N/*`` collections so the same code may use both.

   The ``params/`` subgroup stores the diffence from the nominal configuration,
   including all MC and optimized parameters, as well as any changed by the user

Finally, we can resume the calculations using the same command as above::

  $ python -m gwonc.tools.optimizer A+coat.yaml --output A+coat.h5

If you cancel this, then change some parameters in A+coat.yaml, you will find
that it will complain and fail to resume, with some diffing to show the changes. This is to prevent
accidental modification and erroneous studies. It is not currently possible to override this behavior.


Using Makefiles for large studies
---------------------------------

Since the optimizer has this command line interface, multiple runs can be started in parallel using makefiles. Some ``mv`` tricks are employed so that the
start/stop resuming still works as well. Generating the file ``Makefile`` in a directory with optimizer yaml files.

.. code-block:: make

  yaml_files := $(wildcard *.yaml)
  h5_files := $(yaml_files:.yaml=.h5)

  .PHONY: all
  all: $(h5_files)

  %.h5 : %.yaml
          python -m gwonc.tools.optimizer $< --output _$@
          mv _$@ $@


Now the user only needs to run::

  $ make all -j 3

and all of the studies will be done across 3 cores. The h5 files are prepended with underscores until they are complete. This prevents make from assuming they are done until they truly are.

Multiple Studies and Notebook
-----------------------------

The general method to make plots is load the hdf file into an HDFStruct, then access the data vectors.

.. code-block:: python

  #open the file, uses h5py internally
  hdf = HDFStruct('./A+coat.h5')

  #setup the plot
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.grid(b=True)

  #plot! Notice the attribute access into the HDF5 file. How nice..
  ax.plot(hdf.mc_params["Materials.Coating.Phihighn"]/3.6e-4, hdf.foms.range)
  #not also that the attribute access doesn't work for these flattened parameter keys

  #label the axes like a civilized person
  ax.set_xlabel('Fractional CTN reduction from aLIGO')
  ax.set_ylabel('Inspiral Range (comoving)')
  ax.set_title('Range as a function of CTN')


The notebook to create the plot at the beginning is :doc:`coatingFCplots <./coating_studies/coatingFCplots>` (:download:`download <./coating_studies/coatingFCplots.ipynb>`), . This uses hdf datasets generated from

 *  :download:`coating_studies/A+coat_all.yaml`
 *  :download:`coating_studies/A+coatFC100.yaml`
 *  :download:`coating_studies/A+coatFC.yaml`
 *  :download:`coating_studies/A+coatFChold.yaml`
 *  :download:`coating_studies/A+coatFC100ALL.yaml`

as well as the makefile above. The data is accessed using the :class:`gwonc.utilities.hdf_struct.HDFStruct` data type introduced in the optimizer code and documented at :ref:`hdf_struct`.

Use the h5ls and h5dump utilities described above to find the relevant fields of the optimizer output format.

.. toctree::
   :hidden:
   :maxdepth: 1

   ./coating_studies/coatingFCplots
