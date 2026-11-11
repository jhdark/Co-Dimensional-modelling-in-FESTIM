"""Application 3 results: short-circuit transport in a 2D Voronoi polycrystal.

The face x = 0 is loaded at t = 0 and the flux leaving x = 1 is recorded, with fast
grain boundaries (``D_GB``) and with boundaries no faster than the lattice (``D_REF``).
A snapshot of the microstructure at ``T_SNAP`` shows the network filling ahead of the
grains.

Writes ``breakthrough.csv``, ``snapshot_*.npz`` and ``polycrystal.pdf``.
Run with ``--plot`` to redraw from those files without solving.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import festim as F
import matplotlib.tri as mtri
import pandas as pd
from common import *
from matplotlib.collections import LineCollection
from model import build, exit_flux

HERE = pathlib.Path(__file__).resolve().parent
CASES = {
    2: {"n_grains": 30, "seed": 0, "h_gb": 0.015, "h_bulk": 0.04},
}
D_GB, D_REF = 1e3, 1.0
K_T, K_D = 1e2, 1e4  # segregation length k_t / k_d = 0.01 L
FINAL_TIME, T_SNAP = 0.6, 1e-3


def stepsize(final_time):
    return F.Stepsize(
        initial_value=1e-6, growth_factor=1.15, cutback_factor=0.5,
        target_nb_iterations=4, max_stepsize=final_time / 40,
    )


def run(dim, d_gb, final_time):
    model, grains, network, species, sigma, info = build(
        dim=dim, d_gb=d_gb, k_t=K_T, k_d=K_D, final_time=final_time, **CASES[dim]
    )
    model.settings.stepsize = stepsize(final_time)
    model.initialise()
    model.run()
    return model, grains, network, species, sigma, info


def cells(function):
    V = function.function_space
    tdim = V.mesh.topology.dim
    n = V.mesh.topology.index_map(tdim).size_local
    return V.tabulate_dof_coordinates(), np.array([V.dofmap.cell_dofs(i) for i in range(n)])


def main():
    rows = []
    for dim in CASES:
        for label, d_gb in (("fast", D_GB), ("reference", D_REF)):
            model, *_, info = run(dim, d_gb, FINAL_TIME)
            t, lattice, boundary = exit_flux(model, info)
            rows.append(pd.DataFrame({"dim": dim, "case": label, "t": t,
                                      "lattice": lattice, "network": boundary}))
            print(dim, label, "final flux", lattice[-1] + boundary[-1],
                  "GB measure", info["gb_measure"], flush=True)
        # snapshot with fast boundaries
        model, grains, network, species, sigma, info = run(dim, D_GB, T_SNAP)
        x_n, c_n = cells(get(sigma, network))
        snap = {"network_x": x_n, "network_cells": c_n,
                "network_values": get(sigma, network).x.array / (K_T / K_D)}
        if dim == 2:
            for spe, grain in zip(species, grains):
                x_g, c_g = cells(get(spe, grain))
                snap[f"grain_{grain.id}_x"] = x_g
                snap[f"grain_{grain.id}_cells"] = c_g
                snap[f"grain_{grain.id}_values"] = get(spe, grain).x.array
        np.savez_compressed(HERE / f"snapshot_{dim}d.npz", **snap)
    pd.concat(rows).to_csv(HERE / "breakthrough.csv", index=False)
    plot()


def plot():
    df = pd.read_csv(HERE / "breakthrough.csv")
    s2 = np.load(HERE / "snapshot_2d.npz")
    levels = np.linspace(0, 1, 11)
    norm = plt.Normalize(0, 1)

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(COL2, 2.7), gridspec_kw={"width_ratios": [1.0, 1.15]}
    )
    n_grains = sum(k.endswith("_values") and k.startswith("grain") for k in s2.files)
    for g in range(1, n_grains + 1):
        x = s2[f"grain_{g}_x"]
        tri = mtri.Triangulation(x[:, 0], x[:, 1], s2[f"grain_{g}_cells"])
        ax.tricontourf(tri, np.clip(s2[f"grain_{g}_values"], 0, 1), levels=levels, cmap=cmap)
    segments = s2["network_x"][s2["network_cells"]][:, :, :2]
    values = s2["network_values"][s2["network_cells"]].mean(axis=1)
    ax.add_collection(LineCollection(segments, colors="white", lw=2.2))
    ax.add_collection(LineCollection(segments, array=values, cmap=cmap, norm=norm, lw=1.3))
    ax.set_aspect("equal")
    ax.set_xlim(0, 1), ax.set_ylim(0, 1)
    ax.set_xticks([0, 0.5, 1]), ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel(r"$x/L$"), ax.set_ylabel(r"$y/L$")
    ax.set_title("(a)", loc="left")

    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, shrink=0.9,
                 ticks=[0, 0.5, 1], label="Concentration / loaded-face value")

    df = df[df.dim == 2]
    for part, colour, label in (("network", PALETTE[2], "through the network"),
                                ("lattice", PALETTE[0], "through the grains")):
        sub = df[df.case == "fast"]
        ax2.loglog(sub.t, sub[part], color=colour, label=label)
    sub = df[df.case == "reference"]
    ax2.loglog(sub.t, sub.lattice + sub.network, color="grey", ls="--",
               label=r"total, $D_\mathrm{gb} = D$")
    ax2.set_xlim(1e-5, FINAL_TIME)
    ax2.set_ylim(1e-3, 1e2)
    ax2.set_xlabel(r"Time $tD/L^2$")
    ax2.set_ylabel(r"Exit flux $JL/(Dc_0)$")
    ax2.legend(loc="lower left", bbox_to_anchor=(0.2, 0.02))
    ax2.set_title("(b)", loc="left")
    fig.tight_layout()
    savefig(fig, __file__, "polycrystal")


if __name__ == "__main__":
    plot() if "--plot" in sys.argv else main()
