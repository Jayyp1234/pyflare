import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "pyflare — African gas flaring, by satellite",
  description:
    "Open-source Python toolkit + dashboard for satellite-based gas flaring " +
    "analytics across African oil-producing nations. Built around the VIIRS " +
    "Nightfire (VNF) product from EOG at the Colorado School of Mines and " +
    "the World Bank's Global Flaring and Methane Reduction Partnership (GFMR).",
  metadataBase: new URL("https://pyflare.dev"),
  openGraph: {
    title: "pyflare — African gas flaring, by satellite",
    description:
      "Roughly 30 megatonnes of CO₂-equivalent emissions per year across 17 African " +
      "oil-producing nations. Open methodology, open code, open data.",
    images: ["/africa-overview.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[--color-bg] text-[--color-text]">
        {children}
      </body>
    </html>
  );
}
