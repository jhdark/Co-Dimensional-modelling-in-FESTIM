"""Shared plotting style and small helpers for every script in this directory.

Import it from a script one directory down with::

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from common import *
"""

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt
import morethemes as mt
import numpy as np

__all__ = [
    "PALETTE",
    "COL1",
    "COL2",
    "cmap",
    "get",
    "manifold_segments",
    "np",
    "plt",
    "savefig",
    "sorted_line",
]

PALETTE = ["#1a4848", "#f7b000", "#f46036", "#c9f2c7", "#aceca1"]

# elsarticle 5p: column 3.35 in, full width 7.0 in
COL1 = 3.35
COL2 = 7.0

mt.set_theme("urban")
mpl.rcParams.update(
    {
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "lines.linewidth": 1.4,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.grid": False,
        "savefig.dpi": 300,
        "figure.dpi": 150,
        "mathtext.fontset": "dejavusans",
    }
)

# sequential map built from the palette: dark teal (high) to pale green (low)
cmap = mpl.colors.LinearSegmentedColormap.from_list(
    "codim", ["#f4fbf3", "#aceca1", "#3f8f7a", "#1a4848"]
)


def savefig(fig, script_file, name):
    """Write ``name``.pdf next to the script that made it."""
    out = pathlib.Path(script_file).resolve().parent / f"{name}.pdf"
    fig.savefig(out, bbox_inches="tight")
    print(f"wrote {out}")
    return out


def get(species, subdomain):
    """The post-processing solution of ``species`` on ``subdomain``."""
    return species.subdomain_to_post_processing_solution[subdomain]


def sorted_line(function, axis=0):
    """Dof coordinates and values of a P1 function on a line, sorted along ``axis``."""
    x = function.function_space.tabulate_dof_coordinates()
    order = np.argsort(x[:, axis])
    return x[order], function.x.array[order]


def manifold_segments(function):
    """Segments and their mean value, for a P1 function on a 1D manifold in 2D.

    Returns ``(segments, values)`` ready for a ``LineCollection``, which is the only
    way to draw a branched network: its dofs have no single ordering.
    """
    V = function.function_space
    mesh = V.mesh
    x = V.tabulate_dof_coordinates()[:, :2]
    n_cells = mesh.topology.index_map(mesh.topology.dim).size_local
    dofs = np.array([V.dofmap.cell_dofs(c) for c in range(n_cells)])
    return x[dofs], function.x.array[dofs].mean(axis=1)
