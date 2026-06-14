import { motion } from "framer-motion";
import { useEffect, useState } from "react";

// Numbers counting up = cheap dopamine (Section 8). Used for %, ₹, km.
export function CountUp({
  to,
  duration = 1.2,
  decimals = 0,
  prefix = "",
  suffix = "",
}: {
  to: number;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / (duration * 1000));
      const eased = 1 - Math.pow(1 - t, 3);
      setVal(to * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [to, duration]);
  return (
    <span>
      {prefix}
      {val.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })}
      {suffix}
    </span>
  );
}

// Thin radial gauge that animates from 0, always labeled with what it measures.
export function RadialGauge({
  value,
  label,
  color = "#0e9f6e",
  size = 110,
}: {
  value: number; // 0..1
  label: string;
  color?: string;
  size?: number;
}) {
  const r = size / 2 - 8;
  const circ = 2 * Math.PI * r;
  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e2e8f0" strokeWidth={7} />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={7}
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ * (1 - value) }}
          transition={{ duration: 1.3, ease: "easeOut" }}
        />
      </svg>
      <div className="-mt-[72px] text-center" style={{ width: size }}>
        <div className="text-2xl font-bold text-ink">
          <CountUp to={value * 100} decimals={1} suffix="%" />
        </div>
      </div>
      <div className="mt-12 text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  );
}

export function SeverityChip({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    cosmetic: "bg-slate-100 text-slate-600",
    minor: "bg-amber-100 text-amber-700",
    moderate: "bg-orange-100 text-orange-700",
    major: "bg-alert-soft text-alert",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${map[severity] || map.minor}`}>
      {severity}
    </span>
  );
}

export function PrimaryButton({
  children,
  onClick,
  disabled,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full rounded-full border border-[#FCD200] bg-amzn-yellow py-3 text-[15px] font-medium text-[#0F1111] shadow-sm transition hover:bg-amzn-yellowHover active:scale-[0.98] disabled:opacity-40"
    >
      {children}
    </button>
  );
}

// Amazon dark secondary action (squid pill).
export function SecondaryButton({
  children,
  onClick,
  disabled,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full rounded-full bg-amzn-squid py-3 text-[15px] font-medium text-white transition hover:bg-amzn-navy active:scale-[0.98] disabled:opacity-40"
    >
      {children}
    </button>
  );
}

// Streaming status text — makes latency feel like depth (Section 3.4).
export function StreamingStatus({ lines, interval = 700 }: { lines: string[]; interval?: number }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    if (shown >= lines.length) return;
    const t = setTimeout(() => setShown((s) => s + 1), interval);
    return () => clearTimeout(t);
  }, [shown, lines.length, interval]);
  return (
    <div className="space-y-2">
      {lines.slice(0, shown).map((l, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-2 text-sm text-slate-600"
        >
          <span className="text-trust">✓</span>
          {l}
        </motion.div>
      ))}
      {shown < lines.length && (
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-300 border-t-ink" />
          {lines[shown]}
        </div>
      )}
    </div>
  );
}
