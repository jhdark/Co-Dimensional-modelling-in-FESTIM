"""Application 2, Be/BeO: filling of the interface against molecular dynamics.

Reproduces the interface concentration against time that Hodille et al. obtained by
molecular dynamics for the Be/BeO(0001) and Be/BeO(000-1) interfaces, labelled "0001"
and "0001b" here, at 750, 1000 and 1250 K.

SOURCE: E. A. Hodille, J. Byggmastar, Y. Ferro, K. Nordlund, "Molecular dynamics study
of hydrogen isotopes at the Be/BeO interface", J. Phys.: Condens. Matter (2022),
DOI 10.1088/1361-648X/ac8328 (postprint HAL hal-03736200).
  - the model is their Eq. (6), with no exchange on the BeO side and a constant
    concentration in the beryllium
  - the rate constants are their Table 1
  - lambda_Be = 2 x 1.577 Angstrom, c_Be = 5e27 m-3 and n_i = 1e20 m-2 are the values
    stated in their Sec. on rate-equation modelling
  - the interface starts from the concentration already trapped in the first MD frame,
    which is the time delay of their Eqs. (7) and (8)

    d c_I/dt = nu_trap lambda c_Be (1 - c_I / N_SITES) - nu_detrap c_I

MD DATA: ``data/D_trapped_at_0001.csv`` and ``data/D_trapped_at_000-1.csv`` are the raw
time series behind their Fig. 12, supplied by the authors. They are used at 750 and
1250 K. Their 1000 K columns are NOT used: over the first 6 ns the rows alternate
between two separate curves, and the column disagrees with the published figure up to
about 13 ns, whereas the 750 and 1250 K columns reproduce it. Until a corrected file is
supplied, the 1000 K points are those digitised from Fig. 12
(``data/hodille_2022_data.csv``).

In FESTIM the interface is a point manifold (``dim=0``) on the end of a 1D beryllium
slab. The slab is a reservoir: thick and fast enough that it stays uniform.

Writes ``be_beo.csv``, ``be_beo_error.csv`` and ``be_beo.pdf``. Run with ``--plot`` to redraw only.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import festim as F
import pandas as pd
from common import *

HERE = pathlib.Path(__file__).resolve().parent
K_B = 8.617e-5  # eV/K, as in the supplied script

LAMBDA_BE = 2 * 1.577e-10  # m
N_SITES = 1e20  # m-2
C_BE = 0.5e28  # m-3
FINAL_TIME, N_STEPS = 20e-9, 200  # s
TEMPERATURES = [750.0, 1000.0, 1250.0]
# (prefactor in s-1, activation energy in eV)
TRAPPING = {"0001": (3.285e10, 0.231), "0001b": (3.217e10, 0.229)}
DETRAPPING = {"0001": (4.104e9, 0.229), "0001b": (1.877e10, 0.292)}

# reservoir: uniform over the run, and far larger than what the interface takes
L_BE, D_BE = 1e-3, 1.0  # m, m2/s


def arrhenius(pair, T):
    return pair[0] * np.exp(-pair[1] / (K_B * T))


def run(interface, T, c_0):
    nu_trap = arrhenius(TRAPPING[interface], T)
    nu_detrap = arrhenius(DETRAPPING[interface], T)

    beryllium = F.VolumeSubdomain1D(
        id=1, borders=[0.0, L_BE], material=F.Material(D_0=D_BE, E_D=0.0)
    )
    plane = F.VolumeSubdomain(
        id=2, dim=0, material=F.Material(D_0=1.0, E_D=0.0),
        locator=lambda x: np.isclose(x[0], L_BE, rtol=0.0, atol=1e-12),
    )
    c_be = F.Species("c_be", subdomains=[beryllium])
    c_i = F.Species("c_i", subdomains=[plane])
    pair = {"cb": c_be, "ci": c_i}

    def J(cb, ci):
        return nu_trap * LAMBDA_BE * cb * (1 - ci / N_SITES) - nu_detrap * ci

    model = F.HydrogenTransportProblemDiscontinuous(
        mesh=F.Mesh1D(np.linspace(0.0, L_BE, 201)),
        species=[c_be, c_i],
        subdomains=[beryllium, plane],
        sources=[F.ParticleSource(value=J, species=c_i, volume=plane,
                                  species_dependent_value=pair)],
        boundary_conditions=[
            F.ParticleFluxBC(subdomain=plane, species=c_be,
                             value=lambda cb, ci: -J(cb, ci), species_dependent_value=pair)
        ],
        initial_conditions=[
            F.InitialConcentration(value=C_BE, species=c_be, volume=beryllium),
            F.InitialConcentration(value=c_0, species=c_i, volume=plane),
        ],
        temperature=T,
        settings=F.Settings(atol=1e8, rtol=1e-10, transient=True, final_time=FINAL_TIME,
                            stepsize=FINAL_TIME / N_STEPS),
        exports=[F.TotalVolume(field=c_i, volume=plane)],
    )
    model.show_progress_bar = False
    model.initialise()
    model.run()
    t, c = np.array(model.exports[0].t), np.array(model.exports[0].data)
    # the same balance integrated exactly, for a constant reservoir
    a = nu_trap * LAMBDA_BE * C_BE
    rate = a / N_SITES + nu_detrap
    exact = a / rate + (c_0 - a / rate) * np.exp(-rate * t)
    return t, c, exact


RAW_FILES = {"0001": "D_trapped_at_0001.csv", "0001b": "D_trapped_at_000-1.csv"}
DIGITISED_ONLY = [1000.0]  # raw column unusable, see the docstring


def md_data():
    """The MD points as {(interface, T): (t in s, c_I in m-2)}."""
    out = {}
    for interface, name in RAW_FILES.items():
        raw = pd.read_csv(HERE / "data" / name)
        for T in TEMPERATURES:
            if T not in DIGITISED_ONLY:
                out[(interface, T)] = np.array([raw["time(ns)"] * 1e-9, raw[f"N_D_at_{T:.0f}K"]])
    path = HERE / "data" / "hodille_2022_data.csv"
    with open(path) as f:
        names = f.readline().strip().split(",")
    raw = pd.read_csv(path, skiprows=2, header=None)
    for i in range(0, len(names) - 1, 2):
        T, interface = names[i].split("_")
        if float(T) in DIGITISED_ONLY:
            xy = raw[[i, i + 1]].apply(pd.to_numeric, errors="coerce").dropna().to_numpy()
            out[(interface, float(T))] = xy[np.argsort(xy[:, 0])].T
    return out


def relative_error(t_md, c_md, t, c):
    """The measure of Hodille et al.: int |c_MD - c| dt / int c_MD dt."""
    return np.trapezoid(np.abs(c_md - np.interp(t_md, t, c)), t_md) / np.trapezoid(c_md, t_md)


def main():
    md = md_data()
    rows, errors = [], []
    for interface in TRAPPING:
        for T in TEMPERATURES:
            t_md, c_md = md[(interface, T)]
            # raw series: the first frame. Digitised points: the mean of the earliest five
            c_0 = c_md[:5].mean() if T in DIGITISED_ONLY else c_md[0]
            t, c, exact = run(interface, T, c_0)
            t, c, exact = np.insert(t, 0, 0.0), np.insert(c, 0, c_0), np.insert(exact, 0, c_0)
            rows.append(pd.DataFrame({"interface": interface, "T": T, "t": t,
                                      "c_i": c, "exact": exact}))
            errors.append({"interface": interface, "T": T, "c_0": c_0,
                           "md_source": "digitised" if T in DIGITISED_ONLY else "raw",
                           "relative_error": relative_error(t_md, c_md, t, c)})
            print(interface, T, "final c_I", c[-1], "max rel. diff to exact",
                  np.max(np.abs(c[1:] - exact[1:]) / exact[1:]),
                  "error against MD", errors[-1]["relative_error"], flush=True)
    pd.concat(rows).to_csv(HERE / "be_beo.csv", index=False)
    pd.DataFrame(errors).to_csv(HERE / "be_beo_error.csv", index=False)
    plot()


def plot():
    df = pd.read_csv(HERE / "be_beo.csv")
    md = md_data()
    fig, axes = plt.subplots(1, 2, figsize=(COL2, 2.4), sharey=True)
    for ax, interface, title in zip(axes, TRAPPING, ("(a)", "(b)")):
        for T, colour in zip(TEMPERATURES, PALETTE):
            sub = df[(df.interface == interface) & (df["T"] == T)]
            t_md, c_md = md[(interface, T)]
            raw = T not in DIGITISED_ONLY
            ax.plot(t_md * 1e9, c_md, "o", ms=1.2 if raw else 2.2, color=colour,
                    alpha=0.3 if raw else 0.45, mew=0, rasterized=True)
            ax.plot(sub.t * 1e9, sub.c_i, color=colour, label=f"{T:.0f} K")
        ax.set_xlabel("Time (ns)")
        ax.set_xlim(0, FINAL_TIME * 1e9)
        ax.set_ylim(0)
        ax.set_title(f"{title}  interface {interface}", loc="left")
    axes[0].set_ylabel(r"Interface concentration (m$^{-2}$)")
    axes[1].plot([], [], "o", ms=2.2, color="grey", label="molecular dynamics")
    axes[1].legend(loc="lower right", ncol=2)
    fig.tight_layout()
    savefig(fig, __file__, "be_beo")


if __name__ == "__main__":
    plot() if "--plot" in sys.argv else main()
