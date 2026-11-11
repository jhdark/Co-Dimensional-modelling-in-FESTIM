"""The two permeator cases of Rader, Greenwood and Humrickhouse, Nucl. Technol. 203
(2018) 58, DOI 10.1080/00295450.2018.1431505, read from the OSTI accepted manuscript.

Geometry and conditions are their Table I, properties their Table II (activation
energies in J/mol), and the Sherwood numbers and efficiencies their Table III. The
analytical solutions are those of Humrickhouse and Merrill, Fusion Sci. Technol. 68
(2015) 295, DOI 10.13182/FST14-941 (Sieverts liquid), and of Rader et al. (Henry
liquid).

NOT stated in the source, inferred here and to be checked by the authors:
  - the units of the solubilities. The published regime number xi = 174 of the FLiBe
    case is recovered with the nickel solubility read per MPa^0.5 and an inlet
    concentration of 1 mol/m3; both are assumptions.
  - the inlet concentration of the Pb-17Li case, which is linear and does not matter.
"""

import numpy as np
from scipy.special import lambertw

R = 8.314462618  # J/mol/K


def arrhenius(pre, energy, T):
    return pre * np.exp(-energy / (R * T))


class Case:
    def __init__(self, name, law, length, d_inner, wall, velocity, T, sherwood,
                 D_liquid, K_liquid, D_solid, K_solid, c_in, eta_published):
        self.name, self.law = name, law
        self.length, self.r_i, self.r_o = length, d_inner / 2, d_inner / 2 + wall
        self.velocity, self.T, self.c_in = velocity, T, c_in
        self.D_liquid, self.K_liquid = D_liquid, K_liquid
        self.D_solid, self.K_solid = D_solid, K_solid
        self.k_t = sherwood * D_liquid / d_inner  # film mass-transfer coefficient
        self.eta_published = eta_published  # (analytical, Modelica) of Table III

    # ---- analytical solution ----
    @property
    def wall_group(self):
        """Phi_s / (K_T d ln(d_o / d))."""
        d = 2 * self.r_i
        return self.D_solid * self.K_solid / (self.k_t * d * np.log(self.r_o / self.r_i))

    def tau(self, z):
        return 4 * self.k_t * np.asarray(z) / (self.velocity * 2 * self.r_i)

    def efficiency(self, z):
        """Fraction extracted after a length ``z`` of tube."""
        if self.law == "sieverts":
            zeta = 2 * self.wall_group / self.K_liquid
            return 1 - np.exp(-self.tau(z) * zeta / (1 + zeta))
        xi = self.wall_group**2 / (self.c_in * self.K_liquid)
        s = np.sqrt(1 / xi + 1)
        w = lambertw(np.exp(s + np.log(s - 1) - self.tau(z) - 1)).real
        return 1 - xi * (w**2 + 2 * w)

    def regime_number(self):
        if self.law == "sieverts":
            return 2 * self.wall_group / self.K_liquid  # zeta
        return self.wall_group**2 / (self.c_in * self.K_liquid)  # xi


T1 = 743.15
PBLI = Case(
    name="Pb-17Li / RAFM steel", law="sieverts",
    length=37.3, d_inner=10e-3, wall=0.5e-3, velocity=1.768, T=T1, sherwood=1310,
    D_liquid=arrhenius(2.5e-7, 27000, T1), K_liquid=arrhenius(1.26e-3, 1350, T1),
    D_solid=arrhenius(1e-7, 13200, T1), K_solid=arrhenius(0.872, 28600, T1),
    c_in=1.0, eta_published=(0.690, 0.684),
)
T2 = 973.15
FLIBE = Case(
    name="FLiBe / nickel", law="henry",
    length=50.0, d_inner=25.4e-3, wall=0.25e-3, velocity=2.5, T=T2, sherwood=837,
    D_liquid=arrhenius(9.3e-7, 42000, T2), K_liquid=8.27e-9 * np.exp(4.27e-3 * T2),
    D_solid=arrhenius(7.43e-7, 44100, T2), K_solid=arrhenius(953, 10700, T2) * 1e-3,
    c_in=1.0, eta_published=(0.415, 0.414),
)
CASES = [PBLI, FLIBE]

if __name__ == "__main__":
    for c in CASES:
        print(f"{c.name}: K_T = {c.k_t * 1e3:.3f} mm/s, regime number = "
              f"{c.regime_number():.3g}, eta = {float(c.efficiency(c.length)):.4f}, "
              f"published {c.eta_published}")
