# pyflare execution status

> Living log. Updated at end of each phase. For the full plan see [`PLAN.md`](PLAN.md).

**Last updated:** 2026-05-06 (Day 0, evening)
**Current phase:** Day 0 — Foundation
**Days to PyCon Africa deadline:** 14
**Submission target date:** 2026-05-20

---

## Day 0 (2026-05-06) — Foundation

### Landed today

- [x] Strategic plan written ([`PLAN.md`](PLAN.md))
- [x] Verification system designed ([`scripts/verify.sh`](scripts/verify.sh))
- [x] Project hygiene scaffolded:
  - [x] `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1, contact set to okekejohnpaul12@gmail.com)
  - [x] `CITATION.cff` (machine-citable, points to v0.1.0 / 2026-05-16)
  - [x] `CHANGELOG.md` (Keep-a-Changelog format, [0.1.0] entry drafted)
  - [x] `.github/workflows/ci.yml` (matrix on 3.10/3.11/3.12 + ruff)
  - [x] `.github/ISSUE_TEMPLATE/{bug_report,feature_request,country_maintainer}.md`
  - [x] `.github/PULL_REQUEST_TEMPLATE.md`
  - [x] `.pre-commit-config.yaml` (ruff, mypy, standard hygiene hooks)
- [x] `YOUR-HANDLE` placeholders replaced with `jayyp1234` in `README.md`, `CONTRIBUTING.md`
- [x] `pyproject.toml` URLs harmonized to `jayyp1234` (was `jpokekeebube`)

### Not yet committed

All Day 0 work is on disk but uncommitted. Commit + push are part of Y1 (user does deployment).

Suggested commit:

```bash
git add .github CODE_OF_CONDUCT.md CITATION.cff CHANGELOG.md .pre-commit-config.yaml \
        PLAN.md STATUS.md scripts/verify.sh README.md CONTRIBUTING.md pyproject.toml
git commit -m "Day 0: hygiene scaffold + plan + verify.sh"
```

### Blockers (must clear before Day 1 push)

- [ ] **Y1**: GitHub repo URL — user creates empty repo at https://github.com/new and adds remote
- [ ] **Y2**: EOG account registration at https://eogdata.mines.edu/ (lead time 2-7 days)
- [ ] **Y3**: confirm `pyflare` available on PyPI (or pick fallback)

### Tomorrow (Day 1, 2026-05-07): Gate G1

- AM: Y1 (repo URL) → `git remote add origin <url>` → `git push -u origin main`
- AM: Y2 EOG registration starts
- PM: `bash scripts/verify.sh G1` → expect green
- PM: C4 (CO₂-eq function) prep + Y4 cold-email drafts

### Risk register changes

None today.

### Cut-order reminder

If we slip: drop time-lapse → Streamlit → communities-near-sites. Never cut: CO₂-eq function, country notebooks, iconic map, PyPI release.
