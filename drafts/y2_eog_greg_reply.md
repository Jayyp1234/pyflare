# Y2 round 4 — reply to Greg Gleason on attribution + naming + license

**Status:** ready to send
**To:** `gregory.gleason@mines.edu`, with `eog@mines.edu` and `victoria.patti@mines.edu` on CC (continue the existing thread)
**From:** your UNILAG academic email
**When:** today
**Why this matters:** Greg flagged three substantive issues. Confirming the corrections in writing — and pointing him at specific commits — is the cleanest way to close the loop and keep the academic license relationship in good standing.

---

## Suggested subject

> Re: pyflare repository — VNF attribution, GFMR naming, and license restrictions

## Suggested body

> Hi Greg,
>
> Thanks for the careful read — all three points are well taken, and I've made the corrections across the repo, the docs, the four country notebooks, the Streamlit dashboard, and the new Next.js frontend I'm prototyping. Specifically:
>
> 1. **VNF attribution**: every previous "NOAA's VIIRS Nightfire" / "NOAA EOG" reference is now corrected. VNF is consistently attributed to "the Earth Observation Group (EOG) at the Payne Institute for Public Policy, Colorado School of Mines," with the VIIRS instrument noted separately as the source of underlying observations on Suomi NPP / JPSS-1. The §2.a verbatim notice is in the README, in every notebook header, in the iconic Africa map figure footer, and in the Next.js frontend footer.
>
> 2. **GFMR naming**: I've renamed `pyflare.fetch_ggfr_annual()` → `pyflare.fetch_gfmr_annual()` and updated all human-facing prose to "World Bank Global Flaring and Methane Reduction Partnership (GFMR; formerly Global Gas Flaring Reduction / GGFR)." The old name remains as a deprecated alias for v0.1 / v0.2 so that any existing notebooks keep running, with removal planned for v0.3.
>
> 3. **License §1.b restrictions**: pyflare does not (and will not) bundle, mirror, redistribute, or rehost VNF data. I've added an explicit "pyflare does not redistribute" statement up front in the README, in `LICENSING_NOTES.md`, in the `pyflare.data` module docstring, and in the `fetch_vnf_nightly()` function docstring. The library is a thin client only; every pyflare user must hold their own VNF Academic Data Use License from EOG. None of the test fixtures, notebook synthetic blocks, dashboard caches, or frontend static JSON files contain real VNF rows.
>
> If you'd like to verify any of the above directly, the relevant files in the repo are:
>
> - `LICENSING_NOTES.md` — developer-facing checklist mapped to each restriction
> - `README.md` — top-level acknowledgements + non-redistribution statement
> - `src/pyflare/data.py` — module docstring + `fetch_vnf_nightly()` docstring
> - `src/pyflare/__init__.py` — package docstring
> - `notebooks/01_niger_delta.ipynb` (and the three sister notebooks) — attribution cell at the top of each
>
> Happy to walk you through any of this on a short call, or send a tagged release archive once v0.1.0 is on PyPI.
>
> Thanks again for the careful review.
>
> Best,
> Johnpaul Okeke
> University of Lagos
> okekejohnpaul12@gmail.com

---

## Voice tells to scrub

- ✗ "I appreciate your feedback" / "your valuable input" — too thanksgiving
- ✗ "delve into", "leverage", "ecosystem"
- ✗ Five em-dashes in one paragraph
- ✓ Specific file paths Greg can verify against — already in there

## Pre-send checklist

- [ ] Push the corrections to GitHub before sending so the file paths in the email actually resolve
- [ ] Confirm `git log --oneline | head -5` shows the rename commit
- [ ] Send as a reply in the existing eog@mines.edu thread

## After-send actions

- Note send time in [STATUS.md](../STATUS.md)
- If Greg asks for a tagged release archive, follow [RELEASE.md](../RELEASE.md) — that's exactly what it covers
