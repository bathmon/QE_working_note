import numpy as np
import pydft2kp as dft2kp
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 18})


# import s0, sx, sy, sz: Pauli matrices
from pydft2kp.constants import s0, sx, sy, sz

# step 1: read DFT data
kp = dft2kp.irrep(dftdir='graphene',
                  outdir='outdir',
                  prefix='graphene',
                  kpt=31,           
                  kname='K')

# step 2: read or calculate matrix elements of p
kp.get_p_matrices(qekp='kp.dat')

# step 3: define the set alpha
#         applies fold down via Löwdin
setA = [3, 4]
kp.define_set_A(setA)

# step 4: builds optimal model with qsymm
phi = 2*np.pi/3
U = np.diag([np.exp(1j*phi), np.exp(-1j*phi)])
C3 = dft2kp.rotation(1/3, [0,0,1], U=U)
My = dft2kp.mirror([0,1,0], U=sx)
Mz = dft2kp.mirror([0,0,1], U=-s0)
TI = dft2kp.PointGroupElement(R=-np.eye(3), 
                              conjugate=True, 
                              U=sx)
symms = [C3, My, Mz, TI]
qs = dft2kp.qsymm(symms, total_power=2, dim=3);

# step 5: calculate the representation matrices
kp.get_symm_matrices()
# (optional): adds anti-unitary symmetry
kp.add_antiunitary_symm(TI, np.array([0,0,0]))

# step 6: calculates and applies 
#         the transformation U
optimal = dft2kp.basis_transform(qs, kp)

# step 7: print results
optimal.print_report(sigdigits=3)

# step 8: plot the result
# kpath as run in the bands calculation of QE
kpath = [[         30,     30,     30], 
         [R'$\Gamma$', R'$K$', R'$M$']]

# init plotter
bands = dft2kp.qe_plotter(kp, 'bands.gnu', kpath)

# crude and optimal models as H(kx,ky,kz)

# build crude model with all bands
H_crude_full = kp.build_H_of_k(all_bands=True)
# build crude model folded into set A
H_crude_setA = kp.build_H_of_k(all_bands=False)

# the optimal model for set was already computed
# in step 6 above: optimal.Heff

# compute the eigenenergies as a function k for the path used in QE's data
Efull = np.array([np.linalg.eigvalsh(H_crude_full(*kvec)) for kvec in bands.k3D])
EsetA = np.array([np.linalg.eigvalsh(H_crude_setA(*kvec)) for kvec in bands.k3D])
Ek = np.array([np.linalg.eigvalsh(optimal.Heff(*kvec)) for kvec in bands.k3D])

plt.figure(figsize=(6,8))
pdft   = plt.plot(bands.kdist, bands.bands, 'o', c='C0', ms=5) 
pcrude = plt.plot(bands.kdist, Efull, c='black', lw=2)
poptim = plt.plot(bands.kdist, Ek, c='red', lw=2)
# set legends for single lines
pdft[0].set_label('QE/DFT')
pcrude[0].set_label('Crude: all bands')
poptim[0].set_label(r'Optimal: set $\alpha$')
plt.legend(fontsize=12)
bands.set_labels_and_limits(ax=plt.gca(), ymin=-1, ymax=1)
plt.grid()

plt.tight_layout()
# basename = 'Figures/' + kp.dftdir.replace('/', '')
basename = 'graphene'
plt.savefig(basename + '.svg')
plt.savefig(basename + '.png')
# plt.show()


