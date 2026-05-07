import Image from "next/image";
import Link from "next/link";

import ggfrData from "@/lib/data/ggfr.json";
import countriesData from "@/lib/data/countries.json";
import exposureData from "@/lib/data/exposure.json";

import { HeroNumber } from "@/components/HeroNumber";
import { SectionLabel } from "@/components/SectionLabel";
import { CountryCard } from "@/components/CountryCard";


// ---------------------------------------------------------------------------
// Headline maths — done at build time so the page is a single static document
// ---------------------------------------------------------------------------

const SLIP = 0.05; // pyflare default / Plant et al. 2022 mid

// Combustion EF + GWP100 from pyflare.analysis. Inlined here so the frontend
// has no Python dependency at runtime.
const CO2_PER_M3_GAS_KG = 2.55;
const METHANE_GWP100 = 29.8;
const METHANE_DENSITY = 0.717;

function bcmToMtCO2e(bcmFlared: number, slip: number): number {
  const m3 = bcmFlared * 1e9;
  const burned = m3 * (1 - slip);
  const slipped = m3 * slip;
  const combustionKg = burned * CO2_PER_M3_GAS_KG;
  const methaneKg = slipped * METHANE_DENSITY;
  const methaneCo2eKg = methaneKg * METHANE_GWP100;
  return (combustionKg + methaneCo2eKg) / 1e9; // kg → Mt
}

const continentBcm = ggfrData.continent_total_bcm_latest;
const continentCo2e = bcmToMtCO2e(continentBcm, SLIP);
const latestYear = ggfrData.latest_year;

// Index countries metadata by name for fast lookup.
const countriesByName = Object.fromEntries(
  countriesData.map((c) => [c.country, c]),
);

const top5 = ggfrData.top5_latest;
const allByCountry = Object.fromEntries(
  ggfrData.by_country.map((c) => [c.country, c.series]),
);

// Niger Delta exposure as the headline public-health number.
const nigeriaExposure10km =
  exposureData.Nigeria.exposure_by_radius_km["10"].total_population_exposed;
const nigeriaExposure25km =
  exposureData.Nigeria.exposure_by_radius_km["25"].total_population_exposed;


// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function Home() {
  return (
    <main className="flex-1">

      {/* ---------- HERO ---------- */}
      <section className="relative min-h-[100svh] flex flex-col items-center justify-center overflow-hidden pyflare-hero-bg px-6">
        <Image
          src="/africa-overview.png"
          alt="Africa with synthesised flare-site glow points highlighting Nigeria, Algeria, Libya, and Angola"
          fill
          priority
          className="object-cover opacity-40"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/85 pointer-events-none" />

        <div className="relative z-10 flex flex-col items-center text-center max-w-4xl">
          <SectionLabel className="pyflare-pulse">
            African gas flaring &middot; {latestYear}
          </SectionLabel>

          <h1 className="font-bold leading-none tracking-tight mb-6 text-[--color-flare-core]">
            <span className="block text-[clamp(5rem,18vw,12rem)]">
              <HeroNumber value={continentCo2e} decimals={0} />
            </span>
            <span className="block text-2xl md:text-3xl text-[--color-text] font-medium mt-2 tracking-normal">
              megatonnes CO₂-equivalent / year
            </span>
          </h1>

          <p className="text-base md:text-lg text-[--color-muted] max-w-2xl leading-relaxed">
            <span className="text-[--color-text] font-semibold">
              {continentBcm.toFixed(1)} billion cubic metres
            </span>{" "}
            of gas burned off in {latestYear} across {top5.length}+ African
            oil-producing nations — measured by satellite, computed with open
            code, citable from your IDE.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-3 text-sm">
            <a
              href="https://github.com/Jayyp1234/pyflare"
              className="inline-flex items-center gap-2 rounded-full border border-[--color-flare-core] px-5 py-2 text-[--color-flare-core] hover:bg-[--color-flare-core] hover:text-black transition"
            >
              View on GitHub
            </a>
            <a
              href="#headline"
              className="inline-flex items-center gap-2 rounded-full border border-[--color-border-soft] px-5 py-2 text-[--color-muted] hover:text-[--color-text] hover:border-[--color-flare-core] transition"
            >
              Show me the number
            </a>
          </div>

          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-xs text-[--color-muted]/70">
            Source: VIIRS Nightfire, Colorado School of Mines &middot; Boundaries: Natural Earth
          </div>
        </div>
      </section>

      {/* ---------- WHY THIS NUMBER ---------- */}
      <section
        id="headline"
        className="max-w-5xl mx-auto px-6 py-24 md:py-32"
      >
        <SectionLabel>The two frames that compound</SectionLabel>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-8">
          A climate number and a public-health number, from one library.
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-[--color-bg-warm] border border-[--color-border-soft] rounded-2xl p-8">
            <SectionLabel>Climate frame &middot; Nigeria 2024</SectionLabel>
            <div className="text-6xl font-bold text-[--color-flare-core] pyflare-glow">
              {bcmToMtCO2e(allByCountry.Nigeria.at(-1)?.bcm ?? 0, 0.02).toFixed(0)}
              –
              {bcmToMtCO2e(allByCountry.Nigeria.at(-1)?.bcm ?? 0, 0.09).toFixed(0)}
            </div>
            <div className="text-lg mt-1">MtCO₂e / year</div>
            <p className="text-sm text-[--color-muted] mt-4 leading-relaxed">
              Range driven by the methane-slip assumption — IPCC AR6
              conservative (2 %) versus recent satellite-derived basin
              estimates (Plant et al. 2022, 5–9 %). The spread is itself
              the argument for satellite measurement.
            </p>
          </div>

          <div className="bg-[--color-bg-warm] border border-[--color-border-soft] rounded-2xl p-8">
            <SectionLabel>Public-health frame &middot; Niger Delta</SectionLabel>
            <div className="text-6xl font-bold text-[--color-flare-core] pyflare-glow">
              {(nigeriaExposure10km / 1000).toFixed(0)}k
              <span className="text-3xl text-[--color-muted]"> – </span>
              {(nigeriaExposure25km / 1e6).toFixed(1)}M
            </div>
            <div className="text-lg mt-1">people exposed</div>
            <p className="text-sm text-[--color-muted] mt-4 leading-relaxed">
              <span className="text-[--color-text] font-semibold">
                {nigeriaExposure10km.toLocaleString()}
              </span>{" "}
              within 10 km of a major Niger Delta flare facility;{" "}
              <span className="text-[--color-text] font-semibold">
                {nigeriaExposure25km.toLocaleString()}
              </span>{" "}
              within 25 km. Synthetic facility list × curated settlement
              reference; v0.2 swaps to WorldPop.
            </p>
          </div>
        </div>
      </section>

      {/* ---------- TOP 5 PRODUCERS ---------- */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <SectionLabel>Top 5 producers &middot; {latestYear}</SectionLabel>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-10">
          Where {latestYear}&apos;s flaring is concentrated.
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {top5.map((c, i) => {
            const meta = countriesByName[c.country];
            const isPriority = meta?.is_priority ?? false;
            const exposure10 = isPriority
              ? exposureData[c.country as keyof typeof exposureData]
                  ?.exposure_by_radius_km?.["10"]?.total_population_exposed
              : undefined;
            return (
              <CountryCard
                key={c.country}
                country={c.country}
                bcm={c.bcm}
                rank={i + 1}
                narrative={meta?.narrative ?? undefined}
                isPriority={isPriority}
                exposureAt10km={exposure10}
              />
            );
          })}
        </div>
      </section>

      {/* ---------- TIMELAPSE ---------- */}
      <section className="max-w-5xl mx-auto px-6 py-24">
        <SectionLabel>2012 → {latestYear}</SectionLabel>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
          How African flaring has shifted in 12 years.
        </h2>
        <p className="text-[--color-muted] mb-10 max-w-3xl leading-relaxed">
          Per-country dot brightness scales with that year&apos;s GFMR-published
          flared volume, normalised to the African producer maximum across the
          dataset. Libya&apos;s 2015 dip is the civil-war disruption; Nigeria&apos;s
          steady descent is gas-flaring reduction policy biting.
        </p>
        {/* Use plain <img> so the GIF animates — next/image disables animation by default */}
        <img
          src="/africa-timelapse.gif"
          alt="Animated African gas flaring intensity, 5 keyframes from 2012 to 2024"
          className="w-full rounded-xl border border-[--color-border-soft] shadow-2xl"
        />
      </section>

      {/* ---------- CTA ---------- */}
      <section className="max-w-4xl mx-auto px-6 py-24 text-center">
        <SectionLabel>Open methodology, open code, open data</SectionLabel>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-6">
          Reproduce every number on this page in two lines.
        </h2>
        <pre className="bg-[--color-bg-elev] border border-[--color-border-soft] rounded-xl p-6 text-left text-sm font-mono text-[--color-text] overflow-x-auto inline-block mx-auto">
          <code>{`pip install pyflare-africa
python -c "import pyflare as pf; print(pf.fetch_ggfr_annual().tail())"`}</code>
        </pre>
        <p className="text-sm text-[--color-muted] mt-8">
          Pyflare is MIT-licensed.{" "}
          <a
            href="https://github.com/Jayyp1234/pyflare/blob/main/LICENSING_NOTES.md"
            className="text-[--color-flare-core] hover:underline"
          >
            VNF data attribution and license terms
          </a>{" "}
          apply when fetching real VIIRS Nightfire detections.
        </p>
      </section>

      {/* ---------- FOOTER ---------- */}
      <footer className="border-t border-[--color-border] mt-12 py-10 px-6 text-center text-xs text-[--color-muted]">
        <div className="max-w-4xl mx-auto space-y-2">
          <div>
            This product was made utilizing VIIRS Nightfire (VNF) nightly data
            produced by the Earth Observation Group, Payne Institute for
            Public Policy, Colorado School of Mines.
          </div>
          <div>
            Boundaries: Natural Earth &middot; Annual volumes: World Bank
            Global Flaring and Methane Reduction Partnership (formerly
            Global Gas Flaring Reduction Partnership).
          </div>
          <div className="pt-3">
            <a
              href="https://github.com/Jayyp1234/pyflare"
              className="text-[--color-flare-core] hover:underline mr-4"
            >
              GitHub
            </a>
            <Link
              href="/about"
              className="text-[--color-flare-core] hover:underline"
            >
              About this dashboard
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
