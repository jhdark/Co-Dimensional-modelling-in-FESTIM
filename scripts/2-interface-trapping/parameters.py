"""Parameters for Application 2: the W/Cu interface carrying its own inventory.

SOURCE: Y. Silva-Solis, PhD thesis, Aix-Marseille Universite, 2024 (HAL tel-04750846),
Chapter 5 "Diffusion of H within the W/Cu interface" (paper reproduced in the thesis;
page numbers below are PDF pages of paper_references/yosvany_thesis.pdf).

What is taken from the thesis as printed:
  - bulk diffusivities, Sec. 3.2 (PDF p. 137)
  - the activation energies and jump distances of the "green" path, Table 1 (p. 137)
  - the areal density of interfacial sites, from Table 2 (p. 139): the Oh-4 row gives
    1.21e-10 at.fr. = 1.75e9 m-2, i.e. 1.45e19 m-2 per unit occupancy
  - the fitted characteristic frequency of the interface, nu_0 = 7.84e12 Hz (p. 143)
  - the three temperatures, those at the rear of the W armour (p. 135)

What is OUR REDUCTION, not the thesis's, and must be checked by the authors:
  - the seven-site green path (Td-31 ... Oh-4 ... Oh-2) is collapsed onto three states,
    W side / interface (Oh-4) / Cu side, following the three-site picture of Hodille et
    al. for Be/BeO. Each effective barrier is the highest saddle met between two states,
    measured from the state the jump leaves. See ``landscape()``.
  - one attempt frequency, the fitted nu_0, is used for all four jumps.
  - the pink and blue paths are ignored: Oh-4 is the dominant trap (thesis p. 140-143).

NOMINAL choices, not from any source: layer thicknesses and the surface concentration.
"""

import numpy as np

K_B = 8.617333262e-5  # eV/K

# ---- bulk diffusivities (thesis Sec. 3.2) ----
D_W_0, E_D_W = 4.99e-7, 0.23  # m2/s, eV
D_CU_0, E_D_CU = 2.07e-6, 0.34
# in-plane diffusion along the interface; unused in 1D, kept for a 2D case
D_INT_0, E_D_INT = 2.09e-6, 0.46

# ---- green path, Table 1: (forward barrier, backward barrier) in eV, W -> Cu ----
GREEN_PATH = {
    "31-29": (0.257, 0.455),
    "29-27": (0.073, 0.390),
    "27-25": (0.856, 0.721),
    "25-4": (0.065, 0.456),
    "4-43": (0.754, 0.410),
    "43-2": (0.756, 0.873),
}
INTERFACE_SITE = 4  # index of Oh-4 in the list of sites below
LAMBDA_W = 1.286e-10  # m, jump distance 31 -> 29
LAMBDA_CU = 1.319e-10  # m, jump distance 43 -> 2

N_SITES = 1.75e9 / 1.21e-10  # m-2, interfacial sites (Oh-4)
NU_0 = 7.84e12  # Hz

TEMPERATURES = [340.0, 430.0, 550.0]  # K


def landscape():
    """Site and saddle energies along the green path, relative to the W-side site."""
    sites, saddles = [0.0], []
    for forward, backward in GREEN_PATH.values():
        saddles.append(sites[-1] + forward)
        sites.append(saddles[-1] - backward)
    return np.array(sites), np.array(saddles)


_sites, _saddles = landscape()
E_INTERFACE = _sites[INTERFACE_SITE]  # eV, relative to the W side
E_CU = _sites[-1]
_top_w = _saddles[:INTERFACE_SITE].max()
_top_cu = _saddles[INTERFACE_SITE:].max()

# effective barriers of the three-state reduction
E_W_TO_I = _top_w - 0.0
E_I_TO_W = _top_w - E_INTERFACE
E_I_TO_CU = _top_cu - E_INTERFACE
E_CU_TO_I = _top_cu - E_CU


def rates(T):
    """Jump frequencies (Hz) of the three-state reduction at temperature ``T``."""
    f = lambda E: NU_0 * np.exp(-E / (K_B * T))
    return {
        "w_to_i": f(E_W_TO_I),
        "i_to_w": f(E_I_TO_W),
        "i_to_cu": f(E_I_TO_CU),
        "cu_to_i": f(E_CU_TO_I),
    }


def partition(T):
    """Equilibrium ratio c_Cu / c_W across the interface, dilute limit."""
    r = rates(T)
    return (r["w_to_i"] * LAMBDA_W * r["i_to_cu"]) / (r["i_to_w"] * r["cu_to_i"] * LAMBDA_CU)


# ---- NOMINAL geometry and loading ----
L_W = 6.0e-3  # m, tungsten armour
L_CU = 1.0e-3  # m, copper interlayer
C_SURFACE = 1.0e20  # m-3, mobile concentration held on the plasma-facing surface

if __name__ == "__main__":
    print("site energies (eV):  ", np.round(_sites, 3))
    print("saddle energies (eV):", np.round(_saddles, 3))
    for name in "E_W_TO_I E_I_TO_W E_I_TO_CU E_CU_TO_I E_INTERFACE E_CU N_SITES".split():
        print(f"{name:12s} {globals()[name]:.4g}")
    for T in TEMPERATURES:
        print(T, {k: f"{v:.3e}" for k, v in rates(T).items()}, f"c_Cu/c_W = {partition(T):.3e}")
