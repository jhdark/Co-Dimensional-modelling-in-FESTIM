# STYLE.md: how James Dark's papers are written

Descriptive guide distilled from seven papers, for drafting the co-dimensional paper without re-reading them.
Where a habit below conflicts with a rule in `CLAUDE.md`, `CLAUDE.md` wins; conflicts are flagged with **[conflict]**.

Corpus and short names (first author in brackets):
- **NF24**: Modelling neutron damage effects on tritium transport in tungsten, Nucl. Fusion 2024 [Dark]
- **WCLL**: Influence of hydrogen trapping on WCLL breeding blanket performances, Nucl. Fusion 2021 [Dark]
- **ARC**: Multiphysics tritium transport modelling of the ARC breeding blanket, preprint 2026 [Dark]
- **V2**: FESTIM v2.0, IJHE 2026 [Dark]
- **V1**: FESTIM review, IJHE 2024 [Delaporte-Mathurin; Dark second]
- **WEST**: Fuel retention in WEST and ITER divertors, Nucl. Fusion 2021 [Delaporte-Mathurin; Dark fourth]
- **IFACE**: kinetic interface models, companion draft [Delaporte-Mathurin; Dark second]

The four Dark-first papers are the voice benchmark. IFACE is the outlier: heavy "we", short epigrammatic sentences, long captions. Borrow its structure (it is the sister paper), not its voice.

## 1. Introductions

Length: 4 to 5 paragraphs, 400 to 750 words (WCLL ~390, NF24 ~690, V2 ~730, ARC ~750), then a one-sentence reproducibility paragraph. No subsections. IFACE is the exception (11 short paragraphs).

Paragraph functions, in order:
1. **Component or problem and why it matters** (safety, inventory, design). Opens on the object, not on the code. "An integral part of the DEMO design is the breeding blanket (BB) responsible for tritium production to replenish fuel inventories." (WCLL). ARC reuses the same opener: "An integral component of the ARC ... fusion reactor concept is its breeding blanket".
2. **The physics in two or three sentences**: "Tritium permeates through materials by diffusion. However, it can get trapped within microstructural defects such as vacancies, dislocations, interstitials, and voids." (NF24)
3. **What exists and the gap**, citations in blocks, gap introduced by "However": "However, previous work that evaluated values of tritium inventories in the structure and permeation fluxes does not account for trapping" (WCLL); "However, integrated simulations that represent the coupled multiphysics environment ... remain scarce." (ARC)
4. **Contribution**, impersonal, naming FESTIM: "A model is proposed to predict the temporal evolution of the damage-induced trap densities." (NF24); "To address these challenges, the present work introduces a modular modelling workflow" (ARC); "To this end, the tritium transport code FESTIM ... was employed, extended and coupled to a fluid dynamics solver." (WCLL). Scope limits are stated here too: "The objective of this study is to demonstrate a flexible framework ... rather than to provide a fully resolved representation" (ARC).
5. **Reproducibility line**, always last, own paragraph: "All the results presented in this paper can be reproduced with the scripts available at [28]." (NF24)

Outline: application papers (NF24, WCLL, ARC, WEST) have **no** section-by-section outline. Only the code papers do: "Section 2 provides an overview ... Sections 3-6 describes the mathematical framework ... Finally, Section 10 summarises the advances" (V2). For a 6 to 7 page paper, skip it or use one sentence.

## 2. Methodology and model sections

- **Equations come first, explanation second.** A one-line lead-in ending in a colon, the equation(s), then a sentence starting with the equation number: "Tritium transport can be modelled using macroscopic rate equations first introduced by McNabb and Foster [29]:" then "Equations (1) and (2) describe the thermo-kinetic model used for tritium transport." (NF24). WCLL stacks all six governing equations at the top of the section and then walks through them: "Eq. (1) and (2) are the steady state Navier-Stokes equations ...".
- **Symbols are defined term by term in running prose with units attached**, pattern "X is the <name> in <unit>": "Φ is the damage rate in [dpa s−1], and can vary spatially. K is the trap creation factor in [traps m−3 dpa−1]." (NF24); "where Dturb is the turbulent diffusivity of hydrogen, νt is the turbulent kinematic viscosity (obtained from the fluid dynamics simulation), and Sct is the turbulent Schmidt number." (ARC). Older papers put units in square brackets; ARC and V2 write "in units of m−3". Use siunitx here.
- Each term of an equation is named when introduced: "The first term on the right-hand side of equation (1), ∇·(D∇cm), is a Fickian diffusion term" (NF24); "The coupling term, R(...), accounts for all local interactions between species" (V2).
- **Exclusions are stated flatly, one sentence each**: "The Soret effect is not considered in this work." (ARC); "Trapping is omitted, since it plays no part in the arguments that follow." (IFACE)
- Assumptions use "It is assumed that": "It is assumed that only empty traps are created ... This is due to a current technical limitation of the FESTIM code" (NF24).
- Boundary conditions: one sentence naming the condition and its physical meaning, then the equation reference: "A homogeneous Dirichlet boundary condition is applied to the inlet, which assumes a perfect purification system (see Eq. (19))." (WCLL)
- **Tense**: present for what equations state and what the model is ("Equation (3) describes"); past passive for what was done ("was employed", "was modelled", "were fitted"). Present passive in setups is also common ("is applied", "is imposed").
- **Person**: almost entirely impersonal. Counts of "we" in body text: WCLL 0, ARC 0 (one "To our knowledge"), NF24 1 ("we can make informed guesses"), V2 3 ("we consider", "Here, we assume"). Self-reference is "this work", "the present work", "this study", "This paper presents". "one can" appears in NF24 derivations ("one can simplify equation (3)"). IFACE uses "we" every few sentences. **[conflict]** `CLAUDE.md` wants "we" for our moves, about once per 200 words, which is nearer IFACE than the Dark-first papers. Follow `CLAUDE.md`, but most sentences stay impersonal.
- **Code/API** (V2, IFACE): one prose sentence, then a short listing with `import festim as F`, `...` for omitted arguments, then a sentence on what the snippet does: "Users define such reactions using the SurfaceReaction class:" (V2). Listings are 5 to 15 lines, at most one or two inline comments.
- **FESTIM is introduced in one sentence** with version and citation: "The open-source hydrogen transport code FESTIM (v1.1.1) [27] was employed and extended" (NF24).
- **Verification** (V1, IFACE, V2): state the test problem with its numbers in prose, say an analytical or manufactured solution exists, report one error number. "The computed and exact solutions agree very well (see Fig. 16(a)). The L2 error is 5.49 × 10−4." (V1); "The computed interfacial concentrations agree with the analytical solution to a relative difference of 6 × 10−12 or less across the whole sweep." (IFACE)

## 3. Model setups and parameters

- **Parameters live in small tables, prose points to them.** "The transport and trapping properties of each material are described in Tables 4 and 5, respectively." (WCLL); "The reference operating conditions assumed throughout this work are summarised in Table 1." (ARC); "All values for heat transfer boundary conditions are described in Table 3." (WCLL)
- Table layout: 3 or 4 columns, "Parameter | Description | Value | Units" (ARC, WCLL) or "Property | Value | Unit" (NF24). 5 to 10 rows. Captions are a short fragment: "Table 2. TDS simulation parameters." (NF24); "Table 5: Trap properties for W and EUROFER" (WCLL).
- **Sources are cited in the row label or in the pointing sentence**, not in a footnote: rows read "W [22]", "EUROFER [12]", "LiPb [11, 32]" (WCLL). IFACE adds a "Source" column and an "Assumed carrier" column.
- Single values that do not merit a table go in prose with the citation: "The pre-exponential factor of the diffusion coefficient of deuterium in tungsten was D0 = 1.6 × 10−7 m2 s−1 and its activation energy ED = 0.28 eV [35]." (NF24)
- Geometry gets one schematic figure with boundary labels (Γ names) plus a dimensions table (WCLL Fig. 2 + Table 1; IFACE Fig. 7).
- Setups are 1 to 3 paragraphs: geometry, materials, boundary conditions, run length. "Simulations were run over a period of 10 days, which was found to be enough to reach a steady state." (WCLL)
- Uncertain inputs are flagged where they are introduced: "However, there is uncertainty associated with this value as it has been evaluated experimentally under a vacuum." (WCLL); "experimentally validated values of the turbulent Schmidt number are scarce" (ARC).
- IFACE adds an explicit scope paragraph before the application: "Nothing below is fitted, and nothing is compared with a measurement." Worth copying for the three applications here.

## 4. Narrating results

- **Figure references are parenthetical at the end of the clause or sentence**: "(see Figure 7)", "(see figure 6)", "(see Fig. 1)". This is the dominant form in every paper (WCLL has about 40 in 4 pages of results). Second form, figure as subject: "Fig. 2 shows the concentration fields at t = 5 s and t = 10 s." (V2). ARC also uses "as shown in figure 6e" and a bare "(figure 9)". "Fig." vs "Figure" simply follows the journal (IJHE "Fig.", IOP "figure", preprints "Figure"); for FED use "Fig." as `CLAUDE.md` says.
- **Statement then cause.** An observation with its figure reference, then a sentence opening "This is due to", "This is explained by", "is attributed to": "Prior to 10^5 s, the highest tritium fluxes are found in the front breeding zone pipes ... (see Figure 9). This is due to the decreasing exponential nature of the tritium source term in the LiPb." (WCLL); "the small difference is most likely attributable to the different time discretisation schemes used by the two codes." (ARC)
- **Numbers as factors, percentages or orders of magnitude, with the comparator named**: "the tritium inventory increases by a factor of 4.5 when including trapping mechanisms" (WCLL); "tungsten damaged at a rate of 10^2 dpa/FPY has an inventory four orders of magnitude higher compared to the undamaged case" (NF24); "runtime was reduced to 113.5 s, corresponding to an approximately 11× speedup" (V2).
- **Code-to-code and analytical comparisons give both numbers side by side**: "The steady-state outlet flux is 1.0 mg s−1 in FESTIM and 1.01 mg s−1 in OpenFOAM, with corresponding inventories of 243 mg and 240 mg." (ARC). Agreement vocabulary is graded: "agree closely", "in good agreement", "agree very well", "a reasonable agreement is observed".
- "approximately" precedes most simulated values in ARC (13 uses); NF24 and WCLL quote them bare.
- Observations are passive: "was observed", "was found to", "is shown to", "can be seen": "It was observed that concentrations of trapped tritium were lower near the hot spots (see Figures 4b and 8a)." (WCLL)
- Results sections open with a roadmap or scope sentence: "This section covers the results of a standard case and the study of trapping effects, followed by a parametric study" (WCLL); "All results presented in this section correspond to values for the full breeding blanket." (ARC)
- Each results subsection ends on a design or modelling implication: "This result could be of particular concern for fusion devices, as this temperature range is within the operational limitations of tungsten." (NF24)
- **Caveats are short declaratives, placed right after the number they qualify**, usually opened by "It should be noted that" or "However": "It should be noted that only 1 trap was used in the EUROFER and 2 in W." (WCLL); "It should be emphasised that these values represent a lower-bound estimate." (ARC); "However, this phenomenon has not been considered in the present study." (NF24); "was not considered as it was outside the scope of this work" (WCLL). Limitations are named as limitations: "Despite these insights, several limitations of the present model must be acknowledged." (ARC)
- Parametric studies are motivated by literature scatter, then reported as a range: "This variation results in a range of two orders of magnitude for a given temperature. Thus, a parametric study was undertaken" (WCLL).

## 5. Figure captions

Dark-first papers: **one noun-phrase fragment, 8 to 30 words, no verb**, panel positions in brackets, optionally one short second sentence decoding line styles. No interpretation in the caption.
- "Figure 3. Trapping site density Fermi-Dirac distribution described by equation (7)." (NF24)
- "Figure 7. Tritium inventory over 1 FPY (top) per unit section and the concentration distribution after 24 h (bottom) from simultaneous damage exposure and tritium implantation, at 700 K varying the damage rate." (NF24)
- "Figure 7: Temporal evolution of the tritium inventory in the LiPb, first wall, breeding zone pipes and structure. Dashed lines correspond to cases without traps." (WCLL)
- "Fig. 6. Comparison of average runtimes for the Diffusion: multi-material benchmark case [40] using FESTIM v1 and v2.0 with different interface treatments. Results are averaged over ten runs." (V2)
- "Figure 8: Temporal evolution of the total tritium inventory (bottom) and the mass flux of tritium leaving the outlet (top) in the ARC blanket model, comparing the FESTIM and OpenFOAM solutions." (ARC)

Stock openers: "Temporal evolution of", "Evolution of ... as a function of", "Comparison of", "Influence of ... on", "Distribution of". Sub-captions are two or three words: "(a) 2000 s", "(b) Steady state".
IFACE captions are the opposite: a headline fragment plus an (a)/(b)/(c) walkthrough and an interpretive sentence, 60 to 110 words. Do not copy that length in a 6 to 7 page paper.

## 6. Discussion and conclusions

- **No separate Discussion section in any Dark-first paper.** Discussion is folded into the last paragraphs of Results (WCLL, ARC) and into the Conclusion. Only IFACE has one (four subsections, ending with "Limitations and future work").
- **Conclusion length**: 3 to 5 paragraphs, 220 to 550 words (V2 ~220, WCLL ~310, NF24 ~550, ARC ~550). No bullets, no new figures.
- **Structure**: (1) what was done, restating the tool; (2) headline numbers repeated from Results; (3) limitations; (4) future work and implications.
- Openers: "This work presents a new mathematical model for describing hydrogen traps induced by displacement damage in tungsten" (NF24); "This work demonstrates a fully open-source, modular workflow" (ARC); "The tritium transport code FESTIM was extended to investigate how trapping mechanisms affect tritium inventory" (WCLL). Present perfect for the work: "has been presented", "have been analysed and fitted".
- Numbers in the conclusion: "Results show that the inclusion of trapping mechanisms increase steady state tritium inventories in the BZ piping and structure by 35% and 14%, respectively." (WCLL)
- Limitations in one list-sentence, then the consequence: "The present model neglects tritium transport in solid structures, permeation through the inner wall, and chemical effects within the breeder ... The predicted inventory should therefore be regarded as a lower bound" (ARC).
- **Future work phrasing**: "Future work will improve the accuracy of the model by considering additional traps" (WCLL); "is the next logical step of this work" (WCLL); "will be investigated in a future study" (WCLL); "A key priority for future development is therefore to replace ..." (ARC); "the model can be developed further to account for" (NF24); "This will be the subject of future work" (IFACE). Simple future "will", specific named extensions, no "we plan to".
- Often ends on a "Nevertheless" sentence restating value, or an implication: "Thus, the influence of damage-induced trapping in tritium transport modelling should be considered" (NF24).

## 7. Sentence-level habits

- **Sentence length**: typical 20 to 25 words in NF24, WCLL and V2; ARC runs longer (25 to 30, many above 30). Setup sentences are often short (8 to 15 words): "No traps are set in the materials." (V1). **[conflict]** cap at 25 per `CLAUDE.md`.
- **Connectives, sentence-initial, followed by a comma.** "However" is the workhorse (NF24 13, WCLL 8). Then "Furthermore" (NF24 11), "Additionally" (WCLL 4), "Thus" (NF24 5, WCLL 3), "Therefore", "Moreover", "Nevertheless", "Consequently", "Notably". 2026 papers shift to "While ..., ..." (V2 16, ARC 11), "In addition", "By contrast", "Together, these ...".
- **Hedges**: "likely", "potentially", "may", "can", "is expected to", "it could be argued that", "approximately", "to our knowledge". Usually one hedge per claim.
- **Favourite verbs and phrases**: "was employed (and extended)", "evaluate", "investigate the influence of", "account for", "is outlined in", "was found to", "is observed", "highlights", "allows for", "enabling", "is governed by", "significant(ly)", "orders of magnitude", "by a factor of", "respectively", "in this work", "the present study", "It should be noted that".
- **Spelling is British**: modelling, behaviour, parameterised, discretisation, stabilisation, optimisation, localised, licence (noun), "centre", "colour". Both "parametrisation" and "parameterisation" occur; pick "parameterisation". Possessive "Sievert's law" in Dark-first papers (IFACE writes "Sieverts' law"; match IFACE for consistency with the companion).
- **Punctuation**: semicolons join a result to its qualifier ("; see Table 3"); colons introduce equations and explanations; "i.e." and "e.g." in brackets. Em dashes are near absent in the older papers. No footnotes (IFACE has two). No rhetorical questions outside IFACE.
- **Abbreviations** are defined at first use in brackets and then used heavily: "breeding blanket (BB)", "Plasma Facing Surface (PFS)", "FPY".
- **Essentially never used**: "we" as the routine subject; first-person singular; "rather than" in NF24 and WCLL (0 each); "novel"; contractions; rhetorical contrasts of the IFACE kind ("LTE here is not inaccurate; it is ill-posed").
- **[conflict] Present in the corpus but banned by `CLAUDE.md`**: "rather than" (V2 6, ARC 5); "leverag-" (ARC 3, V1, V2); "robust" as filler (ARC 6, V2 4); "seamlessly" (V2, ARC); "underscores", "delves", "a testament to" (NF24 Sec. 3.1, V1 intro and conclusion); "closure" (ARC, turbulence sense only). Also the NF24 Sec. 3.1 register ("escalating to a substantial factor of 50", "a nuanced relationship that merits careful consideration") is not the author's normal voice; do not imitate it.

## 8. Lengths and counts, for budgeting

| Paper | Body pages | Figures | Tables | Numbered eqs | Top-level sections |
|---|---|---|---|---|---|
| WCLL (2-col preprint) | 8 | 12 | 5 | 19 | Intro, Methodology (3 subs), Results (2 subs), Conclusion |
| NF24 (2-col journal) | 9 | 8 | 4 | 8 + appendix | Intro, Model parametrisation (5 subs), Impact (2 subs), Conclusion, Appendix |
| ARC (2-col preprint) | 12.5 | 9 | 5 | 5 | Intro, Methodology (3 subs), Results (2 subs), Conclusion |
| WEST (2-col preprint) | 7 + figure pages | 16 | 1 | 5 | Intro, Methodology, Results, Conclusion |
| V2 (wide single col) | 17 | 9 | 0 | 38 | 10 sections, ~17 code listings |
| V1 (2-col journal) | 15 | 16 | symbols list | 52 | 8 sections |
| IFACE (2-col draft) | 15 + 2 appendix | 10 | 2 | 26 + appendices | 7 sections, Discussion has 4 subs |

Approximate word counts: Introduction 400 to 750; Methodology 900 (WCLL) to 1900 (ARC); Results 1300 (NF24), 1900 (WCLL), 3300 (ARC); Conclusion 220 to 550.
Roughly one figure per 0.7 to 1 page and one table per 2 pages in the Dark-first papers; WCLL (8 pages, 12 figures, 5 tables) is the closest size match to the target.

Suggested budget for 6 to 7 pages in `[5p]` (inference from the above, about 4500 to 5500 words): Introduction 450 to 550 (4 paragraphs + reproducibility line); Motivation 300 to 350; Methodology 1000 to 1200 with 8 to 10 equations, one code listing, one verification figure; each application 550 to 700 with 2 figures and at most 1 small table; Discussion 300; Conclusions 250 to 300. Total 7 to 9 figures, 3 to 4 tables.
