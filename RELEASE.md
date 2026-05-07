# Release runbook — pyflare-africa

End-to-end procedure for cutting a tagged PyPI release. Targeted at `v0.1.0` (the PyCon Africa 2026 poster release) but applies to subsequent tags.

> **Distribution name**: `pyflare-africa` (PyPI). **Import name**: `pyflare`.

## 0. Prerequisites (one-time)

- PyPI account: <https://pypi.org/account/register/>
- TestPyPI account (for dry runs): <https://test.pypi.org/account/register/>
- API token for each: Account settings → Add API token → scope to project (after first upload), or "Entire account" for the very first push.
- Tokens stored in `~/.pypirc`:

  ```ini
  [pypi]
    username = __token__
    password = pypi-AgEI...

  [testpypi]
    username = __token__
    password = pypi-AgEI...
  ```

  `chmod 600 ~/.pypirc`. Don't commit.

## 1. Pre-release checklist

```bash
source .venv/bin/activate

# Tests + lint clean.
pytest                                 # expect "55 passed, 1 skipped"
ruff check .                           # expect no errors

# Verify gates relevant to release.
bash scripts/verify.sh G2 G3 G4 G5 G6 G7 G9

# Confirm version is in sync.
grep -E '^version' pyproject.toml      # → 0.1.0
grep -E '__version__' src/pyflare/__init__.py  # → 0.1.0

# CHANGELOG has a dated entry for the version.
grep "## \[0.1.0\]" CHANGELOG.md       # → ## [0.1.0] - 2026-05-XX
```

If the CHANGELOG date is still `2026-05-XX`, update it to today.

## 2. Clean build

```bash
rm -rf dist/ build/
python -m pip install -q --upgrade build twine
python -m build
ls dist/
# expect: pyflare_africa-0.1.0-py3-none-any.whl
#         pyflare_africa-0.1.0.tar.gz
```

## 3. Smoke install in a fresh venv

```bash
SMOKE=/tmp/pyflare_smoke
rm -rf "$SMOKE"
python3.12 -m venv "$SMOKE"
"$SMOKE/bin/pip" install -q dist/pyflare_africa-0.1.0-py3-none-any.whl
"$SMOKE/bin/python" -c "
import pyflare as pf
from pyflare.analysis import volume_to_co2eq
print(pf.__version__)
print(round(volume_to_co2eq(6.48, 0.05), 2), 'MtCO2e')
"
# expect:
#   0.1.0
#   22.62 MtCO2e
```

## 4. Dry-run on TestPyPI (recommended first time)

```bash
twine upload --repository testpypi dist/*
# install from TestPyPI in a fresh venv to confirm metadata renders correctly
"$SMOKE/bin/pip" install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    pyflare-africa==0.1.0
```

Open https://test.pypi.org/project/pyflare-africa/ — confirm the description, links, and classifiers render correctly.

## 5. Production upload

```bash
twine upload dist/*
```

Visit https://pypi.org/project/pyflare-africa/ to confirm the listing.

## 6. Tag and push

```bash
git tag -a v0.1.0 -m "v0.1.0 — PyCon Africa 2026 poster release"
git push origin v0.1.0
```

## 7. GitHub Release

```bash
gh release create v0.1.0 \
    --title "v0.1.0 — PyCon Africa 2026 poster release" \
    --notes-from-tag \
    assets/africa_overview_600dpi.png \
    assets/africa_timelapse.gif \
    dist/pyflare_africa-0.1.0-py3-none-any.whl \
    dist/pyflare_africa-0.1.0.tar.gz
```

## 8. Verify in the wild

```bash
SMOKE=/tmp/pyflare_smoke_v2
rm -rf "$SMOKE"
python3.12 -m venv "$SMOKE"
"$SMOKE/bin/pip" install pyflare-africa==0.1.0
"$SMOKE/bin/python" -c "import pyflare; print(pyflare.__version__)"
```

Then run `bash scripts/verify.sh G10` — should show **PASS** for the local tag.

## 9. Announce

- Tweet / Mastodon / LinkedIn the iconic map + headline number, link to PyPI.
- Update <https://github.com/Jayyp1234/pyflare> README with the release badge state (it already references `pyflare-africa` on PyPI).
- Email Tilo at EOG with the release URL — courtesy follow-up.

---

## Common failures and fixes

| Symptom | Cause | Fix |
|---|---|---|
| `twine upload: HTTPError 403` | First upload of a name needs the upload to come from a verified email account, or a project-scoped token can't create the project | Use an "Entire account"-scoped token for the *very first* upload, then create a project-scoped token afterwards |
| Sphinx build fails on RTD | RTD installs core only by default | Confirm `.readthedocs.yaml` lists `extra_requirements: [docs]` |
| Wheel imports fine but `pip show pyflare` is empty | Confusing the distribution and import names | `pip show pyflare-africa` (distribution) vs `python -c "import pyflare"` (import) |
| Tag points at the wrong commit | Tag was created before the final commit | `git tag -d v0.1.0 && git push origin :refs/tags/v0.1.0` then re-tag and push |
