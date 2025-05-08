# Install DFT2KP
## Install python package for DFT2KP
Here I recommend use `conda create -n qsymm-env python=3.10` to generate a clean virtual environment for further use.  
Then use `conda install` to install all the requirement which is achievable for conda, i.e.     'numpy<=1.26.4', 'scipy', 'sympy<=1.10', 'tabulate', 'matplotlib', 'qsymm'.  
And I notice when I install 'qsymm', conda automatically install a package called 'tinyarray' for me, which is necessary for the left package. But I has not figured out what it is right now.  
The we can use `pip install` for the left two requirement, 'irrep<=1.8.2', 'irreptables', and our goal 'dft2kp'.  
Till now, I have finished the first step.
