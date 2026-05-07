# Y2 follow-up — "How do you plan to use the data?"

**Status:** ready to use
**Where this goes:** the use-description section of the academic license PDF (`VNF_academic_license_agreement_20260130.pdf`). Same text also works as a short follow-up to Tilo if he asks separately.
**Why it matters:** this is the substantive part of the academic license review — vague answers slow turnaround, specific answers speed it up. Naming concrete outputs (poster, JOSS paper, Zenodo deposit) signals "real academic project," not "let me grab a dataset."

---

## Suggested text

> Pyflare is an open-source Python toolkit (MIT-licensed, https://github.com/Jayyp1234/pyflare) for satellite-based gas flaring analytics across African oil- and gas-producing nations. I'm developing it through the University of Lagos as the technical centerpiece of three intended academic outputs:
>
> 1. **PyCon Africa 2026 poster** (deadline 2026-05-20). A Niger Delta case study using nightly VNF detections to demonstrate flare/wildfire classification (Elvidge et al. 2013), persistence-based site clustering, and the radiant-heat → flared-volume regression (Elvidge et al. 2016) — combined with World Bank GFMR annual estimates to produce a CO₂-equivalent headline figure for Nigerian flaring in 2024.
>
> 2. **JOSS methods paper**, target submission July 2026. Documents the pyflare implementation, the unit-test suite (currently 41 tests, all passing), and the validation of the implementation against published reference values.
>
> 3. **AFLARED derived dataset**, target Zenodo deposit + DOI late 2026. A harmonised African flaring estimates record (2012–present) at flare-site / monthly resolution. Per-detection VNF data will not be redistributed — AFLARED is a derived product citing VNF as the upstream source of record.
>
> All use is academic and non-commercial. Pyflare's documentation explicitly directs users to register with EOG for raw VNF access; the toolkit handles analytics, EOG remains the data of record. I'm happy to share the v0.1 codebase, test suite, or any specific implementation details during the license review.

---

## Voice tells to scrub

- ✗ "primary purpose", "leverage", "ecosystem"
- ✗ Three em-dashes in one paragraph
- ✓ Specifics they can verify (test count, target dates, GitHub URL, your institution)

---

## Tilo's three steps — checklist for you

- [ ] **Register** at https://eogdata.mines.edu/products/register/ using a `@unilag.edu.ng` (or other UNILAG) academic email — gmail will probably be rejected. If you don't have a UNILAG email, ask the IT helpdesk for one before registering.
- [ ] **Download + sign** the license PDF: https://payneinstitute.mines.edu/wp-content/uploads/sites/149/2026/01/VNF_academic_license_agreement_20260130.pdf — fill in the use-description section using the text above (verbatim or edited for voice).
- [ ] **Attach proof of enrollment** — University ID (front, scanned or photographed) is the path of least resistance. Alternatives: enrollment letter, student/staff card, or a payslip if you're staff.
- [ ] **Reply to Tilo** with the signed PDF + ID image as attachments. Bcc: yourself for paper trail.

## After you send

- Note send time in [STATUS.md](../STATUS.md) under Y2.
- Polite ping at Day 4 (2026-05-10) if no follow-up.
- Once approved, you'll get EOG credentials → set `EOG_USERNAME` / `EOG_PASSWORD` env vars → swap the synthetic VNF cell in `notebooks/01_niger_delta.ipynb` for the real `pf.fetch_vnf_nightly()` call.
