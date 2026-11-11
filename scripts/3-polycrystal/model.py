"""Application 3: grain-boundary transport in a 2D Voronoi polycrystal.

The paper shows 2D only; ``dim=3`` also runs (a surface network in a tet mesh).

DIMENSIONLESS. Lengths are in units of the sample thickness L, lattice concentrations
in units of the value held on the loaded face, time in units of L**2 / D with D the
lattice diffusivity. No grain-boundary property here is taken from a source.

Every grain is its own volume subdomain with its own species; the whole boundary
network is ONE manifold adjacent to all of them, carrying one field. The boundaries
have no thickness: the network field ``sigma`` is a density per unit boundary area
(per unit length in 2D) and obeys a transport equation of its own, one dimension lower
than the grains::

    d sigma/dt = D_gb lap_Gamma(sigma) + sum over the two faces of J
    J = k_t c - k_d sigma            per grain face

``k_t`` is a trapping velocity and ``k_d`` a detrapping rate, so the exchange flux
enters the network equation with no conversion factor. At equilibrium
``sigma = (k_t / k_d) c``; the ratio is a segregation length. Hydrogen passes from one
grain to the next only through the boundary between them.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import festim as F
from common import *
from voronoi import GB_ID, LEFT_ID, RIGHT_ID, polycrystal

GB_IN_ID, GB_OUT_ID = 40001, 40002


def build(
    dim=2, n_grains=30, seed=0, h_gb=0.015, h_bulk=0.04,
    d_gb=1e3, k_t=1e2, k_d=1e4, final_time=0.3, n_steps=150,
):
    mesh, ct, ft, gb_measure = polycrystal(dim, n_grains, seed, h_gb, h_bulk)
    lattice = F.Material(D_0=1.0, E_D=0.0)
    grains = [F.VolumeSubdomain(id=i + 1, material=lattice) for i in range(n_grains)]
    network = F.VolumeSubdomain(
        id=GB_ID, material=F.Material(D_0=d_gb, E_D=0.0), dim=dim - 1
    )
    # the ends (2D) or edges (3D) of the network on the loaded and exit faces
    gb_in = F.SurfaceSubdomain(
        id=GB_IN_ID, dim=dim - 2, locator=lambda x: np.isclose(x[0], 0.0)
    )
    gb_out = F.SurfaceSubdomain(
        id=GB_OUT_ID, dim=dim - 2, locator=lambda x: np.isclose(x[0], 1.0)
    )
    # the loaded and exit faces, one surface per grain touching them
    tags = np.unique(ft.values)
    left = {int(t) - LEFT_ID: F.SurfaceSubdomain(id=int(t)) for t in tags if LEFT_ID < t < RIGHT_ID}
    right = {int(t) - RIGHT_ID: F.SurfaceSubdomain(id=int(t)) for t in tags if t > RIGHT_ID}

    species = [F.Species(f"c_{g.id}", subdomains=[g]) for g in grains]
    sigma = F.Species("sigma", subdomains=[network])

    sources, bcs = [], []
    for spe in species:
        pair = {"c": spe, "s": sigma}
        sources.append(
            F.ParticleSource(
                value=lambda c, s: k_t * c - k_d * s,
                species=sigma, volume=network, species_dependent_value=pair,
            )
        )
        bcs.append(
            F.ParticleFluxBC(
                subdomain=network, species=spe,
                value=lambda c, s: -(k_t * c - k_d * s), species_dependent_value=pair,
            )
        )
    bcs += [
        F.FixedConcentrationBC(subdomain=surf, value=1.0, species=species[g - 1])
        for g, surf in left.items()
    ]
    bcs += [
        F.FixedConcentrationBC(subdomain=surf, value=0.0, species=species[g - 1])
        for g, surf in right.items()
    ]
    bcs += [
        F.FixedConcentrationBC(subdomain=gb_in, value=k_t / k_d, species=sigma),
        F.FixedConcentrationBC(subdomain=gb_out, value=0.0, species=sigma),
    ]

    settings = F.Settings(atol=1e-10, rtol=1e-10, transient=True, final_time=final_time)
    settings.stepsize = F.Stepsize(initial_value=final_time / n_steps)
    model = F.HydrogenTransportProblemDiscontinuous(
        mesh=F.Mesh(mesh),
        species=[*species, sigma],
        subdomains=[*grains, network, *left.values(), *right.values(), gb_in, gb_out],
        sources=sources,
        boundary_conditions=bcs,
        temperature=500,
        settings=settings,
        exports=[F.SurfaceFlux(field=species[g - 1], surface=surf) for g, surf in right.items()]
        + [F.SurfaceFlux(field=sigma, surface=gb_out)],
    )
    model.volume_meshtags = ct
    model.facet_meshtags = ft
    model.show_progress_bar = False
    info = {"gb_measure": gb_measure, "n_exit": len(right), "dim": dim}
    return model, grains, network, species, sigma, info


def exit_flux(model, info):
    """Time, and the flux through x = 1 carried by the lattice and by the network."""
    n = info["n_exit"]
    t = np.array(model.exports[0].t)
    lattice = np.abs(sum(np.array(e.data) for e in model.exports[:n]))
    boundary = np.abs(np.array(model.exports[n].data))
    return t, lattice, boundary


if __name__ == "__main__":
    import time

    for dim, kwargs in (
        (2, {"n_grains": 30}),
        (3, {"n_grains": 12, "h_gb": 0.07, "h_bulk": 0.12}),
    ):
        t0 = time.time()
        model, grains, network, species, sigma, info = build(dim=dim, n_steps=20, **kwargs)
        model.initialise()
        t1 = time.time()
        model.run()
        t, lattice, boundary = exit_flux(model, info)
        print(f"{dim}D: initialise {t1 - t0:.1f} s, 20 steps {time.time() - t1:.1f} s, "
              f"lattice flux {lattice[-1]:.4g}, network flux {boundary[-1]:.4g}, "
              f"sigma max {get(sigma, network).x.array.max():.4g}", flush=True)
