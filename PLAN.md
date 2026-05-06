# pyflare — Execution Plan

> 14-day all-out plan from v0.1 scaffold to PyCon Africa 2026 poster submission.
> Today is **2026-05-06**. Deadline is **2026-05-20**.

This document is the single source of truth for what's being built, by whom, and how we know it's working. It lives next to `HANDOFF.md` (the project brief, written before this plan).

If `PLAN.md` and `HANDOFF.md` ever conflict, `PLAN.md` wins until the poster is submitted; afterwards, both should be reconciled.

---

## 1. Critical path

The poster needs these **7 things** working on 2026-05-20:

1. Public GitHub repo, README rendering, CI badge green, v0.1.0 git tag + Release.
2. `pip install pyflare` works from PyPI (or documented fallback name).
3. One peer-reviewable headline number — Niger Delta CO₂-eq for 2024.
4. Iconic Africa-glowing map at 600 dpi (poster centerpiece).
5. 4 country notebooks (Niger Delta, Angola, Algeria, Libya) running end-to-end with synthetic fallback.
6. At least 1 named endorsement in README (Elvidge ideal; SDN or Adeyanju acceptable).
7. 200-word abstract + 2-sentence elevator pitch — **Johnpaul's voice only** — submitted at https://africa.pycon.org/.

Everything else is **nice-to-have for the poster, must-have for v1.0** (Streamlit dashboard, ReadTheDocs, JOSS submission, communities-within-10km map). Cut order if behind: time-lapse → Streamlit → communities-near-sites. Never cut top 6.

---

## 2. Two-track execution

### Johnpaul's track (cannot be delegated)

| ID | Task | Day | Notes |
|---|---|---|---|
| Y1 | Pick GitHub handle, create repo, share URL | 1 | `jayyp1234` confirmed |
| Y2 | Register EOG account at eogdata.mines.edu | 1 | Approval lead time 2-7 days |
| Y3 | Pick PyPI name (`pyflare` or fallback) | 1 | Fallbacks: `africaflare`, `flarescope-africa` |
| Y4 | Send 3 cold emails (Elvidge, SDN, Adeyanju) | 2 | Claude drafts; Johnpaul edits voice + sends |
| Y5 | Write 200-word abstract | 8-12 | **PyCon CFP rule: LLM-written = auto-reject** |
| Y6 | Write 2-sentence elevator pitch | 12 | Same rule |
| Y7 | Internal review by 2+ humans (not LLMs) | 13 | Friends, mentors |
| Y8 | Submit poster proposal | 14 | https://africa.pycon.org/ |
| Y9 | Apply for Opportunity Grant + email team@pycon.africa | 14 | Speaker benefits confirm |

### Claude's track (automated)

| ID | Task | Output |
|---|---|---|
| C1 | Replace `YOUR-HANDLE` placeholders, push v0.1 | Repo live |
| C2 | CI workflow (3.10/3.11/3.12 + ruff) | Green badge |
| C3 | Hygiene files (CoC, CITATION, CHANGELOG, issue/PR templates, pre-commit) | JOSS-ready |
| C4 | `analysis.volume_to_co2eq()` with IPCC AR6 citation + unit test | Headline-number capability |
| C5 | 4 country notebooks with synthetic fallback | Pan-African evidence |
| C6 | Iconic 600-dpi Africa map | Poster centerpiece |
| C7 | `analysis.communities_near_sites()` with synthetic-pop fallback | Second wow-shot |
| C8 | `viz.flare_timelapse()` (5-frame 2012→2025 GIF) | Time-lapse asset |
| C9 | Streamlit MVP + Streamlit Cloud deploy | Live dashboard URL |
| C10 | Sphinx + Furo docs + ReadTheDocs hookup | Docs URL |
| C11 | PyPI v0.1.0 release + GitHub Release with iconic figure attached | `pip install pyflare` |
| C12 | Email drafts (Y4) + JOSS paper draft (post-poster) | Drafts ready |

### Hybrid (Claude drafts, Johnpaul finalizes)

| ID | Task | Reason |
|---|---|---|
| H1 | README origin paragraph | Allowed per CFP, but voice matters |
| H2 | 3 cold-email drafts | Sent from Johnpaul's address |
| H3 | JOSS paper draft (post-poster) | Submitted under Johnpaul's name |

---

## 3. Day-by-day timeline

| Day | Date | Johnpaul | Claude | End-of-day gate |
|---|---|---|---|---|
| 1 | 05-07 | Y1, Y2, Y3 | C1, C2, C3 | **G1**: Repo public, CI green |
| 2 | 05-08 | Y4 | C4 + email drafts | **G2**: CO₂-eq computable |
| 3 | 05-09 | (await replies) | Notebook 1 | **G3**: Niger Delta notebook |
| 4 | 05-10 | (poll EOG) | Notebooks 2 + 3 | **G4**: 3/4 notebooks |
| 5 | 05-11 | (start abstract drafts) | Notebook 4 + iconic map | **G5**: All 4 notebooks + map @ 600 dpi |
| 6 | 05-12 | (abstract iter) | C7 communities-near | **G6**: Second wow-shot |
| 7 | 05-13 | (abstract iter) | C8 timelapse + PyPI prep | **G7**: Timelapse + PyPI dry-run |
| 8 | 05-14 | Y5 v1 | C9 Streamlit | **G8**: Live dashboard URL |
| 9 | 05-15 | Y5 v2 | C10 Sphinx | **G9**: Docs URL |
| 10 | 05-16 | Y5 v3 + endorsement follow-up | C11 PyPI release | **G10**: `pip install` works |
| 11 | 05-17 | Poster design begins | (support) | **G11**: Poster v1 |
| 12 | 05-18 | Y6 + poster v2 | (verification sweep) | **G12**: All systems green |
| 13 | 05-19 | Y7 internal review | (final pass + bugfixes) | **G13**: Reviewer-ready |
| 14 | 05-20 | Y8, Y9 (submit + grant) | (standby) | **G14**: SUBMITTED |

---

## 4. Verification system

### `scripts/verify.sh`

Single command runs every automated check:

```bash
bash scripts/verify.sh           # run all gates G1..G14
bash scripts/verify.sh G1 G2     # run specific gates
```

Output is colored pass / fail / pending. Run it every commit, every end-of-day, every push.

### `STATUS.md`

A living doc updated after each phase. Read it for 30 seconds at end of day; you'll always know where we are.

### Gate definitions

| Gate | Pass condition |
|---|---|
| G1  | Repo public; CI green on `main`; remote configured |
| G2  | `volume_to_co2eq()` ships with citation; unit test passes |
| G3  | `notebooks/01_niger_delta.ipynb` executes cleanly |
| G4  | All 4 notebooks execute without EOG creds |
| G5  | `assets/africa_overview_600dpi.png` ≥ 3000×3000 px |
| G6  | `communities_near_sites()` returns DataFrame |
| G7  | `assets/africa_timelapse.gif` has 5+ frames |
| G8  | Streamlit Cloud URL returns 200 + Nigeria trend renders |
| G9  | RTD or docs URL returns 200 |
| G10 | `pip install pyflare` from clean venv works |
| G11 | Poster PDF: A1 portrait, 300 dpi |
| G12 | All 11 prior gates green |
| G13 | 2+ humans confirm abstract reads as Johnpaul's voice |
| G14 | PyCon submission confirmation email received |

### Strategic reviews (Days 5, 9, 12)

Beyond pass / fail, on these days we ask:

- Is the headline number defensible if a NOAA scientist reviews it? Re-run with alternate slip fractions to bound the answer.
- Does the iconic map photograph well at A1 print size? Render a 50% crop, check pixel density.
- Does the abstract open with the **NUMBER**, not the project name? Reviewers skim — numbers stick.
- Are there LLM tells in the README origin paragraph? Grep for "delve", "tapestry", em-dash overuse, "furthermore", "moreover".
- Does the repo signal **active community** (open issues, "Country maintainer wanted", labelled `good-first-issue`)?

---

## 5. Risk register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| EOG account approval > 7 days | Med | High | Synthetic fallback in all notebooks |
| `pyflare` taken on PyPI | Med | Med | Day 1 check; fallbacks: `africaflare`, `flarescope-africa` |
| Elvidge doesn't reply | Med | Med | 3 targets in parallel; SDN + Adeyanju acceptable |
| WorldPop raster too heavy | High | Low | Synthetic test data; document integration path |
| Streamlit Cloud flaky | Low | Low | Local screenshot acceptable for poster |
| 14 days insufficient | Low-Med | High | Cut order: timelapse → Streamlit → communities. Never cut top 6 |
| Abstract reads "AI-generated" | Med | **Catastrophic** | Day 13 human review; LLM-tell grep on Day 12 |
| `pip install` fails on user machine | Med | High | Day 10 install test on clean venv |

---

## 6. Second-order moves

These are moves that 99% of submissions miss. They compound.

1. **Pre-register the iconic map** on social on Day 7 with the headline number — familiarity → trust by submission.
2. **GitHub Release with attached PNG** — looks shipped, not WIP.
3. **`good-first-issue` open issues per African country** — repo signals active community before any contributors arrive.
4. **Bidirectional Elvidge citation** — once he replies, ask if his lab's project page can link `pyflare`.
5. **arXiv pre-print of JOSS paper** by Day 12 — stable URL, no peer-review wait.
6. **Live dashboard URL on poster** — `pyflare.streamlit.app` Day 8.
7. **Open the abstract with the NUMBER**, not the project name. Reviewers skim — numbers stick.
8. **Use "African oil-producing nations" 3+ times** in the abstract.
9. **Pre-empt 1-2 likely reviewer concerns** in the abstract.
10. **Print project palette swatches on poster** — signals craft.
11. **PyPI release on Day 10**, not Day 14 — older listing photographs better.
12. **"Citing this work" anchor at top of README** — reviewers Cmd-F "cite".

---

## 7. How to use this document

- **Daily check**: `bash scripts/verify.sh` then read updated `STATUS.md`.
- **End of phase**: review the gate criteria; update STATUS.
- **Risk changes**: update §5 risk register inline.
- **Cut decisions**: if a gate fails and the risk is high-impact, consult cut order in §1.

Plan owner: Johnpaul Okeke. Plan executor: Claude Code session.
