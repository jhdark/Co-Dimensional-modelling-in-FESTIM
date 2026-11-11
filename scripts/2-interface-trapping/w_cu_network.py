"""Application 2, W/Cu: the multi-site kinetic model of Silva-Solis on one manifold.

Reproduces the 0D rate-equation model of the thesis (Eq. 5.16) inside FESTIM. The
twelve interfacial sites and the two Cu-side sites are fourteen species on a single
point manifold (``dim=0``) at the end of a 1D tungsten slab held at the concentration
the thesis fixes on the W side. Every jump between two sites is a pair of opposite
sources on the manifold; the two jumps out of tungsten are also a flux on the bulk.

    site i <-> site j :  f = nu_ij C_i (1 - theta_j) - nu_ji C_j (1 - theta_i)

The Cu-side sites are volumetric in the thesis, each a layer one jump distance thick.
Here they are carried as areal densities ``lambda C`` and converted back on output.

The thesis holds the W-side concentration fixed. ``reservoir=True`` reproduces that by
giving the slab a diffusivity high enough to stay uniform. ``reservoir=False`` uses the
diffusivity of tungsten, and the supply through the slab then limits the filling.

Writes ``w_cu_network.csv`` (time histories), ``w_cu_network_summary.csv`` and
``w_cu_network.pdf``. Run with ``--plot`` to redraw only.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import festim as F
import pandas as pd
import silva_solis as S
from common import *

HERE = pathlib.Path(__file__).resolve().parent
C_W_FIXED = 2.30e7  # m-3, held on the W side at every temperature (thesis Fig. 6)
L_W = 1e-6  # m, thickness of the tungsten slab
D_W_0, E_D_W = 4.99e-7, 0.23  # thesis Sec. 3.2
D_RESERVOIR = 1.0  # m2/s, keeps the slab uniform
SITES = [s for s in dict.fromkeys(S.GREEN + S.PINK + [24]) if s not in S.W_SITES]
SHOWN = [4, 63, 2, 54]  # the sites the thesis tabulates
T_START = {340.0: 1e-6, 430.0: 1e-9, 550.0: 1e-12}


def run(T, final_time, reservoir=True):
    nu = S.frequencies(T, corrected=True)
    tungsten = F.VolumeSubdomain1D(
        id=1, borders=[0.0, L_W], material=F.Material(D_0=D_RESERVOIR, E_D=0.0) if reservoir
        else F.Material(D_0=D_W_0, E_D=E_D_W),
    )
    plane = F.VolumeSubdomain(
        id=2, dim=0, material=F.Material(D_0=1.0, E_D=0.0),
        locator=lambda x: np.isclose(x[0], L_W, rtol=0.0, atol=1e-15),
    )
    left = F.SurfaceSubdomain1D(id=3, x=0.0)
    c_w = F.Species("c_w", subdomains=[tungsten])
    site = {s: F.Species(f"c_{s}", subdomains=[plane]) for s in SITES}

    def blocking(c, s):  # the Cu-side sites are never blocked
        return 1.0 if s in S.CU_SITES else 1 - c / S.N_SITES

    sources, bcs = [], []
    for i, j, *_ in S.EDGES:
        if i in S.W_SITES:  # tungsten -> first interfacial site
            def f(cw, cj, i=i, j=j):
                return nu[(i, j)] * S.LAYER[i] * cw * blocking(cj, j) - nu[(j, i)] * cj

            pair = {"cw": c_w, "cj": site[j]}
            sources.append(F.ParticleSource(value=f, species=site[j], volume=plane,
                                            species_dependent_value=pair))
            bcs.append(F.ParticleFluxBC(subdomain=plane, species=c_w,
                                        value=lambda cw, cj, f=f: -f(cw, cj),
                                        species_dependent_value=pair))
            continue

        def f(ci, cj, i=i, j=j):
            return nu[(i, j)] * ci * blocking(cj, j) - nu[(j, i)] * cj * blocking(ci, i)

        pair = {"ci": site[i], "cj": site[j]}
        sources.append(F.ParticleSource(value=f, species=site[j], volume=plane,
                                        species_dependent_value=pair))
        sources.append(F.ParticleSource(value=lambda ci, cj, f=f: -f(ci, cj),
                                        species=site[i], volume=plane,
                                        species_dependent_value=pair))

    settings = F.Settings(atol=1e-8, rtol=1e-10, transient=True, final_time=final_time)
    settings.stepsize = F.Stepsize(
        initial_value=T_START[T], growth_factor=1.12, cutback_factor=0.5,
        target_nb_iterations=100, max_stepsize=lambda t: max(t / 15, T_START[T]),
    )
    model = F.HydrogenTransportProblemDiscontinuous(
        mesh=F.Mesh1D(np.linspace(0.0, L_W, 21)),
        species=[c_w, *site.values()],
        subdomains=[tungsten, plane, left],
        sources=sources,
        boundary_conditions=[*bcs, F.FixedConcentrationBC(subdomain=left, value=C_W_FIXED, species=c_w)],
        initial_conditions=[F.InitialConcentration(value=C_W_FIXED, species=c_w, volume=tungsten)],
        temperature=T,
        settings=settings,
        exports=[F.TotalVolume(field=site[s], volume=plane) for s in SITES],
    )
    model.show_progress_bar = False
    model.initialise()
    model.run()
    out = {"t": np.array(model.exports[0].t)}
    for s, export in zip(SITES, model.exports):
        scale = 1 / S.LAYER[s] if s in S.CU_SITES else 1.0
        out[s] = np.array(export.data) * scale
    return pd.DataFrame(out)


def time_to_steady(df, threshold=0.01):
    """Thesis Eq. (6): the first time every site is within 1 % of its final value."""
    values = df[SITES].to_numpy()
    close = (np.abs(values[-1] - values) <= threshold * np.abs(values[-1])).all(axis=1)
    settled = np.flip(np.cumprod(np.flip(close))).astype(bool)
    return float(df.t[np.argmax(settled)])


def main():
    histories, summary = [], []
    for T in S.C_W:
        df = run(T, final_time=20 * S.TAU_S[T])
        tau = time_to_steady(df)
        histories.append(df.assign(T=T))
        row = {"T": T, "tau_s": tau, "tau_s_thesis": S.TAU_S[T]}
        row.update({f"c_{s}": df[s].iloc[-1] for s in SHOWN})
        summary.append(row)
        print({k: f"{v:.3g}" for k, v in row.items()}, flush=True)
    if 340.0 in S.C_W:
        print("thesis Table 5, 340 K:", S.TABLE_5)
    limited = run(340.0, final_time=1e4 * S.TAU_S[340.0], reservoir=False)
    limited.to_csv(HERE / "w_cu_network_diffusion_limited.csv", index=False)
    pd.concat(histories).to_csv(HERE / "w_cu_network.csv", index=False)
    pd.DataFrame(summary).to_csv(HERE / "w_cu_network_summary.csv", index=False)
    plot()


def plot():
    df = pd.read_csv(HERE / "w_cu_network.csv")
    summary = pd.read_csv(HERE / "w_cu_network_summary.csv")
    df.columns = [int(c) if c.isdigit() else c for c in df.columns]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(COL2, 2.5))
    sub = df[df["T"] == 340.0]
    limited = pd.read_csv(HERE / "w_cu_network_diffusion_limited.csv")
    labels = {4: "Oh-4 (interface)", 63: "Oh-63 (interface)", 2: "Oh-2 (Cu side)",
              54: "Oh-54 (Cu side)"}
    colours = {4: PALETTE[0], 63: "#3f8f7a", 2: PALETTE[2], 54: PALETTE[1]}
    for s in SHOWN:
        ax.loglog(sub.t, sub[s], color=colours[s], label=labels[s])
        ax.plot(limited.t.iloc[-1], S.TABLE_5[s], "o", ms=4, mfc="white", mec=colours[s],
                mew=0.9, clip_on=False, zorder=5)
    ax.plot([], [], "o", ms=4, mfc="white", mec="grey", mew=0.9, label="Silva-Solis, steady")
    ax.loglog(limited.t, limited["4"], color=colours[4], ls="--", lw=1.0,
              label=r"Oh-4, fed through 1 $\mu$m of W")
    ax.axvline(S.TAU_S[340.0], color="grey", lw=0.6, ls=":")
    ax.set_xlim(1e-4, limited.t.iloc[-1])
    ax.set_ylim(1e2, 1e22)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Concentration (m$^{-2}$ | m$^{-3}$)")
    ax.legend(loc="upper left", ncol=2, columnspacing=0.8, handlelength=1.6)
    ax.set_title("(a)  340 K", loc="left")

    inv_T = 1000 / summary["T"]
    ax2.semilogy(inv_T, 1 / summary.tau_s, "o-", ms=4, color=PALETTE[0], label="this work")
    ax2.semilogy(inv_T, 1 / summary.tau_s_thesis, "s", ms=4, mfc="white", mec=PALETTE[2],
                 label="Silva-Solis")
    x = np.linspace(inv_T.min(), inv_T.max(), 50)
    ax2.semilogy(x, 7.84e12 * np.exp(-1.01 / (S.K_B * 1000 / x)), color=PALETTE[2], lw=0.8,
                 ls="--", label="Silva-Solis, Arrhenius fit")
    ax2.set_xlabel(r"$1000/T$ (K$^{-1}$)")
    ax2.set_ylabel(r"Characteristic frequency $1/\tau_\mathrm{s}$ (s$^{-1}$)")
    ax2.legend()
    ax2.set_title("(b)", loc="left")
    fig.tight_layout()
    savefig(fig, __file__, "w_cu_network")


if __name__ == "__main__":
    plot() if "--plot" in sys.argv else main()
