# Install DFT2KP
## Install python package for DFT2KP
Here I recommend use `conda create -n qsymm-env python=3.10` to generate a clean virtual environment for further use.  
We can use command `conda env list` to find out the existing virtual environments. And use command `conda activate yourenv` to activate the virtual environment you want.  
Then use `conda install` to install all the requirement which is achievable for conda, i.e.     'numpy<=1.26.4', 'scipy', 'sympy<=1.10', 'tabulate', 'matplotlib', 'qsymm'.  
And I notice when I install 'qsymm', conda automatically install a package called 'tinyarray' for me, which is necessary for the left package. But I has not figured out what it is right now.  
The we can use `pip install` for the left two requirement, 'irrep<=1.8.2', 'irreptables', and our goal 'dft2kp'.  
Till now, we have finished the first step.
## patch the qe program
Use `tar -zxvf qe-7.2-ReleasePack.tar.gz` to unzip the qe package. Notice the version of qe is limited to be 7.0, 7.1 and 7.2.  
Download the patch with correct version from the [dft2kp's gitlab](https://gitlab.com/dft2kp/dft2kp/-/tree/main/patch?ref_type=heads).  
But we should better clone this repository from [qe's github](https://github.com/QEF/q-e) with command `git clone https://github.com/QEF/q-e.git`. Then we can use all the git command. It's better to check all the version within by `git tag`, then checkout the correct version we want by `git checkout qe-7.2`. Then this repository stays in the version 'qe-7.2'.  
Then we can use the patch file by command `git apply path/to/qe2kp-7.2.patch`. Before we actually do that, we (a) use `git describe --tags` to ensure the version of repository is correct (b) should use `git apply --check path/to/qe2kp-7.2.patch` or `git apply --stat path/to/qe2kp-7.2.patch` to make sure our patch can be successfully applied. If this patch is suitable, the command `git apply --check path/to/qe2kp-7.2.patch` will provide the content it modified.  
Generally, the command `git apply path/to/qe2kp-7.2.patch` generates no information. But I found that if we actually use the  `git apply --check path/to/qe2kp-7.2.patch` again after applying the patch, it reports an error which should be another sign of successful application.
## Make the patched QE program
### My first try ###
Here we use **intel oneapi** to compile the QE program. First we need to find the directory of intel oneapi (cd /fs1/software/intel/oneapi) use `source setvars.sh` to acticate oneapi.   
Following the README.md procedure, conduct the following commands
```
$ mkdir ./build
$ cd ./build
$ cmake -DCMAKE_Fortran_COMPILER=mpif90 -DCMAKE_C_COMPILER=mpicc ..
$ make [-jN]
$ cmake -DCMAKE_INSTALL_PREFIX=/path/to/install ..
$ [make install]
```
The commands in first two lines generate a clean environment for cmake. This procedure is called 'out-of-source build'. The third line provide a detailed requirement of `cmake` and we should never miss the `..` in the end since the cmake file locates at the above shell. And forth line conducts the compile with -N cores, e.g. `make -j32`. We can use command `nproc` to find out how many cores we can use. The forth line provide the position of the executive file where we are about to generate them. The last line will install and generate the conductive file in the direcotry `/path/to/install`.  

However, during the `make`, it reports several warning like
```
Warning: Type mismatch in argument ‘a’ at (1); passed COMPLEX(8) to REAL(8) [-Wargument-mismatch] 
/fs1/home/wanghua/guozhch/soft/qe-7.2/q-e/KS_Solvers/CG/ccgdiagg_gpu.f90:383:19:

         b0 = ksDdot( kdim2, cg_d(1), 1, ppsi_d(1), 1 ) / cg0**2
```
I don't know if it is incompatible between qe-7.x and compiler `Intel_compiler/19.1.2(default)`.  
And the test is not successful, breaking down at the first iteration.
```
[th-hpc4-ln1:4080677:0:4080677] Caught signal 11 (Segmentation fault: invalid permissions for mapped object at address 0x7fffdb5b8f5c)
==== backtrace (tid:4080677) ====
0 0x00000000000534c9 ucs_debug_print_backtrace()  ???:0
1 0x0000000000012b20 .annobin_sigaction.c()  sigaction.c:0
=================================
Program received signal SIGSEGV: Segmentation fault - invalid memory reference.

Backtrace for this error:
#0  0x14c497120171 in ???
#1  0x14c49711f313 in ???
#2  0x14c49518ab1f in ???
#3  0x7fffdb5b8f5c in ???
Segmentation fault (core dumped）
```

### My second try ###
Here I use the method published by [AronHung](https://www.bilibili.com/opus/782400564586610696) 
We need to first find our which module should we use. To do this, we can use command `module avail` or simply `module av` to find out all the module we can use. Then, use command `module purge` to clean the loaded module for a clean environment for compile.  
Here we adopt these modules for compile
```
Currently Loaded Modulefiles:
 1) Intel_compiler/19.1.2(default)   3) hdf5/1.12.0-icc19.1-openmpi  
 2) MPI/openmpi/3.1.6-icc19.1        4) MKL/19.1.2(default)
```
Remember these module and we will use these settings to write a corresponding submit file.  
We can use the following commands to get the directory of compiler and math database.
```
which mpirun
which mpiifort
which ifort
echo $MKLROOT
```
All the environment have been set already, let's turn to the qe git repository. If we have compiled these before, we should use command `make clean` and `make distclean` to clean all the changes.  
Then we generate a new `make.inc` file by the following command
```
./configure --prefix=/your/install/path MPIF90=mpifort CC=icc F90=ifort F77=ifort --enable-parallel
```
Notice these setting should be consistent with the compiler and database. The reference use command `./configure --prefix=path  MPIF90=mpiifort CC=mpiicc F90=ifort F77=mpiifort -enable-parallel` but we need to change these parameters to the correct value (we should use `which` command to find out whether we can achieve these parameters).  
Then we have done all the prerequisites. Then just use `make all install` to generate executive file in `/your/install/path/bin`. Don't use parallel compile which may cause a collapse (but I don't know the reason).  
We also negelct the third step in the reference, i.e. 
```
1. FFLAGS = -O3 -assume byterecl -g -traceback
2. BLAS_LIBS = -L${MKLROOT}/lib/intel64 -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lmkl_blacs_intelmpi_lp64 -lpthread -lm -ldl
3. LAPACK_LIBS = -L${MKLROOT}/lib/intel64 -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lmkl_blacs_intelmpi_lp64 -lpthread -lm -ldl
4. SCALAPACK_LIBS = -L${MKLROOT}/lib/intel64 -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lmkl_blacs_intelmpi_lp64 -lpthread -lm -ldl
5. FFT_LIBS = -L${MKLROOT}/lib/intel64 -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lmkl_blacs_intelmpi_lp64 -lpthread -lm -ldl
6. MPI_LIBS = -L/home/probe/app/intel/impi/2019.1.144/intel64/lib -lmpi
```
It seems the `make.inc` can automatically find these pathway. If we insist on filling these parameters, we should make sure it is consistent with the module we used, i.e. these parameters are compatible with INTEL MPI but we use OPENMPI herem we should replace the first line as `BLAS_LIBS = -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lmkl_blacs_openmpi_lp64 -lmkl_scalapack_lp64`. Otherwise it may collapse when we actually conduct calculation:
```
 1 forrtl: severe (174): SIGSEGV, segmentation fault occurred
  2 Image              PC                Routine            Line        Source
  3 pw.x               00000000010413BA  Unknown               Unknown  Unknown
  4 libpthread-2.28.s  000014A0EBCC6B20  Unknown               Unknown  Unknown
  5 libmpi.so.40.10.4  000014A0EAC4A941  PMPI_Comm_size        Unknown  Unknown
  6 libmkl_blacs_inte  000014A0EBEFDDC9  MKLMPI_Comm_size      Unknown  Unknown
  7 libmkl_blacs_inte  000014A0EBEFC041  mkl_blacs_init        Unknown  Unknown
  8 libmkl_blacs_inte  000014A0EBEFBF88  Cblacs_pinfo          Unknown  Unknown
  9 libmkl_blacs_inte  000014A0EBEEC86F  blacs_gridmap_        Unknown  Unknown
 10 libmkl_blacs_inte  000014A0EBEEC24E  blacs_gridinit_       Unknown  Unknown
 11 pw.x               0000000000EFE112  laxlib_start_drv_         250  la_helper.f90
 12 pw.x               0000000000A953A0  set_para_diag_             46  set_para_diag.f90
 13 pw.x               00000000005CB8C4  setup_                    825  setup.f90
 14 pw.x               0000000000593E06  run_pwscf_                140  run_pwscf.f90
 15 pw.x               0000000000411DEF  MAIN__                     85  pwscf.f90
 16 pw.x               0000000000411C62  Unknown               Unknown  Unknown
 17 libc-2.28.so       000014A0EA80D493  __libc_start_main     Unknown  Unknown
 18 pw.x               0000000000411B6E  Unknown               Unknown  Unknown
 19 yhrun: error: cn1710: task 0: Exited with exit code 174
 20 yhrun: First task exited 60s ago
 21 yhrun: StepId=2216748.0 tasks 1-35: running
 22 yhrun: StepId=2216748.0 task 0: exited abnormally
 23 yhrun: launch/slurm: _step_signal: Terminating StepId=2216748.0
 24 yhrun: Job step aborted: Waiting up to 32 seconds for job step to finish.
 25 slurmstepd: error: *** STEP 2216748.0 ON cn1710 CANCELLED AT 2025-05-09T16:50:50 ***
 26 yhrun: error: cn1710: tasks 1-35: Killed
```

## Submit Jobs
Here is a general template for job submitting
```

  1 #!/bin/bash
  2 #---------------------- sys setup ----------------------#
  3 #module purge
  4 #module load VASP/5.4.1-intel-2016b
  5 #module load intel/2017A
  6 
  7 #yhbatch -N1 -n36 -pcp1  run.vasp
  8 #WORKDIR=`pwd`
  9 #---------------------- job setup ----------------------#
 10 #cd ${WORKDIR}
 11 #log=${WORKDIR}/job.txt
 12 
 13 # echo "job start: "`date` > ${log}
 14 # echo "work directory: "$WORKDIR >> $log
 15 topdir=`pwd`
 16 
 17 
 18 EXEC=/fs1/home/wanghua/guozhch/soft/qe-7.2/qe7.2install/bin/pw.x
 19 #EXEC=/fs1/home/wanghua/soft/6.2.1-icc19.1-IMPI2019.8/vasp_ncl_wannier
 20 #EXEC=/fs1/home/wanghua/bin/vasp.5.3.3
 21 
 22 module purge
 23 module load  Intel_compiler/19.1.2
 24 module load  hdf5/1.12.0-icc19.1-openmpi
 25 module load  MPI/openmpi/3.1.6-icc19.1
 26 module load  MKL/19.1.2
 27 # source /fs1/software/intel/oneapi/2021.3/setvars.sh
 28 yhrun -N1 -n36 -pcp1 ${EXEC} < scf.in > scf.out
 29 

```
We first use `module purge` the make sure our environment is clean and use `module load` to load the modules we used while compiling. After that, use `yhrun` to run our jobs. 
The detailed process of a dft2kp job testing can be find in [the document of dft2kp](https://dft2kp.gitlab.io/dft2kp/main/quickstart.html)  
The final output for graphene is
```
Space group  191 : P6/mmm                                                                             
Group of the k-vector: <code not ready>                                                               
Verifying set A: [3, 4]                                                                               
Band indices: [3, 4] Irreps: (K6) Degeneracy: 2                                                       
Matrix([[c0 + c3*k_z**2 + c4*k_x**2 + c4*k_y**2, -c1*k_x + I*c1*k_y + c2*k_x**2/2 + I*c2*k_x*k_y - c2*
k_y**2/2], [-c1*k_x - I*c1*k_y + c2*k_x**2/2 - I*c2*k_x*k_y - c2*k_y**2/2, c0 + c3*k_z**2 + c4*k_x**2 + c4*k_y**2]])                                                                                        cn      a.u. (Ry, a0)    with (eV, nm)  units    k powers                                             
----  ---------------  ---------------  -------  ----------                                           
c0          -1.39e-05        -0.00019   eV       0                                                    
c1           0.719            0.517     eV.nm    x,y                                                  
c2          -1.65            -0.0628    eV.nm²   xx,xy,yy                                            
c3           0.0282           0.00107   eV.nm²   zz                                                  
c4          -0.00616         -0.000235  eV.nm²   xx,yy

```
consistent with the result in the document (slight different because of the different definition of parameters).
