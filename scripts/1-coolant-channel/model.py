"""Application 1: a 1D plug-flow liquid on a manifold, coupled to an axisymmetric wall.

A permeator tube: tritium dissolved in a flowing liquid permeates through the tube wall
into vacuum. Geometry (cylindrical, first coordinate is the radius)::

    r = r_o  ----------------------------------  c_wall = 0 (vacuum)
             |           tube wall            |
    r = r_i  ==================================  manifold: the liquid, c_f(z)
             z = 0 (inlet, c_f = c_in)     z = L (outflow)

The liquid is not meshed. Its cross-section averaged concentration ``c_f`` lives on
the inner surface of the wall and obeys the plug-flow balance::

    d c_f/dt + d(u c_f)/dz - D_l d2 c_f/dz2 = -(2 / r_i) J

with ``J`` the flux from the liquid into the wall per unit inner area and ``2 / r_i``
the wetted perimeter over the flow area. ``J`` crosses a film of mass-transfer
coefficient ``k_t`` between the bulk liquid and the liquid at the wall, which is in
equilibrium with the metal surface::

    J = k_t (c_f - c_wl)
    c_wl = c_wall K_l / K_s             Sieverts liquid (Pb-17Li)
    c_wl = K_h (c_wall / K_s)**2        Henry liquid (FLiBe)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import dolfinx
import festim as F
from common import *
from mpi4py import MPI

WALL_ID, LIQUID_ID, OUTER_ID, INLET_ID, OUTLET_ID = 1, 2, 3, 4, 5


def build(case, n_z=400, n_r=4, transient=False, final_time=None, n_steps=200):
    mesh = dolfinx.mesh.create_rectangle(
        MPI.COMM_WORLD,
        [np.array([case.r_i, 0.0]), np.array([case.r_o, case.length])],
        [n_r, n_z],
    )
    wall = F.VolumeSubdomain(
        id=WALL_ID,
        material=F.Material(D_0=case.D_solid, E_D=0.0),
        locator=lambda x: np.full_like(x[0], True, dtype=bool),
    )
    liquid = F.VolumeSubdomain(
        id=LIQUID_ID,
        material=F.Material(D_0=case.D_liquid, E_D=0.0),
        dim=1,
        locator=lambda x: np.isclose(x[0], case.r_i, rtol=0.0, atol=1e-9),
    )
    outer = F.SurfaceSubdomain(
        id=OUTER_ID, locator=lambda x: np.isclose(x[0], case.r_o, rtol=0.0, atol=1e-9)
    )
    inlet = F.SurfaceSubdomain(id=INLET_ID, dim=0, locator=lambda x: np.isclose(x[1], 0))
    outlet = F.SurfaceSubdomain(
        id=OUTLET_ID, dim=0, locator=lambda x: np.isclose(x[1], case.length)
    )

    c_wall = F.Species("c_wall", subdomains=[wall])
    c_f = F.Species("c_f", subdomains=[liquid])
    both = {"cw": c_wall, "cf": c_f}

    def J(cw, cf):  # liquid -> wall, per unit inner area
        if case.law == "sieverts":
            c_wl = cw * case.K_liquid / case.K_solid
        else:
            c_wl = case.K_liquid * (cw / case.K_solid) ** 2
        return case.k_t * (cf - c_wl)

    velocity = dolfinx.fem.Function(dolfinx.fem.functionspace(mesh, ("Lagrange", 1, (2,))))
    velocity.interpolate(
        lambda x: np.vstack([np.zeros(x.shape[1]), np.full(x.shape[1], case.velocity)])
    )

    settings = F.Settings(atol=1e-12, rtol=1e-10, transient=transient, final_time=final_time)
    initial = []
    if transient:
        settings.stepsize = final_time / n_steps
        # the tube starts full of liquid at the inlet concentration, the wall empty
        initial = [F.InitialConcentration(value=case.c_in, species=c_f, volume=liquid)]

    model = F.HydrogenTransportProblemDiscontinuous(
        mesh=F.Mesh(mesh, coordinate_system="cylindrical"),
        species=[c_wall, c_f],
        subdomains=[wall, liquid, outer, inlet, outlet],
        sources=[
            F.ParticleSource(
                value=lambda cw, cf: -2 / case.r_i * J(cw, cf),
                species=c_f, volume=liquid, species_dependent_value=both,
            )
        ],
        boundary_conditions=[
            F.ParticleFluxBC(
                subdomain=liquid, value=J, species=c_wall, species_dependent_value=both
            ),
            F.FixedConcentrationBC(subdomain=outer, value=0.0, species=c_wall),
            F.FixedConcentrationBC(subdomain=inlet, value=case.c_in, species=c_f),
            F.OutflowBC(subdomain=outlet, species=c_f),
        ],
        initial_conditions=initial,
        drift_terms=[F.AdvectionTerm(velocity=velocity, subdomain=liquid, species=c_f)],
        temperature=case.T,
        settings=settings,
        exports=[F.AverageSurface(field=c_f, surface=outlet)] if transient else [],
    )
    model.show_progress_bar = False
    return model, (wall, liquid), (c_wall, c_f)


def steady(case, **kwargs):
    """z and the liquid concentration along the tube at steady state."""
    model, (wall, liquid), (c_wall, c_f) = build(case, **kwargs)
    model.initialise()
    model.run()
    x, cf = sorted_line(get(c_f, liquid), axis=1)
    return x[:, 1], cf
