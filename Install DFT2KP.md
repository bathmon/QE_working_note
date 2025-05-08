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
