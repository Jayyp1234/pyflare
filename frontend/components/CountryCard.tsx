"use client";

import { motion } from "framer-motion";

interface CountryCardProps {
  country: string;
  bcm: number;
  rank?: number;
  narrative?: string;
  isPriority?: boolean;
  exposureAt10km?: number;
}

export function CountryCard({
  country,
  bcm,
  rank,
  narrative,
  isPriority,
  exposureAt10km,
}: CountryCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="relative bg-[--color-bg-warm] border border-[--color-border-soft] rounded-2xl p-6 h-full"
    >
      <div className="flex items-baseline justify-between mb-2">
        <h3 className="text-xl font-semibold text-[--color-text]">{country}</h3>
        {rank && (
          <span className="text-xs font-mono text-[--color-muted]">
            #{rank} {rank === 1 ? "🏴" : ""}
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-2 mb-4">
        <span className="text-4xl font-bold text-[--color-flare-core] tabular-nums">
          {bcm.toFixed(2)}
        </span>
        <span className="text-sm text-[--color-muted]">bcm flared, 2024</span>
      </div>
      {narrative && (
        <p className="text-sm text-[--color-muted] leading-relaxed mb-3">
          {narrative}
        </p>
      )}
      {isPriority && exposureAt10km !== undefined && (
        <div className="text-xs text-[--color-muted] mt-4 pt-4 border-t border-[--color-border]">
          <span className="text-[--color-flare-core] font-mono">
            {exposureAt10km.toLocaleString()}
          </span>{" "}
          people within 10 km of major flare facilities (synthetic exposure)
        </div>
      )}
    </motion.div>
  );
}
