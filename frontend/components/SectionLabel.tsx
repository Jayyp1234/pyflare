interface SectionLabelProps {
  children: React.ReactNode;
  className?: string;
}

export function SectionLabel({ children, className = "" }: SectionLabelProps) {
  return (
    <div
      className={`text-[--color-flare-core] uppercase text-xs tracking-[0.18em] font-semibold mb-3 ${className}`}
    >
      {children}
    </div>
  );
}
