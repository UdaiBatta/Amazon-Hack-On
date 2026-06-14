import { useEffect, useRef, useState } from "react";
import { motion, useAnimationControls } from "framer-motion";
import { api, CaptureStep, API_BASE } from "../../lib/api";
import { assessFrame, captureBlob, QualityReport } from "../../lib/quality";

// Scripted redirect: the AI catches the wrong view once (the gasp moment,
// Section 2 step 2). Distinct from the on-device quality gate below.
const REDIRECT_AT = "serial";
const REDIRECT_MSG = "That's the box barcode — I need the sticker under the left earcup.";

export default function Scan({
  sessionId,
  productName,
  onDone,
}: {
  sessionId: string;
  productName: string;
  onDone: () => void;
}) {
  const [checklist, setChecklist] = useState<CaptureStep[]>([]);
  const [idx, setIdx] = useState(0);
  const [redirected, setRedirected] = useState(false);
  const [redirectMsg, setRedirectMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [camOn, setCamOn] = useState(false);
  const [quality, setQuality] = useState<QualityReport | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const workRef = useRef<HTMLCanvasElement>(null);
  const captureRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const shake = useAnimationControls();
  const captured = idx;

  useEffect(() => {
    fetch(`${API_BASE}/catalog/items`)
      .then((r) => r.json())
      .then((d) => {
        const item = d.items.find((i: any) => i.name === productName) || d.items[0];
        setChecklist(item.checklist);
      });
  }, [sessionId, productName]);

  // ---- real camera (graceful fallback if denied/unavailable) ----
  useEffect(() => {
    let raf = 0;
    let active = true;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: 1280, height: 720 },
          audio: false,
        });
        if (!active) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play().catch(() => {});
        }
        setCamOn(true);
        const loop = () => {
          if (!active) return;
          if (videoRef.current && workRef.current && videoRef.current.videoWidth) {
            setQuality(assessFrame(videoRef.current, workRef.current));
          }
          raf = requestAnimationFrame(loop);
        };
        raf = requestAnimationFrame(loop);
      } catch {
        setCamOn(false); // fall back to simulated viewport
      }
    })();
    return () => {
      active = false;
      cancelAnimationFrame(raf);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const total = checklist.length || 4;
  const progress = captured / total;
  const current = checklist[Math.min(idx, total - 1)];
  const ready = !camOn || (quality?.ok ?? true);

  async function capture() {
    if (busy || idx >= total) return;
    const step = checklist[idx];

    // on-device quality gate (real). Rejected frame shakes once.
    if (camOn && quality && !quality.ok) {
      setRedirectMsg(quality.reason || "Adjust framing");
      await shake.start({ x: [0, -8, 8, -5, 5, 0], transition: { duration: 0.35 } });
      return;
    }

    setBusy(true);

    // staged AI redirect once (wrong view)
    if (step.key === REDIRECT_AT && !redirected) {
      setRedirected(true);
      setRedirectMsg(REDIRECT_MSG);
      await shake.start({ x: [0, -10, 10, -6, 6, 0], transition: { duration: 0.4 } });
      setBusy(false);
      return;
    }

    setRedirectMsg(null);

    // capture a real JPEG if the camera is live
    let blob: Blob | undefined;
    if (camOn && videoRef.current && captureRef.current) {
      blob = await captureBlob(videoRef.current, captureRef.current);
    }
    const q = quality ? Math.min(1, quality.blurVariance / 60) : 0.93;
    await api.submitFrame(sessionId, step.key, q, blob);
    await new Promise((r) => setTimeout(r, 350));
    setIdx((i) => i + 1);
    setBusy(false);
  }

  useEffect(() => {
    if (checklist.length && idx >= total) {
      const t = setTimeout(onDone, 700);
      return () => clearTimeout(t);
    }
  }, [idx, total, checklist.length, onDone]);

  return (
    <div className="relative min-h-[760px] bg-ink pt-12 text-white">
      <canvas ref={workRef} className="hidden" />
      <canvas ref={captureRef} className="hidden" />

      {/* camera viewport */}
      <motion.div animate={shake} className="relative mx-auto mt-2 h-[420px] w-full overflow-hidden">
        {/* live video (object-fit cover) */}
        <video
          ref={videoRef}
          playsInline
          muted
          className={`absolute inset-0 h-full w-full object-cover ${camOn ? "" : "hidden"}`}
        />
        {/* simulated fallback */}
        {!camOn && (
          <>
            <div className="absolute inset-0 bg-gradient-to-br from-slate-700 via-slate-800 to-black" />
            <div className="absolute inset-0 grid place-items-center">
              <motion.div
                animate={{ opacity: [0.5, 0.9, 0.5] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="text-[120px]"
              >
                🎧
              </motion.div>
            </div>
          </>
        )}

        {/* framing reticle — turns trust-green when on-device checks pass */}
        <div
          className={`absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-3xl border-2 border-dashed transition-colors ${
            ready ? "border-trust" : "border-white/40"
          }`}
        />

        {/* live quality chips (real on-device metrics) */}
        {camOn && quality && (
          <div className="absolute left-3 top-3 space-y-1 text-[10px] font-mono">
            <Chip ok={quality.blurVariance >= 8} label={`sharp ${quality.blurVariance}`} />
            <Chip ok={quality.brightness >= 35 && quality.brightness <= 245} label={`light ${quality.brightness}`} />
            <Chip ok={quality.fill >= 0.04} label={`fill ${quality.fill}`} />
          </div>
        )}

        {/* progress ring */}
        <div className="absolute right-4 top-4">
          <svg width="56" height="56" className="-rotate-90">
            <circle cx="28" cy="28" r="24" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="4" />
            <motion.circle
              cx="28"
              cy="28"
              r="24"
              fill="none"
              stroke="#0e9f6e"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 24}
              animate={{ strokeDashoffset: 2 * Math.PI * 24 * (1 - progress) }}
              transition={{ duration: 0.5 }}
            />
          </svg>
          <div className="-mt-[40px] text-center text-xs font-bold">
            {captured}/{total}
          </div>
          <div className="mt-5" />
        </div>

        {redirectMsg && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="absolute bottom-4 left-4 right-4 rounded-2xl bg-alert/90 p-3 text-sm font-medium backdrop-blur"
          >
            ⚠ {redirectMsg}
          </motion.div>
        )}
      </motion.div>

      {/* instruction + capture */}
      <div className="px-6 pt-6">
        <div className="flex items-center justify-between">
          <div className="text-xs uppercase tracking-widest text-trust">AI-guided scan</div>
          <div className="text-[10px] text-white/40">{camOn ? "● live camera" : "○ demo viewport"}</div>
        </div>
        <motion.div
          key={current?.key}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-xl font-semibold"
        >
          {idx >= total ? "All angles captured ✓" : current?.instruction}
        </motion.div>

        <div className="mt-3 flex gap-1.5">
          {checklist.map((s, i) => (
            <div
              key={s.key}
              className={`h-1.5 flex-1 rounded-full ${i < idx ? "bg-trust" : "bg-white/20"}`}
            />
          ))}
        </div>

        {idx < total && (
          <button
            onClick={capture}
            disabled={busy}
            className={`mt-8 flex w-full items-center justify-center gap-2 rounded-2xl py-4 font-semibold transition active:scale-95 disabled:opacity-50 ${
              ready ? "bg-white text-ink" : "bg-white/30 text-white"
            }`}
          >
            {busy ? (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-ink" />
            ) : (
              <span className={`h-4 w-4 rounded-full ${ready ? "bg-alert" : "bg-white/60"}`} />
            )}
            {busy ? "Analyzing frame…" : ready ? "Capture" : "Adjust framing…"}
          </button>
        )}
        <p className="mt-3 text-center text-[11px] text-white/40">
          Live blur &amp; framing checks run on-device; each frame is verified by Claude vision.
        </p>
      </div>
    </div>
  );
}

function Chip({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div
      className={`rounded-md px-1.5 py-0.5 backdrop-blur ${
        ok ? "bg-trust/30 text-trust" : "bg-alert/30 text-white"
      }`}
    >
      {ok ? "✓" : "•"} {label}
    </div>
  );
}
