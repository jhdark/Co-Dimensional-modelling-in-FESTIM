"""Voronoi polycrystals in 2D and 3D, meshed with gmsh, grain boundaries on mesh facets.

``polycrystal(dim, n_grains, seed, ...)`` returns a dolfinx mesh of the unit box with

- cell tags: one id per grain, 1 ... n_grains
- facet tags: ``GB_ID`` on every grain boundary; ``LEFT_ID + g`` / ``RIGHT_ID + g`` on
  the part of x = 0 / x = 1 that belongs to grain ``g``. A FESTIM surface subdomain must
  touch a single volume subdomain, hence one tag per grain.

The construction follows the Voronoi examples of the FESTIM-Microstructure package
(github.com/festim-dev/FESTIM-Microstructure): the box is fragmented along every
Voronoi ridge, the mesh is graded from ``h_gb`` on the boundaries to ``h_bulk`` inside
the grains, and each cell takes the grain of its nearest seed.
"""

import dolfinx
import gmsh
import numpy as np
from dolfinx.io import gmsh as gmshio
from mpi4py import MPI
from scipy.spatial import KDTree, Voronoi

GB_ID, LEFT_ID, RIGHT_ID = 10000, 20000, 30000


def mirror(points):
    """The seeds plus their mirror images in every face of the unit box."""
    out = [points]
    for axis in range(points.shape[1]):
        for wall in (0.0, 1.0):
            m = points.copy()
            m[:, axis] = 2 * wall - m[:, axis]
            out.append(m)
    return np.vstack(out)


def seeds(dim, n_grains, seed, lloyd=2):
    """Random seeds in the unit box, relaxed towards equal-sized grains."""
    points = np.random.default_rng(seed).random((n_grains, dim))
    for _ in range(lloyd):
        vor = Voronoi(mirror(points))
        points = np.array(
            [vor.vertices[vor.regions[vor.point_region[i]]].mean(axis=0)
             for i in range(n_grains)]
        )
    return np.clip(points, 0.02, 0.98)


def ridges(points):
    """The polygons (3D) or segments (2D) separating two grains of the box."""
    n = len(points)
    vor = Voronoi(mirror(points))
    out = []
    for (i, j), ridge in zip(vor.ridge_points, vor.ridge_vertices):
        if i >= n or j >= n or -1 in ridge:
            continue  # a mirror ridge lies on the box itself
        poly = np.clip(vor.vertices[ridge], 0.0, 1.0)
        if points.shape[1] == 3:  # order the ring around its normal
            normal = points[j] - points[i]
            centre = poly.mean(axis=0)
            e1 = np.cross(normal, [1.0, 0.3, 0.2])
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(normal, e1)
            angle = np.arctan2((poly - centre) @ e2, (poly - centre) @ e1)
            poly = poly[np.argsort(angle)]
        out.append(poly)
    return out


def measure(poly):
    """Length of a segment or area of a planar polygon."""
    if len(poly) == 2:
        return float(np.linalg.norm(poly[1] - poly[0]))
    v = poly - poly[0]
    return 0.5 * float(np.linalg.norm(np.cross(v[1:-1], v[2:]).sum(axis=0)))


def polycrystal(dim=2, n_grains=30, seed=0, h_gb=0.015, h_bulk=0.04):
    points = seeds(dim, n_grains, seed)
    boundaries = ridges(points)
    # drop slivers the mesher would have to resolve
    smallest = (h_gb / 4) if dim == 2 else (h_gb / 2) ** 2
    boundaries = [b for b in boundaries if measure(b) > smallest]

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("polycrystal")
    occ = gmsh.model.occ
    pad = lambda p: (*p, 0.0) if dim == 2 else tuple(p)
    if dim == 2:
        box = occ.addRectangle(0, 0, 0, 1, 1)
        tools = [
            (1, occ.addLine(occ.addPoint(*pad(a)), occ.addPoint(*pad(b))))
            for a, b in boundaries
        ]
    else:
        box = occ.addBox(0, 0, 0, 1, 1, 1)
        tools = []
        for poly in boundaries:
            pts = [occ.addPoint(*p) for p in poly]
            lines = [occ.addLine(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
            tools.append((2, occ.addPlaneSurface([occ.addCurveLoop(lines)])))
    out, out_map = occ.fragment([(dim, box)], tools)
    occ.synchronize()
    gb = sorted({t for entry in out_map[1:] for (d, t) in entry if d == dim - 1})
    gmsh.model.addPhysicalGroup(dim, [t for (d, t) in out if d == dim], 1)
    gmsh.model.addPhysicalGroup(dim - 1, gb, GB_ID)

    field = gmsh.model.mesh.field
    field.add("Distance", 1)
    field.setNumbers(1, "CurvesList" if dim == 2 else "SurfacesList", gb)
    field.setNumber(1, "Sampling", 30)
    field.add("Threshold", 2)
    field.setNumber(2, "InField", 1)
    field.setNumber(2, "SizeMin", h_gb)
    field.setNumber(2, "SizeMax", h_bulk)
    field.setNumber(2, "DistMin", 2 * h_gb)
    field.setNumber(2, "DistMax", 12 * h_gb)
    field.setAsBackgroundMesh(2)
    for opt in ("MeshSizeFromPoints", "MeshSizeFromCurvature", "MeshSizeExtendFromBoundary"):
        gmsh.option.setNumber(f"Mesh.{opt}", 0)
    gmsh.model.mesh.generate(dim)
    data = gmshio.model_to_mesh(gmsh.model, MPI.COMM_WORLD, 0, gdim=dim)
    gmsh.finalize()
    mesh = data.mesh

    # grains: every cell belongs to its nearest seed
    n_cells = mesh.topology.index_map(dim).size_local
    cells = np.arange(n_cells, dtype=np.int32)
    mid = dolfinx.mesh.compute_midpoints(mesh, dim, cells)[:, :dim]
    grain = (KDTree(points).query(mid)[1] + 1).astype(np.int32)
    cell_tags = dolfinx.mesh.meshtags(mesh, dim, cells, grain)

    # facets: the network from gmsh, the two faces split by grain. A facet tagged by
    # gmsh whose two cells share a grain is a ridge fragment outside the network.
    mesh.topology.create_connectivity(dim - 1, dim)
    f_to_c = mesh.topology.connectivity(dim - 1, dim)
    tags = {}
    for f in data.facet_tags.find(GB_ID):
        c = f_to_c.links(f)
        if len(c) == 2 and grain[c[0]] != grain[c[1]]:
            tags[int(f)] = GB_ID
    for base, wall in ((LEFT_ID, 0.0), (RIGHT_ID, 1.0)):
        for f in dolfinx.mesh.locate_entities_boundary(
            mesh, dim - 1, lambda x: np.isclose(x[0], wall)
        ):
            tags[int(f)] = base + grain[f_to_c.links(f)[0]]
    facets = np.array(sorted(tags), dtype=np.int32)
    facet_tags = dolfinx.mesh.meshtags(
        mesh, dim - 1, facets, np.array([tags[f] for f in facets], dtype=np.int32)
    )
    return mesh, cell_tags, facet_tags, sum(measure(b) for b in boundaries)


if __name__ == "__main__":
    import time

    for dim, n, hg, hb in ((2, 30, 0.015, 0.04), (3, 12, 0.07, 0.12)):
        t = time.time()
        mesh, ct, ft, size = polycrystal(dim, n, 0, hg, hb)
        print(f"{dim}D: cells {mesh.topology.index_map(dim).size_local}, grains "
              f"{len(np.unique(ct.values))}, GB facets {len(ft.find(GB_ID))}, GB measure "
              f"{size:.3f}, {time.time() - t:.1f} s", flush=True)
