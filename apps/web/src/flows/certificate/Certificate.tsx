import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { QRCodeSVG } from "qrcode.react";
import { api, GradeResult } from "../../lib/api";
import { CountUp, SeverityChip, StreamingStatus, PrimaryButton } from "../../components/ui";

const GRADE_COLOR: Record<string, string> = {
  A: "#0e9f6e",
  B: "#0e9f6e",
  C: "#d97706",
  D: "#e02424",
};

export default function Certificate({
  sessionId,
  fraudMode,
  identityConfidence,
  onGraded,
  onNext,
}: {
  sessionId: string;
  fraudMode: boolean;
  identityConfidence: number;
  onGraded: (g: GradeResult) => void;
  onNext: () => void;
}) {
  const [result, setResult] = useState<GradeResult | null>(null);
  const [phase, setPhase] = useState<"analyzing" | "defects" | "certificate">("analyzing");
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return; // grade exactly once (avoid StrictMode double-call)
    started.current = true;
    let active = true;
    (async () => {
      const g = await api.grade(sessionId, fraudMode);
      await new Promise((r) => setTimeout(r, 2400));
      if (!active) return;
      setResult(g);
      onGraded(g);
      setPhase("defects");
      setTimeout(() => active && setPhase("certificate"), 2600);
    })();
    return () => {
      active = false;
    };
  }, [sessionId, fraudMode]);

  if (phase === "analyzing") {
    return (
      <div className="min-h-[760px] bg-white px-6 pt-20">
        <div className="text-xs uppercase tracking-widest text-trust">Condition inspection</div>
        <h2 className="mt-2 text-xl font-bold text-ink">Inspecting 8 angles…</h2>
        <div className="mt-8">
          <StreamingStatus
            lines={[
              "Anchoring against catalog (new) condition",
              "Scanning 14 defect classes",
              "Measuring scuffs, scratches, wear",
              "Applying the grading rubric",
            ]}
          />
        </div>
      </div>
    );
  }

  if (!result) return null;

  if (phase === "defects") {
    return (
      <div className="min-h-[760px] bg-white px-6 pt-16">
        <div className="text-xs uppercase tracking-widest text-trust">Defects detected</div>
        <div className="relative mx-auto mt-4 grid h-48 w-48 place-items-center rounded-2xl bg-slate-100 text-6xl">
          🎧
          {result.defects.map((d, i) => (
            <motion.div
              key={i}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4 + i * 0.4 }}
              className="absolute h-6 w-6 rounded-full border-2 border-alert bg-alert/20"
              style={{ top: `${20 + i * 26}%`, left: `${30 + i * 14}%` }}
            />
          ))}
        </div>
        <div className="mt-6 space-y-2">
          {result.defects.length === 0 && (
            <div className="rounded-xl bg-trust-soft p-3 text-sm text-trust-dark">
              No defects detected. Pristine condition.
            </div>
          )}
          {result.defects.map((d, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + i * 0.4 }}
              className="flex items-center justify-between rounded-xl border border-slate-100 p-3"
            >
              <div>
                <div className="text-sm font-semibold capitalize text-ink">
                  {d.type} · {d.location}
                </div>
                <div className="text-xs text-slate-500">
                  {d.size_cm ? `~${d.size_cm} cm · ` : ""}
                  {d.affects_function ? "affects function" : "cosmetic only"} ·{" "}
                  {(d.confidence * 100).toFixed(0)}% conf
                </div>
              </div>
              <SeverityChip severity={d.severity} />
            </motion.div>
          ))}
        </div>
      </div>
    );
  }

  // ---- the certificate slab (mint with sheen) ----
  const color = GRADE_COLOR[result.grade];
  return (
    <div className="min-h-[760px] bg-white px-5 pb-8 pt-12">
      <motion.div
        initial={{ scale: 0.9, opacity: 0, rotateX: 20 }}
        animate={{ scale: 1, opacity: 1, rotateX: 0 }}
        transition={{ type: "spring", stiffness: 120, damping: 14 }}
        className="guilloche relative overflow-hidden rounded-3xl border border-slate-200 p-5 shadow-xl"
      >
        {/* sheen */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -inset-y-4 left-0 w-1/3 rotate-12 animate-sheen bg-gradient-to-r from-transparent via-white/60 to-transparent" />
        </div>

        <div className="flex items-center justify-between">
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
            RELAY Trust Certificate
          </div>
          <div className="rounded-md bg-trust-soft px-2 py-0.5 text-[10px] font-bold text-trust-dark">
            FRAUD SCREEN PASSED
          </div>
        </div>

        <div className="mt-4 flex items-center gap-4">
          <div
            className="grid h-24 w-24 place-items-center rounded-2xl text-5xl font-extrabold text-white"
            style={{ background: color }}
          >
            {result.grade}
          </div>
          <div className="flex-1">
            <div className="text-xs text-slate-500">Condition grade</div>
            <div className="text-lg font-bold text-ink">
              Score <CountUp to={result.score} />/100
            </div>
            <div className="text-xs text-slate-500">
              {(result.confidence * 100).toFixed(0)}% confidence
            </div>
          </div>
          {/* real, scannable QR → public verification target */}
          <div className="rounded-lg bg-white p-1 ring-1 ring-slate-200">
            <QRCodeSVG
              value={`https://relay.trust/verify/${result.certificate_id}`}
              size={56}
              level="M"
              bgColor="#ffffff"
              fgColor="#0b1220"
            />
          </div>
        </div>

        {/* microtext strip — grading-slab detail */}
        <div className="mt-3 overflow-hidden whitespace-nowrap text-[6px] uppercase tracking-[0.2em] text-slate-300">
          {`RELAY·TRUST·LAYER·VERIFIED·${result.certificate_id}·`.repeat(6)}
        </div>

        <p className="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-relaxed text-slate-600">
          {result.rationale}
        </p>

        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <Stat label="Identity" value={`${(identityConfidence * 100).toFixed(0)}%`} />
          <Stat label="Defects" value={`${result.defects.length}`} />
          <Stat label="Cert ID" value={result.certificate_id} small />
        </div>

        <div className="mt-3 flex items-center justify-between border-t border-dashed border-slate-200 pt-2 text-[9px] uppercase tracking-wider text-slate-400">
          <span>Issued {new Date().toLocaleDateString()} · RELAY Trust Layer</span>
          <span>Scan to verify ↗</span>
        </div>
      </motion.div>

      {/* pricing */}
      <div className="mt-5 rounded-2xl border border-slate-100 p-4">
        <div className="flex items-end justify-between">
          <div>
            <div className="text-xs text-slate-500">Resale value</div>
            <div className="text-2xl font-extrabold text-ink">
              ₹<CountUp to={result.price.resale_value} />
            </div>
            <div className="text-xs text-trust-dark">{result.price.pct_of_new}% of new price</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-500">Instant refund</div>
            <div className="text-lg font-bold text-ink">
              ₹{result.price.instant_refund.toLocaleString()}
            </div>
          </div>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">{result.price.rationale}</p>
      </div>

      <div className="mt-6">
        <PrimaryButton onClick={onNext}>Find a buyer nearby</PrimaryButton>
      </div>
    </div>
  );
}

function Stat({ label, value, small }: { label: string; value: string; small?: boolean }) {
  return (
    <div className="rounded-xl bg-slate-50 py-2">
      <div className={`font-bold text-ink ${small ? "text-[11px]" : "text-sm"}`}>{value}</div>
      <div className="text-[9px] uppercase tracking-wide text-slate-400">{label}</div>
    </div>
  );
}
