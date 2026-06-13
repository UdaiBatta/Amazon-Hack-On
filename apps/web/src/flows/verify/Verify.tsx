import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api, VerifyResult } from "../../lib/api";
import { CountUp, StreamingStatus, PrimaryButton } from "../../components/ui";

export default function Verify({
  sessionId,
  fraudMode,
  onPass,
  onRestart,
}: {
  sessionId: string;
  fraudMode: boolean;
  onPass: (v: VerifyResult) => void;
  onRestart: () => void;
}) {
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [analyzing, setAnalyzing] = useState(true);

  useEffect(() => {
    let active = true;
    const run = async () => {
      const v = await api.verify(sessionId, fraudMode);
      // latency theater: let the status lines breathe
      await new Promise((r) => setTimeout(r, 2600));
      if (!active) return;
      setResult(v);
      setAnalyzing(false);
    };
    run();
    return () => {
      active = false;
    };
  }, [sessionId, fraudMode]);

  if (analyzing) {
    return (
      <div className="min-h-[760px] bg-white px-6 pt-20">
        <div className="text-xs uppercase tracking-widest text-trust">Fingerprint check</div>
        <h2 className="mt-2 text-xl font-bold text-ink">
          Verifying this is the exact unit we delivered…
        </h2>
        <div className="mt-8">
          <StreamingStatus
            lines={[
              "Loading delivery-day fingerprint (birth certificate)",
              "Comparing multimodal embeddings",
              "Matching perceptual hash across 6 views",
              "Reading serial number under the left earcup",
            ]}
          />
        </div>
        <div className="mt-10 flex items-center justify-center gap-3">
          <div className="h-28 w-28 rounded-2xl bg-slate-200" />
          <motion.div
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ repeat: Infinity, duration: 1.4 }}
            className="text-2xl text-slate-400"
          >
            ⇌
          </motion.div>
          <div className="h-28 w-28 rounded-2xl bg-slate-200" />
        </div>
      </div>
    );
  }

  if (!result) return null;

  // ---- FRAUD INTERRUPT (the standing-ovation moment, Section 7) ----
  if (!result.trust_passed) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="min-h-[760px] bg-alert px-6 pt-20 text-white"
      >
        <motion.div
          initial={{ scale: 0.6 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
          className="mx-auto grid h-20 w-20 place-items-center rounded-full bg-white/20 text-4xl"
        >
          ⚠
        </motion.div>
        <h2 className="mt-6 text-center text-2xl font-bold">Identity mismatch</h2>
        <p className="mt-2 text-center text-sm text-white/90">
          This unit does not match the one we delivered. This return cannot proceed
          automatically.
        </p>

        <div className="mt-6 space-y-2 rounded-2xl bg-white/10 p-4 text-sm backdrop-blur">
          <Row label="Serial on this unit" value={result.detected_serial} bad />
          <Row label="Serial we delivered" value={result.expected_serial} />
          <Row label="Identity confidence" value={`${(result.identity_confidence * 100).toFixed(1)}%`} bad />
        </div>

        <div className="mt-4 rounded-2xl bg-white/10 p-4 text-sm">
          <div className="mb-2 font-semibold">Why this was flagged</div>
          {result.behavioral_flags.map((f, i) => (
            <div key={i} className="flex gap-2 text-white/90">
              <span>•</span>
              {f}
            </div>
          ))}
        </div>

        <p className="mt-4 text-center text-xs text-white/80">
          Routed to human review with the full evidence bundle.
          <br />
          <span className="font-semibold">AI flags, humans accuse.</span>
        </p>

        <button
          onClick={onRestart}
          className="mt-6 w-full rounded-2xl bg-white py-3.5 font-semibold text-alert"
        >
          ↺ Run the honest return instead
        </button>
      </motion.div>
    );
  }

  // ---- HAPPY PATH: identity confirmed ----
  return (
    <div className="min-h-[760px] bg-white px-6 pt-16">
      <div className="text-xs uppercase tracking-widest text-trust">Fingerprint match</div>

      <div className="mt-5 flex items-center justify-center gap-3">
        <div className="text-center">
          <div className="grid h-28 w-28 place-items-center rounded-2xl bg-slate-100 text-4xl">🎧</div>
          <div className="mt-1 text-[10px] text-slate-400">Delivery day</div>
        </div>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: "spring" }}
          className="grid h-9 w-9 place-items-center rounded-full bg-trust text-white"
        >
          ✓
        </motion.div>
        <div className="text-center">
          <div className="grid h-28 w-28 place-items-center rounded-2xl bg-trust-soft text-4xl ring-2 ring-trust">
            🎧
          </div>
          <div className="mt-1 text-[10px] text-slate-400">Today</div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <div className="text-5xl font-extrabold text-trust">
          <CountUp to={result.identity_confidence * 100} decimals={1} suffix="%" />
        </div>
        <div className="mt-1 text-sm font-medium text-slate-500">Identity confirmed</div>
      </div>

      <div className="mt-8 space-y-2 rounded-2xl border border-slate-100 p-4 text-sm">
        <Row label="Serial match" value={result.serial_match ? `✓ ${result.detected_serial}` : "✗"} />
        <Row label="Embedding similarity" value={`${(result.embedding_sim * 100).toFixed(1)}%`} />
        <Row label="Perceptual hash distance" value={result.phash_dist.toFixed(3)} />
        <Row label="Trust score" value={`${(result.trust_score * 100).toFixed(0)}%`} />
      </div>

      <div className="mt-8">
        <PrimaryButton onClick={() => onPass(result)}>Continue to inspection</PrimaryButton>
      </div>
    </div>
  );
}

function Row({ label, value, bad }: { label: string; value: string; bad?: boolean }) {
  return (
    <div className="flex items-center justify-between">
      <span className="opacity-70">{label}</span>
      <span className={`font-mono font-semibold ${bad ? "text-white underline decoration-wavy" : ""}`}>
        {value}
      </span>
    </div>
  );
}
