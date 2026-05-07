# Y2 round 3 — request EOG OAuth Client ID for programmatic access

**Status:** ready to send
**To:** Tilo (whoever replied last; same thread is fine) — `eog@mines.edu` — and CC `victoria.patti@mines.edu` for paper trail
**From:** your UNILAG academic email
**When:** today
**Why:** Tilo confirmed programmatic access is available but requires a Client ID issued by Greg G. ("Greg Gleason" most likely, per the VNF paper authorship). Without it, `pyflare.fetch_vnf_nightly()` cannot authenticate against the new OAuth 2.0 endpoint. Browser/CSV download works without this — but the library, the notebook end-to-end re-execution, and the JOSS paper all need programmatic access.

---

## Suggested subject (reply in same thread)

> Re: Programmatic access — Client ID request for pyflare

## Suggested body

> Hi Tilo,
>
> Thanks again for the quick license turnaround.
>
> Following the docs you linked at https://eogdata.mines.edu/products/vnf/subscribers/, I'd like to request a Client ID and Client Secret so I can authenticate against the OAuth 2.0 endpoint from the pyflare library. The library's `fetch_vnf_nightly()` function will set them via environment variables (`EOG_CLIENT_ID`, `EOG_CLIENT_SECRET`, plus my existing `EOG_USERNAME` / `EOG_PASSWORD`) and pass an access token in the `Authorization: Bearer` header on each download.
>
> Intended use is unchanged from my license application — academic, non-commercial, attribution per §2.a — and pyflare is structured so end users supply their own EOG credentials (no redistribution).
>
> Could you let me know what Greg needs from me to issue the credentials, or loop him in directly?
>
> EOG username: *<your registered username>*
> Pyflare repo (for context): https://github.com/Jayyp1234/pyflare
>
> Best,
> Johnpaul

---

## Pre-send checklist

- [ ] Send as a reply in the existing thread (preserves context for Tilo and any internal forwarding)
- [ ] Fill in your registered EOG username on the placeholder line
- [ ] CC `victoria.patti@mines.edu`
- [ ] If Tilo doesn't reply within 24h, ping with Greg's likely address — no public listing yet, ask Tilo to forward

## After-send actions

- Note send time in [STATUS.md](../STATUS.md) under Y2 round 3
- Once you have Client ID + secret: drop them into your local `.env` (which is in `.gitignore`), set `EOG_CLIENT_ID` and `EOG_CLIENT_SECRET` env vars, and run `pf.fetch_vnf_nightly("2024-08-15", satellite="snpp")` from the venv
- Then swap the synthetic VNF cell in `notebooks/01_niger_delta.ipynb` for the real fetch and re-execute
