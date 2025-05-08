# Install DFT2KP
## Install python package for DFT2KP
Here I recommend use `conda create -n qsymm-env python=3.10` to generate a clean virtual environment for further use.  
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
Here we use **intel oneapi** to compile the QE program. First we need to find the directory of intel oneapi (cd /fs1/software/intel/oneapi) use `source setvars.sh` to acticate oneapi.

**My first try**  
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
