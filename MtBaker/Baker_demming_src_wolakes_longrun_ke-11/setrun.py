"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""

import os
from pyclaw import data
import numpy as np


#------------------------------
def setrun(claw_pkg='digclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    #assert claw_pkg.lower() == 'digclaw',  "Expected claw_pkg = 'digclaw'"
    ndim = 2
    rundata = data.ClawRunData(claw_pkg, ndim)

    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------

    rundata = setgeo(rundata)   # Defined below

    #------------------------------------------------------------------
    # DigClaw specific parameters:
    #------------------------------------------------------------------

    rundata = setdig(rundata)   # Defined below

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------

    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.ndim = ndim

    # Lower and upper edge of computational domain:
    # DEM limits
    import os
    import dclaw.topotools as gt
    topo=os.environ['TOPO']
    
    xll = 5.1e5 
    yll = 5.36e6 
    xu = 6.1e5
    yu = 5.427e6

    cell = 8. #header['cellsize']
    coarsen = 1
    cell = cell*coarsen
    
    rc = 1 #factor of coarsening from DEM resolution

    r1 = 16 #=> determines number of coarse cells only
    r2 = 8 #=>level 2 = cell*r3*r2 meters
    r3 = 1 #=>level 3 = cell*r3 meters, level 4 = cell meters
    totalrefinement = cell*r1*r2*r3*rc
    
    clawdata.xlower =  xll + 1.0*totalrefinement
    clawdata.xupper =  xu  - 1.0*totalrefinement

    clawdata.ylower =  yll + 1.0*totalrefinement
    clawdata.yupper =  yu  - 1.0*totalrefinement

    # Number of grid cells:
    clawdata.mx = int((clawdata.xupper-clawdata.xlower)/(totalrefinement))
    clawdata.my = int((clawdata.yupper-clawdata.ylower)/(totalrefinement))

    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.meqn = 7

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.maux = 10

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.mcapa = 0



    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0


    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.outstyle = 1

    hrs = 6.

    if clawdata.outstyle==1:
        # Output nout frames at equally spaced times up to tfinal:
        tf = 3600.*hrs
        clawdata.nout = int(tf/60.)
        clawdata.tfinal = tf

    elif clawdata.outstyle == 2:
        # Specify a list of output times.
        clawdata.tout =  [0.0,10.0,70.0,600.0,1200.0]

        clawdata.nout = len(clawdata.tout)

    elif clawdata.outstyle == 3:
        # Output every iout timesteps with a total of ntot time steps:
        iout = 1
        ntot = 100
        clawdata.iout = [iout, ntot]



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 4



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = 1

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 1.e-16

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1.0

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.25
    clawdata.cfl_max = 0.5

    # Maximum number of time steps to allow between output times:
    clawdata.max_steps = 100000




    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 1

    # Transverse order for 2d or 3d (not used in 1d):
    clawdata.order_trans = 0

    # Number of waves in the Riemann solution:
    clawdata.mwaves = 5

    # List of limiters to use for each wave family:
    # Required:  len(mthlim) == mwaves
    clawdata.mthlim = [4,4,4,4,4,4]

    # Source terms splitting:
    #   src_split == 0  => no source term (src routine never called)
    #   src_split == 1  => Godunov (1st order) splitting used,
    #   src_split == 2  => Strang (2nd order) splitting used,  not recommended.
    clawdata.src_split = 1


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.mbc = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.mthbc_xlower = 1
    clawdata.mthbc_xupper = 1

    clawdata.mthbc_ylower = 1
    clawdata.mthbc_yupper = 1


    # ---------------
    # AMR parameters:
    # ---------------


    # max number of refinement levels:
    mxnest = 3

    clawdata.mxnest = -mxnest   # negative ==> anisotropic refinement in x,y,t

    # List of refinement ratios at each level (length at least mxnest-1)
    clawdata.inratx = [r1,r2,r3]
    clawdata.inraty = [r1,r2,r3]
    clawdata.inratt = [r1,r2,r3]


    # Specify type of each aux variable in clawdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    clawdata.auxtype = ['center','center','yleft','center','center','xleft','yleft','xleft','yleft','center']


    clawdata.tol = -1.0     # negative ==> don't use Richardson estimator
    clawdata.tolsp = 0.5    # used in default flag2refine subroutine
                            # (Not used in geoclaw!)

    clawdata.kcheck = 2     # how often to regrid (every kcheck steps)
    clawdata.ibuff  = 4     # width of buffer zone around flagged points
    clawdata.cutoff = 0.7   # efficiency cutoff for grid generator
    clawdata.checkpt_iousr = 200
    clawdata.restart = False
    clawdata.restart_file = 'fort.chk0693'
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    return rundata
    # end of function setrun
    # ----------------------

def setgeo(rundata):
    """
    Set GeoClaw specific runtime parameters.
    For documentation see ....
    """

    try:
        geodata = rundata.geodata
    except:
        print "*** Error, this rundata has no geodata attribute"
        raise AttributeError("Missing geodata attribute")

    geodata.variable_dt_refinement_ratios = True

    # == setgeo.data values ==
    R1=6357.e3 #polar radius
    R2=6378.e3 #equatorial radius
    Rearth=.5*(R1+R2)
    geodata.igravity = 1
    geodata.gravity = 9.81
    geodata.icoordsys = 1
    geodata.icoriolis = 0
    geodata.Rearth = Rearth

    # == settsunami.data values ==
    geodata.sealevel = -1000.00
    geodata.drytolerance = 1.e-3
    geodata.wavetolerance = 5.e-2
    geodata.depthdeep = 1.e2
    geodata.maxleveldeep = 1
    geodata.ifriction = 1
    geodata.coeffmanning = 0.060
    geodata.frictiondepth = 2000.0

    # == settopo.data values ==
    # set a path variable for the base topo directory for portability
    import os
    topo=os.environ['TOPO']
    geodata.topofiles = []
    
    # Topography DEMs

    topotype = 3
    minlevel = 1
    maxlevel = 3
    topopath = os.path.join(topo,'Baker','dems_from_charlie','mtbaker_dtm_10m_adj_dams')
    infile = os.path.join(topopath,'mtbaker_dtm_10m_adj_dams.tt3')
    geodata.topofiles.append([topotype,minlevel,maxlevel, -1.0, 1.e10, infile])

    topopath = os.path.join(topo,'Baker','dems_from_charlie','grdn49w123_13_UTM_H_8ish_m_DEM')
    infile = os.path.join(topopath,'demn49w123_13as_subset.tt3')
    geodata.topofiles.append([topotype,minlevel,maxlevel, -1.0, 1.e10, infile])

    #topopath = os.path.join(topo,'Baker','dems_from_charlie','mtbaker_dtm2_5m.asc')
    #infile = os.path.join(topopath,'mtbaker_dtm2_5m.tt3')
    #geodata.topofiles.append([3, 1, 4, -1.0, 1.e10, infile])

    # Topography and basal slip surface
    topotype = 3
    minlevel = 1
    maxlevel = 4
    topopath = os.path.join(topo,'Baker','dems_from_charlie','deming_n70_ascii')
    infile = os.path.join(topopath,'deming_n70_topo_with_slip_surface.tt3')
    geodata.topofiles.append([topotype,minlevel,maxlevel, -1.0, 1.e10, infile])


    # == setdtopo.data values ==
    # == setdtopo.data values ==
    geodata.dtopofiles = []
    # for moving topography, append lines of the form:
    #   [topotype, minlevel,maxlevel,fname]

    #geodata.dtopofiles.append([1,3,3,'subfault.tt1'])

    # == setqinit.data values ==
    geodata.qinitfiles = []
    # for qinit perturbations append lines of the form
    #   [qinitftype,iqinit, minlev, maxlev, fname]

    #qinitftype: file-type, same as topo files, ie: 1, 2 or 3
    #The following values are allowed for iqinit:
        #n=1,mq perturbation of q(i,j,n)
        #n=mq+1: surface elevation eta is defined by the file and results in h=max(eta-b,0)
    #initfile = os.path.join(topopath,'nofkstill_prefailure_eta_large-3.tt2')

    # Deming landslide source
    topotype = 3
    minlevel = 3
    maxlevel = 3
    eta0n = 8
    topopath = os.path.join(topo,'Baker','dems_from_charlie','deming_n70_ascii')
    initfile = os.path.join(topopath,'deming_n70_src_topo.tt3')
    geodata.qinitfiles.append([topotype,eta0n,minlevel,maxlevel,initfile])

    topotype = 2
    m0n = 4
    initfile = os.path.join(topopath,'m0_src.tt2')
    geodata.qinitfiles.append([topotype,m0n,minlevel,maxlevel,initfile])

    
    # baker lake (not present in this simulation)
    topotype = 3
    minlevel = 3
    maxlevel = 3
    eta0n = 8
    topopath = os.path.join(topo,'Baker','dems_from_charlie','BakerLake220p8_10mBuffer')
    initfile = os.path.join(topopath,'bakerlake220p8_10mbuffer.tt3')
    #geodata.qinitfiles.append([topotype,eta0n,minlevel,maxlevel,initfile])
    topotype = 2
    m0n = 4
    initfile = os.path.join(topopath,'m0_bakerlake_10mbuffer.tt2')
    #geodata.qinitfiles.append([topotype,m0n,minlevel,maxlevel,initfile])
    
    # lake shannon (not present in this simulation)
    topotype = 3
    minlevel = 3
    maxlevel = 3
    eta0n = 8
    topopath = os.path.join(topo,'Baker','dems_from_charlie','LakeShannon126p55_10mBuffer_edit.asc')
    initfile = os.path.join(topopath,'lakeshannon126p55_10mbuffer_edit.tt3')
    #geodata.qinitfiles.append([topotype,eta0n,minlevel,maxlevel,initfile])
    topotype = 2
    m0n = 4
    initfile = os.path.join(topopath,'m0_lakeshannon126p55_10mbuffer_edit.tt2')
    #geodata.qinitfiles.append([topotype,m0n,minlevel,maxlevel,initfile])
    

    geodata.auxinitfiles = []
    # for auxinit perturbations append lines of the form
    #   [auxinitftype,iauxinit, minlev, maxlev, fname]

    #auxinitftype: file-type, same as topo files, ie: 1, 2 or 3
    #The following values are allowed for iauxinit:
        #n=1,maux perturbation of aux(i,j,n)

    # == setregions.data values ==
    geodata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    x1=5.52e5
    x2 = 5.535e5
    y1=5.183e6
    y2 = 5.186e6
    #geodata.regions.append([4,4,-10.0,1.e10,x1,x2,y1,y2])
    #geodata.regions.append([1,3,-10.0,200.0,ss[0],ss[1],ss[2],ss[3]])
    #geodata.regions.append([1,4,2000,1e10,6.145e5,6.194e5,4.9e6-1.e3,4.907e6])

    
    
    #geodata.regions.append([4,4,20.0,10.e3,xlow,xhi+1000.,ylow-5000.,yhi+200.])
    #geodata.regions.append([4,4,-10.0,10.e3,0.9580e6,0.9583e6,1.8342e6,1.8352e6])

    # == setgauges.data values ==
    geodata.gauges = []
    # for gauges append lines of the form  [gaugeno, x, y, t0, tf]
    #geodata.gauges.append([5000, 614324.222138,4898742.796443, 00.e3,60e3])

    # == setfixedgrids.data values ==
    geodata.fixedgrids = []
    # for fixed grids append lines of the form
    # [t1,t2,noutput,x1,x2,y1,y2,xpoints,ypoints,\
    #  ioutarrivaltimes,ioutsurfacemax]
    #geodata.fixedgrids.append([54.e3,55.e3,100,-101.,-96.,14.,19.,1000,1000,0,0])

    # == setflowgrades.data values ==
    geodata.flowgrades = []
    # for using flowgrades for refinement append lines of the form
    # [flowgradevalue, flowgradevariable, flowgradetype, flowgrademinlevel]
    # where:
    #flowgradevalue: floating point relevant flowgrade value for following measure:
    #flowgradevariable: 1=depth, 2= momentum, 3 = sign(depth)*(depth+topo) (0 at sealevel or dry land).
    #flowgradetype: 1 = norm(flowgradevariable), 2 = norm(grad(flowgradevariable))
    #flowgrademinlevel: refine to at least this level if flowgradevalue is exceeded.
    geodata.flowgrades.append([1.e-8, 2, 1, 4])
    geodata.flowgrades.append([0.001, 1, 1, 4])

    return rundata

def setdig(rundata):
    """
    Set DigClaw specific runtime parameters.
    For documentation see ....
    """

    try:
        digdata = rundata.digdata
    except:
        print "*** Error, this rundata has no digdata attribute"
        raise AttributeError("Missing digdata attribute")

    #set non-default values if needed
    digdata.c1 = 1.0
    digdata.rho_f = 1100.0
    digdata.rho_s = 2700.0
    digdata.phi_bed = 38.0
    digdata.phi_int = 38.0
    digdata.theta_input = 0.0
    digdata.mu = 0.005
    digdata.m0 = 0.62
    digdata.m_crit = 0.64
    permeability = 1.0e-11
    digdata.kappita = permeability #*np.exp((digdata.m0-0.60)/(0.04))
    digdata.alpha_c = 0.05
    digdata.alpha_seg = 0.
    digdata.phi_seg_coeff = 0.0
    digdata.delta = 0.01
    digdata.bed_normal = 0
    digdata.entrainment = 0
    digdata.entrainment_rate = 0.0
    digdata.sigma_0 = 1.e3
    digdata.phys_tol = rundata.geodata.drytolerance

    digdata.init_ptype = 0
    digdata.init_pmax_ratio = 0.00e0
    digdata.init_ptf = 0.0
    digdata.init_ptf2= 0.0

    #-1 =0, 0 = hydro, 1,2 = failure or average failure, 3,4= p(t) to failure or average failure
    #to reduce to shallow water equations, uncomment the following
    #digdata.c1= 0.0
    #digdata.phi_int = 0.0
    #digdata.phi_bed = 0.0
    #digdata.kappita = 0.0
    #digdata.mu = 0.0



    return rundata


if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys

    if len(sys.argv) == 2:
        rundata = setrun(sys.argv[1])
    else:
        rundata = setrun()

    rundata.write()

