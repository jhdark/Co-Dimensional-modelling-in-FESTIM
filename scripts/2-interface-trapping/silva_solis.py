"""The multi-site W/Cu interface network of Silva-Solis (thesis Ch. 5), as data.

SOURCE: Y. Silva-Solis, PhD thesis, Aix-Marseille Universite, 2024 (HAL tel-04750846),
PDF pages 127 (Eq. 5.16), 133-135 (model), 137 (Table 1), 139 (Table 2), 141 (Table 3),
146 (Table 5).

Fourteen sites: two on the W side held at a fixed concentration (Td-31, Td-86), ten in
the interfacial region (areal densities, m-2), and two on the Cu side (Oh-2, Oh-54,
volumetric, each a layer one jump distance thick). They are joined by the "green" and
"pink" paths and bridged by the "blue" one.

Jump frequencies follow Wert and Zener, nu_0 = sqrt(E_a / (2 m lambda**2)), thesis
Eq. (3), times the Boltzmann factor. The thesis then corrects four of them so that the
steady state matches its thermodynamic model (Table 3).
"""

import numpy as np

K_B = 8.617333262e-5  # eV/K
EV = 1.602176634e-19  # J
M_H = 1.6735575e-27  # kg

# (i, j, jump distance in Angstrom, barrier i -> j in eV, barrier j -> i in eV), Table 1
EDGES = [
    (31, 29, 1.286, 0.257, 0.455),
    (29, 27, 1.260, 0.073, 0.390),
    (27, 25, 1.038, 0.856, 0.721),
    (25, 4, 1.389, 0.065, 0.456),
    (4, 43, 1.401, 0.754, 0.410),
    (43, 2, 1.319, 0.756, 0.873),
    (86, 87, 1.305, 0.257, 0.455),
    (87, 84, 1.272, 0.080, 0.396),
    (84, 89, 0.803, 0.128, 0.001),
    (89, 63, 1.241, 0.078, 0.206),
    (63, 60, 1.562, 0.204, 0.117),
    (60, 79, 1.593, 0.240, 0.192),
    (79, 54, 1.468, 0.113, 0.247),
    (25, 24, 1.260, 0.111, 0.132),
    (24, 89, 1.260, 0.110, 0.130),
]
GREEN = [31, 29, 27, 25, 4, 43, 2]
PINK = [86, 87, 84, 89, 63, 60, 79, 54]
W_SITES, CU_SITES = (31, 86), (2, 54)
LAYER = {31: 1.286e-10, 86: 1.305e-10, 2: 1.319e-10, 54: 1.468e-10}  # m
N_SITES = 1.75e9 / 1.21e-10  # m-2 per interfacial site, from Table 2

# Table 3: corrected frequencies (Hz) of the jumps INTO Oh-4, Oh-63, Oh-2 and Oh-54
CORRECTED = {
    340.0: {(25, 4): 2.66e13, (89, 63): 2.36e12, (43, 2): 6.59e1, (79, 54): 2.56e11},
    430.0: {(25, 4): 2.42e13, (89, 63): 2.35e12, (43, 2): 2.07e4, (79, 54): 5.81e11},
    550.0: {(25, 4): 2.24e13, (89, 63): 2.36e12, (43, 2): 2.37e6, (79, 54): 1.13e12},
}
# W-side concentration (m-3) used at each temperature, Table 2
C_W = {340.0: 2.30e7, 430.0: 1.81e11, 550.0: 2.69e14}
# steady concentrations of the thesis, 340 K (m-2 for 4 and 63, m-3 for 2 and 54)
TABLE_2_KINETIC = {4: 9.09e7, 2: 3.87e14, 63: 2.56e5, 54: 1.93e15}  # uncorrected
TABLE_3 = {4: 1.75e9, 2: 1.73e15, 63: 5.55e5, 54: 3.22e15}  # corrected, paths apart
TABLE_5 = {4: 6.28e9, 2: 6.20e15, 63: 4.97e5, 54: 2.88e15}  # corrected, paths bridged
TAU_S = {340.0: 2.63e3, 430.0: 1.06, 550.0: 1.55e-3}  # s, time to steady state


def wert_zener(E, lam, T):
    return np.sqrt(E * EV / (2 * M_H * (lam * 1e-10) ** 2)) * np.exp(-E / (K_B * T))


def frequencies(T, corrected=True, paths=("green", "pink", "blue")):
    """{(i, j): frequency of the jump i -> j} for the requested paths."""
    keep = set()
    if "green" in paths:
        keep |= set(zip(GREEN, GREEN[1:]))
    if "pink" in paths:
        keep |= set(zip(PINK, PINK[1:]))
    if "blue" in paths:
        keep |= {(25, 24), (24, 89)}
    nu = {}
    for i, j, lam, forward, backward in EDGES:
        if (i, j) not in keep:
            continue
        nu[(i, j)] = wert_zener(forward, lam, T)
        nu[(j, i)] = wert_zener(backward, lam, T)
    if corrected:
        nu.update({k: v for k, v in CORRECTED[T].items() if k in nu})
    return nu


def chain_steady_state(T, path, corrected):
    """Dilute steady state of one path, thesis Eqs. (8a) and (8b)."""
    nu = frequencies(T, corrected, paths=("green", "pink"))
    c = {path[0]: C_W[T] * LAYER[path[0]]}  # as an areal density
    for a, b in zip(path, path[1:]):
        c[b] = c[a] * nu[(a, b)] / nu[(b, a)]
    c[path[-1]] /= LAYER[path[-1]]  # the Cu-side site is volumetric
    return c


if __name__ == "__main__":
    for label, corrected, table in (("uncorrected", False, TABLE_2_KINETIC),
                                    ("corrected", True, TABLE_3)):
        print(label, "(ours / thesis):")
        for path in (GREEN, PINK):
            c = chain_steady_state(340.0, path, corrected)
            for site in path:
                if site in table:
                    print(f"   site {site:2d}: {c[site]:.3e} / {table[site]:.3e}")
