"""Spatial convergence of the coupled bulk/manifold problem (Sec. 3, verification).

Method of manufactured solutions, the same solution as the FESTIM system test
``test/system_tests/test_codim1_coupling.py`` (tag v2.2), in material coordinates
``xi`` (``xi = x`` in 2D, the inverse rotation of ``x`` in the tilted 3D case)::

    c_b(xi) = 1 + xi_0**2 + (1 + xi_0) cos(pi xi_1)
    c_G(xi) = 1 + beta cos(pi xi_1),        beta = 1 - D_b / k
    J       = k (c_b - c_G) = D_b cos(pi xi_1)

The manifold is the face ``xi_0 = 0``. In 3D the unit cube is rotated so the manifold
is aligned with no coordinate axis, which exercises the tangential operator.

Writes ``convergence.csv`` and ``convergence.pdf``.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import dolfinx
import festim as F
import pandas as pd
import ufl
from common import *
from dolfinx import fem
from mpi4py import MPI

D_B, D_G, K_EX = 1.5, 0.7, 2.0
BETA = 1.0 - D_B / K_EX
HERE = pathlib.Path(__file__).resolve().parent


def rotation(alpha=0.6, gamma=0.4):
    ca, sa, cg, sg = np.cos(alpha), np.sin(alpha), np.cos(gamma), np.sin(gamma)
    Rz = np.array([[ca, -sa, 0.0], [sa, ca, 0.0], [0.0, 0.0, 1.0]])
    Ry = np.array([[cg, 0.0, sg], [0.0, 1.0, 0.0], [-sg, 0.0, cg]])
    return Ry @ Rz


def error_L2(u_h, u_exact, degree_raise=3):
    """Relative L2 error against a UFL expression, on a richer space."""
    V = u_h.function_space
    mesh = V.mesh
    W = fem.functionspace(mesh, ("Lagrange", V.ufl_element().degree + degree_raise))
    u_W = fem.Function(W)
    u_W.interpolate(u_h)
    u_ex = fem.Function(W)
    u_ex.interpolate(fem.Expression(u_exact, W.element.interpolation_points))
    e = fem.Function(W)
    e.x.array[:] = u_W.x.array - u_ex.x.array
    norm = lambda f: np.sqrt(
        mesh.comm.allreduce(
            fem.assemble_scalar(fem.form(ufl.inner(f, f) * ufl.dx)), op=MPI.SUM
        )
    )
    return norm(e) / norm(u_ex)


def run(n, dim):
    if dim == 2:
        mesh = dolfinx.mesh.create_unit_square(MPI.COMM_WORLD, n, n)
        R = np.eye(3)
    else:
        mesh = dolfinx.mesh.create_unit_cube(MPI.COMM_WORLD, n, n, n)
        R = rotation()
        mesh.geometry.x[:, :] = mesh.geometry.x @ R.T
    Rt = ufl.as_matrix(R.T[:dim, :dim].tolist())
    pi = np.pi

    def xi(x):
        return Rt * ufl.as_vector([x[i] for i in range(dim)])

    def material(x):
        return R.T[:dim, :dim] @ x[:dim]

    bulk = F.VolumeSubdomain(
        id=1,
        material=F.Material(D_0=D_B, E_D=0.0),
        locator=lambda x: np.full_like(x[0], True, dtype=bool),
    )
    gamma = F.VolumeSubdomain(
        id=2,
        material=F.Material(D_0=D_G, E_D=0.0),
        dim=dim - 1,
        locator=lambda x: np.isclose(material(x)[0], 0.0),
    )
    right = F.SurfaceSubdomain(id=3, locator=lambda x: np.isclose(material(x)[0], 1.0))
    c_b = F.Species("c_b", subdomains=[bulk])
    c_g = F.Species("c_g", subdomains=[gamma])
    both = {"cb": c_b, "cg": c_g}

    model = F.HydrogenTransportProblemDiscontinuous(
        mesh=F.Mesh(mesh),
        species=[c_b, c_g],
        subdomains=[bulk, gamma, right],
        sources=[
            F.ParticleSource(
                value=lambda x: (
                    -D_B * (2 - pi**2 * (1 + xi(x)[0]) * ufl.cos(pi * xi(x)[1]))
                ),
                species=c_b,
                volume=bulk,
            ),
            F.ParticleSource(
                value=lambda x: (D_G * pi**2 * BETA - D_B) * ufl.cos(pi * xi(x)[1]),
                species=c_g,
                volume=gamma,
            ),
            F.ParticleSource(
                value=lambda cg, cb: K_EX * (cb - cg),
                species=c_g,
                volume=gamma,
                species_dependent_value=both,
            ),
        ],
        boundary_conditions=[
            F.ParticleFluxBC(
                subdomain=gamma,
                value=lambda cg, cb: K_EX * (cg - cb),
                species=c_b,
                species_dependent_value=both,
            ),
            F.FixedConcentrationBC(
                subdomain=right,
                value=lambda x: (
                    1 + xi(x)[0] ** 2 + (1 + xi(x)[0]) * ufl.cos(pi * xi(x)[1])
                ),
                species=c_b,
            ),
        ],
        temperature=500,
        settings=F.Settings(atol=1e-12, rtol=1e-12, transient=False),
    )
    model.show_progress_bar = False
    model.initialise()
    model.run()

    X_b = Rt * ufl.SpatialCoordinate(bulk.submesh)
    X_g = Rt * ufl.SpatialCoordinate(gamma.submesh)
    return (
        error_L2(get(c_b, bulk), 1 + X_b[0] ** 2 + (1 + X_b[0]) * ufl.cos(pi * X_b[1])),
        error_L2(get(c_g, gamma), 1 + BETA * ufl.cos(pi * X_g[1])),
    )


def main():
    rows = []
    for dim, refinements in ((2, [8, 16, 32, 64, 128]), (3, [4, 8, 16, 32])):
        for n in refinements:
            e_b, e_g = run(n, dim)
            rows.append({"dim": dim, "n": n, "h": 1 / n, "bulk": e_b, "manifold": e_g})
            print(rows[-1])
    df = pd.DataFrame(rows)
    df.to_csv(HERE / "convergence.csv", index=False)
    plot(df)


def plot(df):
    fig, ax = plt.subplots(figsize=(COL1, 2.5))
    styles = {2: ("o", "-"), 3: ("s", "--")}
    for dim, sub in df.groupby("dim"):
        marker, ls = styles[dim]
        for field, colour in (("bulk", PALETTE[0]), ("manifold", PALETTE[2])):
            ax.loglog(
                sub.h, sub[field], marker=marker, ls=ls, color=colour, ms=4,
                label=f"{field}, {dim}D",
            )
            rate = np.polyfit(np.log(sub.h), np.log(sub[field]), 1)[0]
            print(f"{dim}D {field}: fitted order {rate:.2f}")
    h = np.array([df.h.min(), df.h.max()])
    ax.loglog(h, 0.02 * (h / h[1]) ** 2, color="grey", lw=0.8)
    ax.annotate(r"$h^2$", (h[0] * 1.6, 0.02 * (h[0] * 1.6 / h[1]) ** 2 * 0.35),
                color="grey", fontsize=7)
    ax.set_xlabel(r"Cell size $h$")
    ax.set_ylabel(r"Relative $L^2$ error")
    ax.legend(ncol=2, loc="lower right", handlelength=2.4, columnspacing=1.0)
    savefig(fig, __file__, "convergence")


if __name__ == "__main__":
    if "--plot" in sys.argv:
        plot(pd.read_csv(HERE / "convergence.csv"))
    else:
        main()
