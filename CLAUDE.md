# CLAUDE.md

Context for working on the *co-dimensional modelling in FESTIM* paper.

## What this repo is

A single-paper LaTeX repo (Overleaf-synced; `origin` =
`github.com/jhdark/Co-Dimensional-modelling-in-FESTIM.git`).

It was seeded from the companion *interface models* paper
(`github.com/festim-dev/interface-models`, the Ni/FLiBe kinetic-interface paper),
so it inherits that paper's preamble, styling, working rules and bibliography.
**All of that paper's content has been removed.** What is left:

- `main.tex`: the whole manuscript. Currently a **detailed outline**: every
  section has its equations (15, all labelled), specific bullets with the
  numbers from the scripts, and its figures. Bullets are one sentence per line.
  No prose yet. `lipsum` is loaded for filler while drafting.
- `references.bib`: bibliography, inherited whole from the companion paper.
  **Read the plain-text VERIFICATION NOTICE blocks (around lines 80 and 100)
  before touching it.** Several entries were assembled from web search or pulled
  from Crossref, not exported from Zotero; placeholders deliberately carry
  `author = {TODO, Replace}` so they fail loudly. Many entries are inherited and
  will not be cited here; prune only at the end, not now.
- `scripts/`: the simulations and figures, one numbered directory per paper
  section. **Read `scripts/README.md` first**: it lists every script, what it
  writes, its run time, and which parameters are sourced and which are nominal.
- `STYLE.md`: a distilled guide to the first author's own papers (structure,
  voice, captions, section lengths). **Consult it before writing any prose**
  instead of re-reading the PDFs. Where it conflicts with the rules below, the
  rules below win.
- `paper_references/` (gitignored, local only): the PDFs `STYLE.md` was built
  from, the companion `interface_models.pdf`, and `yosvany_thesis.pdf`
  (Silva-Solis, HAL tel-04750846), the data source for Application 2.

Class: `elsarticle`, `[5p]` throughout (the companion paper's look, which this
paper keeps). `[preprint,11pt]` is available for drafting but is not what the
authors want to see. Target journal is set to **Fusion Engineering and Design** (see the
`TODO(journal)` comment for the alternatives considered).

There is **no LaTeX toolchain installed** (`latexmk`, `pdflatex`, `tectonic` all
absent). Don't try to compile; check syntax by reading. If a build is needed,
say so rather than installing TeX Live unprompted.

## The subject

Codimension-1 modelling: a lower-dimensional entity embedded in the mesh (a line
in a 2D mesh, a surface in a 3D mesh) that carries **its own transport equation**
and its own state, coupled to the bulk by a flux, instead of being reduced to an
algebraic condition on the bulk traces. Grain boundaries, cracks, thin surface
layers, adsorbed layers, interfacial trapping sites, pipes embedded in a
structure.

This is explicitly the paper the companion scopes *out*: the interface-models
paper treats interfaces as reactive surfaces with no stored inventory, and defers
interfacial inventory and the codim-1 formulation to here. The Be/BeO and W/Cu
cases (Hodille MD, Silva-Solis DFT + rate equations) belong to this paper, and
both are already in `references.bib`. The W/Cu data comes from the Silva-Solis
thesis in `paper_references/`. The Be/BeO rate parameters and the digitised
molecular dynamics data come from the authors' old scripts in
`paper_references/interface_examples/`.

## The plan

**Length (set 2026-11-11): 6 to 7 pages in all, concise and to the point.**
Sections 1 to 3 take 3 to 4 pages together. Sections 4, 5 and 6 take about one
page each, 30 to 40 % figures and 60 to 70 % text, so one full-width two-panel
figure per application. The outline in `main.tex` holds more than fits: cut to
the budget when converting to prose, do not expand.

**Order of work (set 2026-11-11): scripts, data and figures first, writing
after.** Do not start prose until the figures for a section are settled.

Section list agreed 2026-09-08. The paper covers the co-dimensional (manifold) coupling now
available in \FESTIM{}, then demonstrates it on three applications.

Section list, as in `main.tex` (headings only so far, no bullets, no prose):

1. **Introduction**
2. **Motivation**: thin and lower-dimensional features in hydrogen transport, the
   cost of resolving them in the mesh, existing treatments and what they discard,
   what a co-dimensional description adds.
3. **Co-dimensional modelling in FESTIM** (the methodology / implementation
   section), in four subsections: governing equations and coupling to the bulk;
   weak formulation and mixed-dimensional assembly; the FESTIM user API;
   verification. Networks and junctions, the choice of manifold variable and its
   units, the available transport terms and the exports each get a paragraph
   inside one of those, not a subsection of their own.
4. **Application 1**: coupling a 1D flow model to a 2D/3D component. A plug-flow
   reactor model of the coolant carried on a manifold, coupled to a 2D/3D pipe
   wall, all inside FESTIM rather than through an external system code.
5. **Application 2**: interfaces carrying their own inventory. Expands the Be/BeO
   and W/Cu examples the companion interface paper defers, following
   Silva-Solis et al. and Hodille et al.: an interface concentration with
   exchange kinetics on both sides, against LTE.
6. **Application 3**: grain-boundary transport in a polycrystal, on Voronoi
   tessellations, in both 2D (1D boundaries) and 3D (2D boundaries), against a
   homogenised effective diffusivity.
7. **Discussion**: when a co-dimensional description is appropriate, cost against
   a resolved mesh, limitations and future work.
8. **Conclusions**, data availability, appendices.

The three applications are three top-level sections, not subsections of one
"Applications" section, because each carries its own setup and results. Collapse
them into one section if the page count demands it.

**Keep the subsection count down.** Each application has exactly two
subsections, "Model setup" and "Results"; the discussion has one, "Limitations
and future work"; the introduction, motivation and conclusions have none. An
earlier skeleton had 32 subsections and was cut to 11 on 2026-09-08. Do not
reintroduce a subsection for every idea: in a two-column `[5p]` layout a
subsection heading every few paragraphs fragments the argument. Use paragraphs,
or `\paragraph{}` where a run-in heading genuinely helps.

Still open:

- Verification is a subsection of the methodology section. Promote it to a
  top-level section only if the verification cases grow enough to need it.
- Author order. Ian Wojtowicz (University of Minnesota) is currently appended
  last; order is not settled.
- Which appendices are needed.
- Whether the companion interface paper is cited as in-prep or submitted.
- Isotope/multi-species scope: nothing in the plan requires more than one species
  yet.

## Where the work stands

Updated 2026-11-11 (third session: equations and specific bullets written into
`main.tex`, one commit per section). Seven draft figures exist and are included
in `main.tex` with placeholder captions. All numbers below come from the CSVs
in `scripts/`.

| Section | Figure | What it shows | Result |
|---|---|---|---|
| 3 | `illustration.pdf` | a fast line embedded in a 2D bulk, dimensionless | a manifold may end inside the bulk |
| 3.4 | `convergence.pdf` | MMS, 2D and tilted 3D | second order on both fields (2.00 in 2D, 1.97 in 3D) |
| 4 | `permeator.pdf` | permeator tube, liquid on a manifold along an axisymmetric wall; the two cases of Rader et al. 2018 | efficiency 0.6897 (Pb-17Li/RAFM) and 0.4154 (FLiBe/Ni) against published 0.690 and 0.415; within 2e-5 of the analytical solution along the tube; start-up transient of the Pb-17Li case |
| 5 | `be_beo.pdf` | filling of two Be/BeO interfaces against Hodille's MD at 750, 1000, 1250 K | the point-manifold model follows the MD at both interfaces |
| 5 | `w_cu_network.pdf` | the 14-site W/Cu network of the Silva-Solis thesis as 14 species on one point manifold | steady concentrations within 3 to 19 % of thesis Table 5; time to steady state 2969, 1.20, 1.77e-3 s against 2630, 1.06, 1.55e-3 s |
| 5 | `interface_trapping.pdf` | W/Cu bilayer, three-state interface manifold against `festim.Interface` | steady flux identical; breakthrough delayed 5 % for 6 mm of W at 340 K, by 3.5e4 for 6 um |
| 6 | `polycrystal.pdf` | 30-grain 2D Voronoi polycrystal, one subdomain per grain, network of no thickness | at D_gb/D = 1e3 the network carries about 30 times the lattice flux and breaks through three orders of magnitude earlier |

User decisions recorded 2026-11-11:

- **Application 1 needs no real geometry.** It is a benchmark against a trusted
  solution, found by literature search: Humrickhouse and Merrill 2015 (analytical)
  and Rader et al. 2018 (numbers). No experiment with enough reported data was
  found; Fukada et al. 2015 and Yoshimura et al. 2016 (Pb-Li through Inconel,
  permeation against flow rate) are the only candidates and are paywalled.
- **Application 2 keeps three strands**: Be/BeO against Hodille's MD, replication
  of Silva-Solis, and the thin-layer finding. Old scripts and the digitised MD
  data are in `paper_references/interface_examples/`.
- **Application 3 is 2D only and light.** Grain boundaries have **no thickness**:
  the network field is an areal density with its own transport equation, and the
  exchange enters with no conversion factor. Microstructure modelling proper is
  the subject of a future paper built on
  <https://github.com/festim-dev/FESTIM-Microstructure>; here it is touched on
  with Voronoi geometry only. That package may be read for ideas but **was not
  and should not be installed** (blocked as external code); `voronoi.py` is our
  own and credits it.

The Be/BeO parameters were checked against Hodille's paper
(`paper_references/D_interface_BeBeO_final_version.pdf`): Eq. (6), Table 1,
`n_i = 1e20 m-2` and `c_Be = 5e27 m-3` all match the script.

**Commits (user, 2026-11-11): do not add Claude as author or co-author.** Commit
as the configured git user with no `Co-Authored-By` trailer. Push access to
`origin` works over HTTPS.

Things found that the authors should know:

- **The fixed W concentration of the thesis is not sustainable by diffusion.**
  The network needs up to 2.5e7 m-2 s-1 from the tungsten; 1 um of tungsten at
  340 K and 2.3e7 m-3 supplies 4.4e3. With real diffusivity the interface takes
  about 1e7 s to fill, not 2630 s. This is what coupling to the bulk adds over
  the 0D model, and is shown dashed in `w_cu_network.pdf`.
- **The thesis's Arrhenius fit** (7.84e12 Hz, 1.01 eV) lies about 20 times above
  its own three tabulated times to steady state. `parameters.py` uses that
  attempt frequency for the three-state reduction, so the thin-layer sweep
  inherits the inconsistency. Refit the three-state model to the network before
  quoting the sweep.
- Our steady values sit 3 to 19 % above the thesis tables, consistently. Likely
  rounding of the tabulated barriers (0.001 eV is 3.5 % at 340 K).
- The slight overshoot in the permeator start-up near one transit time is
  unexplained: physical (an empty wall extracts more) or numerical. Check with
  a finer mesh before discussing it.

Still open:

- Application 2 keeps all three figures for now (user, 2026-11-11: "we can
  always cut later"). It is over its one-page budget.
- Citations to add through Zotero, not by hand: Humrickhouse and Merrill 2015
  (DOI 10.13182/FST14-941), Rader et al. 2018 (DOI
  10.1080/00295450.2018.1431505), and the Sherwood correlation behind Rader's
  Table III, which the paper does not name.
- Unit convention (Sec. 3): the applications use a volumetric manifold variable
  with factor 2/r (liquid in a tube) and an areal one with no factor (interface,
  grain boundary).
- `SurfaceFlux` of a bulk species on a manifold was inaccurate (up to 38 %) on a
  coarse mesh where the exchange varied sharply near an inlet. Check before
  quoting such an export.

## The FESTIM implementation this paper describes

**Merged into `main`**, not a feature branch, and released in \FESTIM{} 2.2
(tag `v2.2`, commit `5620e8f5`, identical to `origin/main` on 2026-11-11; on conda-forge and PyPI as `festim=2.2`). Local clone: `/home/jhdark/repos/FESTIM`; use
`git show origin/main:<path>` and `git fetch` before trusting what is checked
out. The work landed over several PRs, the codim ones being festim-dev/FESTIM
**#1250** (a manifold adjacent to more than two volumes, plus the polycrystal
examples) and **#1231** (drift terms); earlier codim PRs precede those in the
log. The superseded `rem/codim` branch is still in the clone; prefer `main`.

Documentation to read before describing the API in the paper:

- `docs/source/userguide/subdomains.rst` on `main`, section "Codimensional
  (manifold) Subdomains", and `docs/source/userguide/drift.rst`.
- The FESTIM workshop, <https://festim-workshop.readthedocs.io/en/latest/content/manifolds/index.html>,
  which has "Transport along a manifold" and "A coolant channel along a pipe
  wall". The latter is the closest existing worked example to Application 1.

In summary, as of `main`:

- A manifold is a `VolumeSubdomain` with `dim` one less than the mesh dimension
  and a `locator`. It is tagged in the **facet** meshtags, so its `id` must be
  unique among the surface subdomains too, and it can be used directly wherever a
  surface is expected (e.g. as the `subdomain` of a `ParticleFluxBC`).
- It may sit on the outer boundary, **between** two volume subdomains, or be
  adjacent to **more than two** volumes, which is what makes a grain-boundary
  network with triple junctions expressible (Application 3).
- Coupling is written twice, as a `ParticleFluxBC` on the bulk and a
  `ParticleSource` on the manifold, with `species_dependent_value` letting each
  half read both concentrations across meshes.
- **Units are the user's responsibility.** A flux BC is per area, a source is per
  volume, so the manifold-side source generally needs a conversion factor. FESTIM
  imposes no unit convention on a manifold species: volumetric (a layer of
  thickness λ, source J/λ), areal (an adsorbed layer, source J) or line density.
  This is a real modelling decision, and Sec.~`sec:method:units` exists to fix a
  convention for it.
- One source may **not** read both sides' bulk concentrations at once; interior
  manifolds are integrated over interior facets and each term must be restricted
  to one side. Split into one exchange per side.
- A pair of volume subdomains is separated **either** by an `Interface` (the LTE
  jump condition of the companion paper) **or** by a manifold, never both; FESTIM
  raises if they cover the same facets. This is the pivot for Application 2.
- Advection and drift terms on a manifold take an ordinary ambient vector and
  self-project onto the manifold.
- Reactions, `ImplicitSpecies`, Dirichlet BCs on manifold ends, derived
  quantities and exports all work on manifolds; each has a system test.

**Verification already in the tree**, worth reading before designing the paper's
own verification cases, and worth citing as the test suite behind it:

| File | What it covers |
|---|---|
| `test/system_tests/test_codim1_coupling.py` | 2D and 3D tilted coupling, advection, transient time integration, time-dependent and reaction sources, `ImplicitSpecies` |
| `test/system_tests/test_codim1_interface.py` | interior manifolds against analytical solutions, particle conservation, declaration-order independence, 3D tilted MMS, and the raises |
| `test/system_tests/test_codim1_boundary.py` | Dirichlet on manifold ends vs analytical, pipe inlet concentration |
| `test/system_tests/test_codim1_coordinates.py` | cylindrical and spherical coordinates: point manifolds (`dim=0`) in 1D radial meshes, lines in axisymmetric meshes |
| `test/system_tests/test_codim1_exports.py` | derived quantities and fluxes on exterior and interior manifolds, flux balance, outlet flux under advection |
| `test/system_tests/test_codim1_polycrystal.py` | grain-boundary networks: three grains against a series chain, one measure id per side, triple junctions, a grain blocked off from the network |
| `test/test_codim1_subdomain.py` | unit level: `dim`/codim validation, facet tagging, id-namespace clashes, `solution_on` resolution, manifold boundaries |

**Check `main` before claiming any capability in the paper.** The list above is
a snapshot taken 2026-09-08, not a contract.
Rechecked against `v2.2` on 2026-11-11: all 106 codim tests pass in `codim-env`
(FESTIM 2.2, DOLFINx 0.11.0). Also in 2.2 and not listed above: cylindrical and
spherical coordinate systems on manifolds, `OutflowBC` on a manifold end, drift
terms assembled in divergence form (an untagged manifold end is a closed end),
and codim-2 `SurfaceSubdomain`s for the boundary of a manifold. Most
interior-manifold and all polycrystal tests are marked serial only.

## Related repos on this machine

| Path | What it is |
|---|---|
| `/home/jhdark/repos/FESTIM` | FESTIM source. The implementation is at tag `v2.2`. Use `git show v2.2:<path>`; don't switch branches, the clone is usually on an unrelated one. |
| `/home/jhdark/repos/Co-Dimensional-modelling-in-FESTIM` | Here. |

The `interface-models` and `mixed-dim` repos an earlier version of this file
listed are not on this machine and are not needed: everything is reproducible
from FESTIM 2.2. The companion paper is available as
`paper_references/interface_models.pdf`.

Environment: conda env `codim-env`, recipe in `scripts/environment.yml`, pinned
to `festim=2.2` from conda-forge with no extra `pip install`. It exists on this
machine; run scripts with `conda run -n codim-env python ...`. To read or run
the FESTIM tests at the release, use `git show v2.2:<path>` or `git archive v2.2
test` into a scratch directory: the local clone is usually checked out on an
unrelated branch.

Plotting goes through `scripts/common.py` (`from common import *`): morethemes
"urban", the palette `#1a4848, #f7b000, #f46036, #c9f2c7, #aceca1`, white
background, top and right spines removed, widths `COL1`/`COL2` for the `5p`
layout. Use it for any new figure.

Practical notes, learnt 2026-11-11:

- `conda run -n codim-env python - <<EOF` prints nothing: write the snippet to a
  file. For long runs use `conda run --no-capture-output ... python -u` and
  `OMP_NUM_THREADS=1`, and send output to a log.
- To look at a figure, convert the PDF to PNG with PyMuPDF and Read the PNG.
  There is no `pdftotext`; PDF text is extracted with `pypdf`. Neither is in
  `codim-env`: install them with `pip install --target` into the scratchpad.
- `np.isclose` in a locator has a default tolerance of about `1e-8 + 1e-5 |x|`.
  On a graded mesh with smaller cells it tags several vertices as the manifold.
  Pass `rtol=0, atol=...` explicitly.
- A FESTIM surface subdomain must touch exactly one volume subdomain. With one
  subdomain per grain, the loaded and exit faces need one surface per grain.
- Supplying gmsh tags: set `model.volume_meshtags` and `model.facet_meshtags`
  after construction, and declare subdomains with ids only. The manifold id goes
  in the facet tags.
- Form compilation grows quickly with the number of subdomains: 30 grains take
  about a minute on first run and are cached afterwards.

## Working rules

**Update this file at the end of every engagement** (state of the work, what was
learnt, what is open), and `scripts/README.md` with it. Helper files that save
time later are welcome without asking.

### Sources and numbers

- **Never invent a citation.** If a claim needs a reference that is not in
  `references.bib`, insert a `\TODO{}` or `\VERIFY{}` naming what is needed.
  The three annotation macros are `\TODO{}` (red), `\VERIFY{}` (orange),
  `\KEY{}` (blue); all three are deleted before submission.
- **Never silently upgrade a placeholder bib entry.** Entries with
  `author = {TODO, Replace}` must keep failing loudly until re-exported from
  Zotero. Same for the `note` fields recording what is unverified.
- **Do not fabricate numbers.** No parameter table rows, dimensions, fitted
  constants, or simulation results unless they come from a script in `scripts/`
  or a source the user supplies. Every number quoted in the paper should be
  traceable to a script.
- **Do not describe a FESTIM capability without checking the branch.** The
  paper describes the 2.2 release; read the source or the test at tag `v2.2`,
  then write.

### LaTeX conventions

- **One sentence per line.** Never wrap a sentence across lines and never put
  two sentences on one line. Both authors edit in Overleaf simultaneously, so
  this keeps diffs sentence-sized and lets a line in the PDF be found by search
  in the source.
- Notation macros already defined: `\FESTIM \TMAP \MHIMS \kB \half`. Reuse them;
  do not hand-roll new notation for the same quantity. Add new macros to the
  preamble and record the term in the registry below at the same time.
- If a concentration macro named `\cm` is reintroduced, it collides with
  siunitx's own short `\cm`; see the note in the preamble for the guard needed.
- **Units go through `siunitx`** (v3 macros): `\qty{2.032}{\milli\metre}`,
  `\unit{\metre\per\second}`, `\num{1.31e5}`. Never hand-roll
  `$1.31\times10^{5}$~Pa`. Spell units out in full inside `\qty`/`\unit`
  (`\centi\metre`, never `\cm`). Clean powers of ten that are part of a maths
  relation (`$\mathrm{Da} = 10^{2}$`) stay as maths.
- Keep every equation label when rewriting; labels are cross-referenced
  throughout.
- **Figure and table references go at the end of the sentence** as
  `(see Fig.~\ref{...})`, or as the subject of their own sentence
  (`Figure~\ref{...} shows ...`). Never mid-clause. This follows the authors'
  own papers.
- **Never use em dashes** (`---`, `--`, or the character itself). Use a comma,
  a colon, a semicolon, parentheses, or two sentences. Applies to prose,
  headings, captions and comments.

### Prose style

- British spelling ("realised", "generalisation").
- **First person is for our moves and our findings; everything else is
  impersonal.** "We formulate the coupling as ..." keeps its *we*. "Reported
  grain-boundary diffusivities span orders of magnitude" does not take one.
  Roughly once per 200 words overall.
- **One term, one meaning.** A term that carries two senses in one paper is an
  error, however clear each sense is locally. See the terminology registry
  below; add to it whenever a new term is introduced.
- **Sentence cap: 25 words** for descriptive prose. Longer is allowed only when
  splitting would break a logical relation that has to be held in one breath.
- **Paragraph cap: six sentences.**
- **Active voice by default.** "Evaluate one time constant per side", not
  "one time constant should be evaluated per side".
- No bullet lists in the final text, except where an explicit decision procedure
  earns one.
- **Cut "btw points".** A sentence that gives a further example, or shows that
  an idea also appears in another field, and which no later sentence depends
  on, comes out. Test: delete it, and check whether any later sentence breaks
  or whether the reader loses something needed to use or judge the model. These
  cluster immediately after a claim, as a second supporting citation that adds
  a field rather than a fact. Defensive writing that answers an objection a
  referee will raise is load-bearing and stays.
- **Honest caveats are kept, not softened.** They pre-empt referees; don't
  delete them when converting notes to prose.
- **Core derivations belong in the main text.** Appendices carry supporting
  proof for things not central to the argument. If a result is quoted in three
  places and named as the paper's falsifiable content, derive it where the
  reader meets it, however short the algebra.
- **No AI tells.** Avoid: "it is worth noting", "it is important to note",
  "delve", "leverage", "showcase", "underscore", "crucially", "notably",
  "robust" as filler, "a testament to"; the "not only X but also Y" and "it is
  not X; it is Y" constructions when they are decoration rather than the actual
  argument; three-item lists padded to three for rhythm; enumerators
  ("First, ... Second, ... Third, ...") where the preceding sentence has
  already announced the count; a summarising sentence that restates its own
  paragraph; stacked hedges ("may potentially suggest"). Some emphatic
  constructions are the author's own voice and are preserved as written.
- **Three tics to keep counting.** Re-grep before declaring a section done.
  - `rather than`: the authors' own papers use it essentially never. Prefer
    restructuring, "instead of", "and not", or a second sentence, and vary the
    replacement so "and not" does not become the next tic.
  - the trailing gloss `, which is <restatement>`: drop the "which is" and leave
    the bare appositive, or split the sentence.
  - `This is the <noun> that/used in ...` as a cross-reference. Say "We use this
    solution in Sec. 4.1".
- **Banned words: "closure" and "closed form".** For an algebraic interface
  constraint write "condition", "interface law", "constraint", or "model". For
  analytical steady states write "analytical solution". An interface is
  "treated" or "described" a given way, it is not "closed" by it.
- **Minimise Latin.** Prefer "in advance" and "known beforehand" to "a priori";
  drop "a fortiori" entirely.
- **Voice benchmark.** Delaporte-Mathurin et al., arXiv:2603.25751 (PathSim) is
  the closest sample of the first author's own prose: plain and expository, mean
  sentence ~23 words, plain connectives, almost no compressed epigrams. Match
  that register.

## Terminology registry

One term, one meaning. Each row records the sense the paper uses and what was
banned or renamed to get there. Settled 2026-11-11 while outlining; revisit only
with the authors.

| Term | The one meaning | Notes |
|---|---|---|
| manifold | the codimension-1 subdomain $\Gamma$ carrying its own transport equation | Introduced once in the introduction as "a subdomain of one dimension less than the mesh, called a manifold". Do not alternate with "codim-1 subdomain" or "lower-dimensional entity". "Co-dimensional" is used only for the description or method as a whole. |
| bulk, bulk subdomain | a full-dimensional subdomain $\Omega_i$ and its field | Never "volume", since FESTIM's `VolumeSubdomain` covers both. |
| interface | the physical plane between two materials (Application 2) | Not a synonym for manifold. |
| algebraic interface condition, equilibrium condition | the jump condition on the two bulk concentrations, FESTIM's `Interface` | Never "closure". "Equilibrium condition" is used in Application 2 for the specific ratio of Eq. `eq:interface:lte`. |
| exchange, exchange law | the flux $J_i$ between $\Omega_i$ and $\Gamma$ and the expression for it | Not "coupling term" or "transfer". |
| network | the connected set of grain boundaries declared as one manifold (Application 3) | |
| liquid | the flowing fluid of Application 1 | Not "coolant": the benchmark is a permeator, not a cooling channel. The directory name `1-coolant-channel` and the label `fig:coolant` are historical. |

Notation, fixed in `main.tex`:

| Symbol | Meaning |
|---|---|
| $\Omega_i$, $\Gamma$ | bulk subdomain $i$, manifold |
| $c_i$, $c_\Gamma$ | bulk and manifold concentrations |
| $D_i$, $D_\Gamma$ | bulk and manifold diffusivities |
| $J_i$ | exchange flux from $\Omega_i$ into $\Gamma$, per unit area of $\Gamma$ |
| $\alpha$ | factor converting $J_i$ to the units of $c_\Gamma$: 1 (areal density), $1/\lambda$ (layer), $P/A$ (channel) |
| `\gradG` | tangential gradient $\nabla_\Gamma = (I - n \otimes n)\nabla$ |
| $\mathbf{u}$, $\mathbf{n}$, $\mathbf{n}_i$ | drift velocity, normal to $\Gamma$, outward normal of $\Omega_i$ |
| $c_\mathrm{f}$, $c_\mathrm{w}$, $c_\mathrm{w,l}$, $k_\mathrm{T}$, $\eta$, $\tau$, $\zeta$ | Application 1: liquid and wall concentrations, liquid at the wall, mass transfer coefficient, efficiency, and the two groups of the analytical solution |
| $n_\Gamma$, $\theta$, $\nu_{i \rightarrow \Gamma}$, $\lambda_i$ | Application 2: site density, coverage, jump frequency, jump distance |
| $\sigma$, $D_\mathrm{gb}$, $k_\mathrm{t}$, $k_\mathrm{d}$ | Application 3: areal density on the network, boundary diffusivity, trapping velocity, detrapping rate |
