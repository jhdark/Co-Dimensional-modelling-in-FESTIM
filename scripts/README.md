# Scripts

Simulation scripts backing the paper. Every figure in `main.tex` is written by a
script here, next to the CSV of the data it plots.

## Environment

```bash
conda env create -f environment.yml
conda activate codim-env
```

The recipe pins **FESTIM 2.2** from conda-forge, the first release carrying the
co-dimensional (manifold) subdomains this paper describes (git tag `v2.2`,
commit `5620e8f5`). No extra `pip install` of a FESTIM branch is needed.
`python-gmsh` meshes the Voronoi polycrystals. `pytest`, `sympy` and `scipy` let the
FESTIM codim system tests (`test/system_tests/test_codim1_*.py` at tag `v2.2`)
run in the same environment.

## Contents

Run each script from its own directory. Sweeps accept `--plot` to redraw the
figure from the committed CSV without solving.

| Directory | Paper section | Script | Writes | Run time |
|---|---|---|---|---|
| `0-method/` | Sec. 3 | `illustration.py` | `illustration.pdf` | seconds |
| `0-method/` | Sec. 3.4 | `convergence.py` | `convergence.csv`, `convergence.pdf` | 2 min |
| `1-coolant-channel/` | Sec. 4 | `benchmark.py` (uses `model.py`, `cases.py`) | `efficiency.csv`, `startup.csv`, `permeator.pdf` | 1 min |
| `2-interface-trapping/` | Sec. 5 | `be_beo.py` | `be_beo.csv`, `be_beo_error.csv`, `be_beo.pdf` | 1 min |
| `2-interface-trapping/` | Sec. 5 | `w_cu_network.py` (uses `silva_solis.py`) | `w_cu_network*.csv`, `w_cu_network.pdf` | 3 min |
| `2-interface-trapping/` | Sec. 5 | `sweep.py` (uses `model.py`, `parameters.py`) | `delay.csv`, `transients.csv`, `interface_trapping.pdf` | 20 min |
| `3-polycrystal/` | Sec. 6 | `results.py` (uses `model.py`, `voronoi.py`) | `breakthrough.csv`, `snapshot_2d.npz`, `polycrystal.pdf` | 3 min |

`common.py` holds the plotting style and small post-processing helpers shared
by all of them.

## Where the numbers come from

| Case | Source of parameters | Status |
|---|---|---|
| `0-method` | dimensionless | illustration and verification only |
| `1-coolant-channel` | Rader, Greenwood and Humrickhouse 2018, Tables I to III; analytical solution of Humrickhouse and Merrill 2015 | solubility units and the FLiBe inlet concentration are **inferred** (they recover the published regime number); neither paper is in `references.bib` yet |
| `2-interface-trapping/be_beo.py` | Hodille et al. 2022 (DOI 10.1088/1361-648X/ac8328): Eq. (6), Table 1 rate constants, n_i = 1e20 m-2, c_Be = 5e27 m-3; raw MD time series supplied by E. A. Hodille, one file per interface and temperature (`data/new_data/D_trapped_at_*_*K.csv`, received 2026-11-24); initial interface concentration from the first MD frame | rate parameters checked against the paper; the 1000 K files are shuffled in time below about 5 ns and hold 447 repeated rows (a post-processing fault on the sender's side); the script sorts by time and drops the repeats, see its docstring. The first delivery in `data/D_trapped_at_*.csv` is no longer read |
| `2-interface-trapping/w_cu_network.py` | Silva-Solis thesis (HAL tel-04750846), Ch. 5: Table 1 barriers, Wert-Zener frequencies, Table 3 corrections | reproduces the thesis; nothing nominal except the reservoir |
| `2-interface-trapping/sweep.py` | same thesis | the collapse of the path onto three states is **ours**; layer thicknesses and surface concentration are **nominal** |
| `3-polycrystal` | dimensionless | no grain-boundary property is sourced; microstructure-scale modelling proper is left to the FESTIM-Microstructure paper |

Each `parameters.py`, `cases.py` or script docstring says line by line what is taken from a source and what is
a nominal choice.

## Conventions

- Directory names are kebab-cased and numbered by the order they appear in the
  paper.
- Plotting goes through `common.py`: `morethemes` (`mt.set_theme("urban")`), the
  palette `#1a4848, #f7b000, #f46036, #c9f2c7, #aceca1`, white background, top
  and right spines removed. Figure widths are `COL1` (one column) or `COL2`
  (full width) of the `elsarticle` `5p` layout.
- Sweeps write the CSV of the data they plot alongside the figure, so a rerun
  can be diffed against the committed output.
- `main.tex` lists every solve directory in `\graphicspath`, so figures are
  included by bare filename. Add a directory there when one is created.
