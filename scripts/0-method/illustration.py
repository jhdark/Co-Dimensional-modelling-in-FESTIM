"""Illustration for Sec. 3: a fast-diffusing line embedded in a 2D bulk.

Dimensionless and illustrative only: no number here is physical.

A unit square bulk with diffusivity ``D`` is loaded on its left edge (c = 1) and
emptied on its right edge (c = 0). A manifold runs from the left edge to x = L_G along
y = 0.5. It carries its own concentration ``c_G`` with diffusivity ``D_G >> D`` and
exchanges with the bulk on both of its sides through ``J = k (c - c_G)``. The same
problem without the manifold is the 1D ramp ``c = 1 - x``.

Writes ``illustration.pdf``.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import dolfinx
import festim as F
import matplotlib.tri as mtri
from common import *
from matplotlib.collections import LineCollection
from mpi4py import MPI

D, D_G, K_EX, L_G = 1.0, 200.0, 20.0, 0.6
N = 80


def run():
    mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, N, N)
    bulk = F.VolumeSubdomain(
        id=1,
        material=F.Material(D_0=D, E_D=0.0),
        locator=lambda x: np.full_like(x[0], True, dtype=bool),
    )
    gamma = F.VolumeSubdomain(
        id=2,
        material=F.Material(D_0=D_G, E_D=0.0),
        dim=1,
        locator=lambda x: np.isclose(x[1], 0.5) & (x[0] <= L_G + 1e-12),
    )
    left = F.SurfaceSubdomain(id=3, locator=lambda x: np.isclose(x[0], 0.0))
    right = F.SurfaceSubdomain(id=4, locator=lambda x: np.isclose(x[0], 1.0))
    mouth = F.SurfaceSubdomain(id=5, dim=0, locator=lambda x: np.isclose(x[0], 0.0))

    c = F.Species("c", subdomains=[bulk])
    c_g = F.Species("c_g", subdomains=[gamma])
    both = {"cb": c, "cg": c_g}

    model = F.HydrogenTransportProblemDiscontinuous(
        mesh=F.Mesh(mesh),
        species=[c, c_g],
        subdomains=[bulk, gamma, left, right, mouth],
        sources=[
            F.ParticleSource(
                value=lambda cg, cb: 2 * K_EX * (cb - cg),  # two faces
                species=c_g,
                volume=gamma,
                species_dependent_value=both,
            )
        ],
        boundary_conditions=[
            F.ParticleFluxBC(
                subdomain=gamma,
                value=lambda cg, cb: K_EX * (cg - cb),
                species=c,
                species_dependent_value=both,
            ),
            F.FixedConcentrationBC(subdomain=left, value=1.0, species=c),
            F.FixedConcentrationBC(subdomain=right, value=0.0, species=c),
            F.FixedConcentrationBC(subdomain=mouth, value=1.0, species=c_g),
        ],
        temperature=500,
        settings=F.Settings(atol=1e-12, rtol=1e-12, transient=False),
        exports=[
            F.SurfaceFlux(field=c, surface=right),
            F.SurfaceFlux(field=c, surface=left),
        ],
    )
    model.show_progress_bar = False
    model.initialise()
    model.run()
    print("flux out of the right edge:", model.exports[0].data[-1], "(no manifold: 1)")
    print("flux out of the left edge: ", model.exports[1].data[-1])
    return get(c, bulk), get(c_g, gamma)


def main():
    c, c_g = run()

    V = c.function_space
    xy = V.tabulate_dof_coordinates()[:, :2]
    n_cells = V.mesh.topology.index_map(2).size_local
    tri = mtri.Triangulation(
        xy[:, 0], xy[:, 1], np.array([V.dofmap.cell_dofs(i) for i in range(n_cells)])
    )

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(COL2, 2.6), gridspec_kw={"width_ratios": [1.0, 1.15]}
    )
    levels = np.linspace(0, 1, 11)
    cf = ax.tricontourf(tri, c.x.array, levels=levels, cmap=cmap)
    ax.tricontour(tri, c.x.array, levels=levels[1:-1], colors="white", linewidths=0.4)
    segments, values = manifold_segments(c_g)
    lc = LineCollection(
        segments, array=values, cmap=cmap, norm=cf.norm, lw=3.0, capstyle="butt"
    )
    ax.add_collection(
        LineCollection(segments, colors="white", lw=4.6, capstyle="butt")
    )
    ax.add_collection(lc)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    ax.annotate(
        r"manifold $\Gamma$", (0.3, 0.52), (0.3, 0.8), ha="center", fontsize=7,
        arrowprops={"arrowstyle": "-", "lw": 0.6},
    )
    ax.text(0.8, 0.12, r"bulk $\Omega$", ha="center", fontsize=7)
    fig.colorbar(cf, ax=ax, label="Concentration", ticks=[0, 0.5, 1], shrink=0.9)
    ax.set_title("(a)", loc="left")

    # profiles along y = 0.5
    on_line = np.isclose(xy[:, 1], 0.5)
    order = np.argsort(xy[on_line, 0])
    xg, cg = sorted_line(c_g)
    ax2.plot(xg[:, 0], cg, color=PALETTE[2], label=r"manifold, $c_\Gamma$")
    ax2.plot(
        xy[on_line, 0][order], c.x.array[on_line][order], color=PALETTE[0],
        label=r"bulk on $y=0.5$, $c$",
    )
    ax2.plot([0, 1], [1, 0], color="grey", lw=0.9, ls="--", label="bulk, no manifold")
    ax2.axvline(L_G, color="grey", lw=0.5, ls=":")
    ax2.set_xlabel(r"$x$")
    ax2.set_ylabel("Concentration")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1.05)
    ax2.legend(loc="lower left")
    ax2.set_title("(b)", loc="left")
    fig.tight_layout()
    savefig(fig, __file__, "illustration")


if __name__ == "__main__":
    main()
