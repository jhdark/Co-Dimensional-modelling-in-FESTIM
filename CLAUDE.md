# CLAUDE.md

Context for working on the *co-dimensional modelling in FESTIM* paper.

## What this repo is

A single-paper LaTeX repo (Overleaf-synced; `origin` =
`github.com/jhdark/Co-Dimensional-modelling-in-FESTIM.git`).

It was seeded from the companion *interface models* paper
(`github.com/festim-dev/interface-models`, the Ni/FLiBe kinetic-interface paper),
so it inherits that paper's preamble, styling, working rules and bibliography.
**All of that paper's content has been removed.** What is left:

- `main.tex`: the whole manuscript. Currently an **empty section skeleton**:
  preamble, frontmatter and `\TODO{}`-marked section shells, nothing else. The
  section list is provisional and should be revised once the argument is fixed.
- `references.bib`: bibliography, inherited whole from the companion paper.
  **Read the plain-text VERIFICATION NOTICE blocks (around lines 80 and 100)
  before touching it.** Several entries were assembled from web search or pulled
  from Crossref, not exported from Zotero; placeholders deliberately carry
  `author = {TODO, Replace}` so they fail loudly. Many entries are inherited and
  will not be cited here; prune only at the end, not now.
- `scripts/`: empty apart from `environment.yml` (conda env `codim-env`) and a
  stub README.

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
both are already in `references.bib`. The companion's notes describe a
`3-interface trapping/` script directory (Be/BeO, W/Cu, raw DOLFINx) held back
for this paper; **it is not on this machine**, so ask the user for it before
assuming those results exist.

## The plan

Agreed 2026-09-08. The paper covers the co-dimensional (manifold) coupling now
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

## The FESTIM implementation this paper describes

**Merged into `main`**, not a feature branch, and released in \FESTIM{} 2.2
(local tag `v2.2-rc.1`). Local clone: `/home/jdark/repos/FESTIM`; use
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
| `test/system_tests/test_codim1_exports.py` | derived quantities and fluxes on exterior and interior manifolds, flux balance, outlet flux under advection |
| `test/system_tests/test_codim1_polycrystal.py` | grain-boundary networks: three grains against a series chain, one measure id per side, triple junctions, a grain blocked off from the network |
| `test/test_codim1_subdomain.py` | unit level: `dim`/codim validation, facet tagging, id-namespace clashes, `solution_on` resolution, manifold boundaries |

**Check `main` before claiming any capability in the paper.** The list above is
a snapshot taken 2026-09-08, not a contract.

## Related repos on this machine

| Path | What it is |
|---|---|
| `/home/jdark/repos/FESTIM` | FESTIM source. The implementation this paper describes is on `main` (FESTIM 2.2). Use `git show origin/main:<path>`; don't switch branches. The stale `rem/codim` branch is superseded. |
| `/home/jdark/repos/mixed-dim` | Scratch prototypes for mixed-dimensional assembly (`mixed_domain.py`, `mwe.py`, plus `.bp` outputs). Predates the FESTIM branch; provenance, not a source to cite. |
| `/home/jdark/repos/interface-models` | The companion **paper** repo (kinetic interface models, Ni/FLiBe; `origin` = festim-dev/interface-models). Same layout as here, and the source of this repo's preamble and working rules. Its `scripts/` is the companion's simulation code. |
| `/home/jdark/repos/papers/Co-Dimensional-modelling-in-FESTIM` | Here. |

Environment: conda env `codim-env`, recipe in `scripts/environment.yml`. It does
not exist on this machine yet, and the extra `pip install` for the FESTIM branch
is not pinned yet either; record both in `scripts/README.md` once they are.

Plotting uses `morethemes` (`mt.set_theme("urban")`) and the palette
`#1a4848, #f7b000, #f46036, #c9f2c7, #aceca1`, top and right spines removed.
Match that style for any new figure.

## Working rules

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
  implementation is unmerged and moving; read the source or the test, then write.

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
banned or renamed to get there. **Empty: repopulate as the paper introduces
terms.** Candidates to settle early, since the FESTIM docs and the literature
use several of them interchangeably:

| Term | The one meaning | Notes |
|---|---|---|
| manifold / codim-1 subdomain / lower-dimensional entity | TODO: pick one, define it once | FESTIM's docs and API say both "manifold" and "codimensional subdomain". The paper should not. |
| interface vs manifold | TODO | FESTIM's `Interface` is the algebraic jump condition; a manifold is a subdomain with its own equation. The two are mutually exclusive on a given set of facets, so the words must not blur. |
| bulk vs volume | TODO | `VolumeSubdomain` covers both a genuine volume and a manifold, so "volume" is ambiguous in prose. |
