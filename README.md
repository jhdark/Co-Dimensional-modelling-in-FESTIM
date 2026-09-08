# Co-Dimensional coupling with FESTIM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Manuscript source and simulation code for the paper by Remi
Delaporte-Mathurin and James Dark (MIT).

**Status: empty skeleton.** The repository was seeded from the companion
*interface models* paper, so it carries that paper's LaTeX preamble, styling
conventions and bibliography. All of its content has been removed. The plan for
this paper lives in [CLAUDE.md](CLAUDE.md).

## The paper

TODO: one or two paragraphs on the argument, once it is settled. The topic is
co-dimensional (codimension-1) modelling in [FESTIM](https://github.com/festim-dev/FESTIM):
interfaces and other lower-dimensional features carrying their own state and
equations alongside the bulk transport problem, rather than being reduced to an
algebraic condition on the bulk traces.

## Repository layout

| Path | What it is |
|---|---|
| `main.tex` | The whole manuscript (`elsarticle`, single file). |
| `references.bib` | Bibliography, inherited from the companion paper. Read the verification notices before editing. |
| `scripts/` | Every simulation, verification and figure script in the paper. |

Every figure and every number quoted in the paper should be produced by a
script in `scripts/`, with each script writing its PDF next to itself;
`main.tex` sets `\graphicspath` to those directories, so figures are included
by bare filename.

## Running the scripts

```bash
cd scripts
conda env create -f environment.yml
conda activate codim-env
```

## Building the manuscript

```bash
latexmk -pdf main.tex
```

The class is `elsarticle` with `[5p]`. `[preprint,11pt]` is available for
drafting a single-column version.

Building requires a local LaTeX installation (`elsarticle`, `siunitx` v3); the
manuscript is otherwise built on Overleaf, which this repository is synced to.

## Licence

Released under the MIT licence, see [LICENSE](LICENSE).
