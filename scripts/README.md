# Scripts

Simulation scripts backing the paper.

**Status: empty.** Only the environment recipe is kept from the companion
*interface models* paper. Nothing here has been written for this paper yet.

## Environment

```bash
conda env create -f environment.yml
conda activate codim-env
```

The FESTIM branch this paper describes is not pinned yet. When it is, record
the branch and the commit here and add the `pip install` line the environment
needs on top of the conda recipe.

## Contents

| Directory | Paper section | What it does |
|---|---|---|
| | | TODO |

## Figures

`main.tex` sets `\graphicspath` to the solve directories, so figures are
included by bare filename and stay next to the script that writes them. Update
`\graphicspath` whenever a directory is added.

| PDF | Paper | Written by |
|---|---|---|
| | | TODO |

## Conventions

- Directory names are kebab-cased and numbered by the order they appear in the
  paper (`1-...`, `2-...`).
- Plotting uses `morethemes` (`mt.set_theme("urban")`) and the palette
  `#1a4848, #f7b000, #f46036, #c9f2c7, #aceca1`, top and right spines removed.
  Match that style for any new figure.
- Sweeps write the CSV of the data they plot alongside the figure, so a rerun
  can be diffed against the committed output.
