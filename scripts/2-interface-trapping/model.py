"""Application 2: a W/Cu bilayer whose interface is a manifold with its own inventory.

1D, so the manifold is a point (``dim=0``)::

    c = C_SURFACE | W, L_W | interface, c_I (m-2) | Cu, L_CU | c = 0

The interface holds an areal density ``c_I`` on ``N_SITES`` sites, with coverage
``theta = c_I / N_SITES``, and exchanges with each side through its own jumps::

    J_W  = nu_wi lambda_W  c_W  (1 - theta) - nu_iw  c_I     (W -> interface)
    J_Cu = nu_ic c_I - nu_ci lambda_Cu c_Cu (1 - theta)      (interface -> Cu)
    d c_I / dt = J_W - J_Cu

``kind="equilibrium"`` replaces the manifold by the algebraic condition
``c_Cu / c_W = partition(T)``, the dilute steady state of the same kinetics with no
stored inventory, imposed with ``festim.Interface``.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import festim as F
import parameters as P
from common import *

W_ID, CU_ID, INTERFACE_ID, LEFT_ID, RIGHT_ID = 1, 2, 3, 4, 5


def vertices(l_w, l_cu, n=200):
    """Graded towards the loaded surface and both sides of the interface."""
    s = np.linspace(0, 1, n + 1)
    graded = 0.5 * (1 - np.cos(np.pi * s))  # clusters at both ends
    return np.concatenate([l_w * graded, l_w + l_cu * graded[1:]])


def build(
    T, kind="manifold", c_surface=P.C_SURFACE, final_time=None, scale=1.0, first_step=None
):
    """``scale`` multiplies both layer thicknesses, keeping the geometry similar."""
    L_W, L_CU = scale * P.L_W, scale * P.L_CU
    first_step = final_time * 1e-7 if first_step is None else first_step
    r = P.rates(T)
    mesh = F.Mesh1D(vertices(L_W, L_CU))
    left = F.SurfaceSubdomain1D(id=LEFT_ID, x=0.0)
    right = F.SurfaceSubdomain1D(id=RIGHT_ID, x=L_W + L_CU)
    settings = F.Settings(atol=1e4, rtol=1e-10, transient=True, final_time=final_time)
    settings.stepsize = F.Stepsize(
        initial_value=first_step, growth_factor=1.1, cutback_factor=0.5,
        target_nb_iterations=6, max_stepsize=lambda t: max(t / 20, first_step),
    )

    if kind == "manifold":
        tungsten = F.VolumeSubdomain1D(
            id=W_ID, borders=[0.0, L_W], material=F.Material(D_0=P.D_W_0, E_D=P.E_D_W)
        )
        copper = F.VolumeSubdomain1D(
            id=CU_ID, borders=[L_W, L_W + L_CU],
            material=F.Material(D_0=P.D_CU_0, E_D=P.E_D_CU),
        )
        interface = F.VolumeSubdomain(
            id=INTERFACE_ID, dim=0, material=F.Material(D_0=P.D_INT_0, E_D=P.E_D_INT),
            # explicit tolerance: the graded cells here are smaller than the default one
            locator=lambda x: np.isclose(x[0], L_W, rtol=0.0, atol=1e-6 * L_W / 200**2),
        )
        c_w = F.Species("c_w", subdomains=[tungsten])
        c_cu = F.Species("c_cu", subdomains=[copper])
        c_i = F.Species("c_i", subdomains=[interface])

        def J_w(cb, ci):  # W -> interface
            return r["w_to_i"] * P.LAMBDA_W * cb * (1 - ci / P.N_SITES) - r["i_to_w"] * ci

        def J_cu(cb, ci):  # Cu -> interface
            return r["cu_to_i"] * P.LAMBDA_CU * cb * (1 - ci / P.N_SITES) - r["i_to_cu"] * ci

        sources, bcs = [], []
        for bulk_species, J in ((c_w, J_w), (c_cu, J_cu)):
            pair = {"cb": bulk_species, "ci": c_i}
            sources.append(
                F.ParticleSource(
                    value=J, species=c_i, volume=interface, species_dependent_value=pair
                )
            )
            bcs.append(
                F.ParticleFluxBC(
                    subdomain=interface, species=bulk_species,
                    value=lambda cb, ci, J=J: -J(cb, ci), species_dependent_value=pair,
                )
            )
        bcs += [
            F.FixedConcentrationBC(subdomain=left, value=c_surface, species=c_w),
            F.FixedConcentrationBC(subdomain=right, value=0.0, species=c_cu),
        ]
        model = F.HydrogenTransportProblemDiscontinuous(
            mesh=mesh,
            species=[c_w, c_cu, c_i],
            subdomains=[tungsten, copper, interface, left, right],
            sources=sources,
            boundary_conditions=bcs,
            temperature=T,
            settings=settings,
            exports=[
                F.SurfaceFlux(field=c_cu, surface=right),
                F.TotalVolume(field=c_i, volume=interface),
                F.TotalVolume(field=c_w, volume=tungsten),
                F.TotalVolume(field=c_cu, volume=copper),
            ],
        )
    elif kind == "equilibrium":
        # c_W / K_W = c_Cu / K_Cu with K_Cu / K_W = partition(T)
        tungsten = F.VolumeSubdomain1D(
            id=W_ID, borders=[0.0, L_W],
            material=F.Material(D_0=P.D_W_0, E_D=P.E_D_W, K_S_0=1.0, E_K_S=0.0),
        )
        copper = F.VolumeSubdomain1D(
            id=CU_ID, borders=[L_W, L_W + L_CU],
            material=F.Material(
                D_0=P.D_CU_0, E_D=P.E_D_CU, K_S_0=P.partition(T), E_K_S=0.0
            ),
        )
        H = F.Species("H", subdomains=[tungsten, copper])
        model = F.HydrogenTransportProblemDiscontinuous(
            mesh=mesh,
            species=[H],
            subdomains=[tungsten, copper, left, right],
            interfaces=[
                F.Interface(id=INTERFACE_ID, subdomains=[tungsten, copper], penalty_term=1e3)
            ],
            boundary_conditions=[
                F.FixedConcentrationBC(subdomain=left, value=c_surface, species=H),
                F.FixedConcentrationBC(subdomain=right, value=0.0, species=H),
            ],
            temperature=T,
            settings=settings,
            exports=[
                F.SurfaceFlux(field=H, surface=right),
                F.TotalVolume(field=H, volume=tungsten),
                F.TotalVolume(field=H, volume=copper),
            ],
        )
    else:
        raise ValueError(kind)
    model.show_progress_bar = False
    return model


def run(T, kind, final_time, **kwargs):
    model = build(T, kind, final_time=final_time, **kwargs)
    model.initialise()
    model.run()
    e = model.exports
    out = {"t": np.array(e[0].t), "flux": np.abs(np.array(e[0].data))}
    if kind == "manifold":
        out["interface"] = np.array(e[1].data)
        out["tungsten"], out["copper"] = np.array(e[2].data), np.array(e[3].data)
    else:
        out["tungsten"], out["copper"] = np.array(e[1].data), np.array(e[2].data)
    return out


def steady_flux(T, c_surface=P.C_SURFACE, scale=1.0):
    """Steady permeation flux with the algebraic condition, two resistances in series."""
    D_w = P.D_W_0 * np.exp(-P.E_D_W / (P.K_B * T))
    D_cu = P.D_CU_0 * np.exp(-P.E_D_CU / (P.K_B * T))
    return c_surface / scale / (P.L_W / D_w + P.L_CU / (D_cu * P.partition(T)))


if __name__ == "__main__":
    T = 430.0
    t_end = 2e6
    for kind in ("equilibrium", "manifold"):
        out = run(T, kind, t_end)
        print(kind, "steps", len(out["t"]), "final flux", out["flux"][-1],
              "analytical", steady_flux(T))
        if kind == "manifold":
            print("  interface inventory", out["interface"][-1], "coverage",
                  out["interface"][-1] / P.N_SITES, " W lattice", out["tungsten"][-1])
