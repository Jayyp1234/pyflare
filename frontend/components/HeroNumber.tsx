"use client";

import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect } from "react";

interface HeroNumberProps {
  value: number;
  decimals?: number;
  duration?: number;
  className?: string;
}

/**
 * Animated counter that ticks from 0 → value when it scrolls into view.
 * Used for the hero CO₂e number; can be reused for any large headline.
 */
export function HeroNumber({
  value,
  decimals = 0,
  duration = 1.6,
  className = "",
}: HeroNumberProps) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => latest.toFixed(decimals));

  useEffect(() => {
    const controls = animate(count, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
    });
    return () => controls.stop();
  }, [value, duration, count]);

  return (
    <motion.span
      className={`inline-block tabular-nums pyflare-glow ${className}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <motion.span>{rounded}</motion.span>
    </motion.span>
  );
}
