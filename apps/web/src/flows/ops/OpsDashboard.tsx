import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../lib/api";

type Ev = { id: string; session_id: string; type: string; actor: string; ts: number; detail: any; mock: boolean };

const STATUS_STYLE: Record<string, string> = {
  REAL: "bg-trust/20 text-trust",
  MOCK: "bg-alert/20 text-alert",
  SEEDED: "bg-[#FF9900]/20 text-[#FF9900]",
  ROADMAP: "bg-white/10 text-slate-300",
};

function statusKey(s: string) {
  return s.startsWith("REAL") ? "REAL" : s;
}

export default function OpsDashboard() {
  const [services, setServices] = useState<{ name: string; engine: string; status: string }[]>([]);
  const [aiMode, setAiMode] = useState("");
  const [events, setEvents] = useState<Ev[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const feedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.opsServices().then((d) => {
      setServices(d.services);
      setAiMode(d.ai_mode);
    });
    const poll = setInterval(() => api.opsMetrics().then(setMetrics), 2000);
    api.opsMetrics().then(setMetrics);

    const es = new EventSource("/api/ops/stream");
    es.onmessage = (m) => {
      try {
        const ev = JSON.parse(m.data) as Ev;
        setEvents((prev) => [...prev.slice(-120), ev]);
      } catch {}
    };
    return () => {
      clearInterval(poll);
      es.close();
    };
  }, []);

  useEffect(() => {
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
  }, [events]);

  return (
    <div className="min-h-screen bg-[#131921] font-sans text-slate-200">
      {/* Amazon-style top bar */}
      <div className="flex items-center justify-between bg-[#0d1117] px-5 py-2.5">
        <div className="flex items-center gap-3">
          <div className="relative select-none pb-1">
            <span className="text-[18px] font-bold lowercase leading-none text-white">relay</span>
            <span className="text-[10px] font-semibold text-[#FF9900]">.ai</span>
            <svg className="absolute -bottom-0.5 left-0" width="48" height="7" viewBox="0 0 48 7" fill="none">
              <path d="M2 2 C 14 8, 34 8, 45 1" stroke="#FF9900" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </div>
          <span className="rounded bg-[#FF9900]/15 px-2 py-0.5 text-[11px] font-semibold text-[#FF9900]">
            Ops · Mission Control
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-white/5 px-3 py-1.5 text-xs">
            AI mode: <span className="font-mono font-bold text-[#FF9900]">{aiMode}</span>
          </div>
          <Link
            to="/"
            className="rounded-md border border-white/30 px-3 py-1.5 text-[12px] font-semibold text-white hover:border-white"
          >
            Store ↗
          </Link>
          <Link
            to="/buyer"
            className="rounded-md border border-white/30 px-3 py-1.5 text-[12px] font-semibold text-white hover:border-white"
          >
            Buyer ↗
          </Link>
        </div>
      </div>
      <div className="h-0.5 w-full bg-gradient-to-r from-[#FF9900] via-[#FF9900]/30 to-transparent" />

      <div className="p-6">
        <div className="mb-1 text-xs text-slate-500">
          Event-driven returns brain · append-only custody ledger · CQRS-lite read model
        </div>

        {/* metrics */}
        {metrics && (
          <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-5">
            <MetricCard label="Returns processed" value={metrics.returns_processed} />
            <MetricCard label="$ saved / return" value={`$${metrics.warehouse_cost_saved_per_return}`} accent />
            <MetricCard label="Avg km avoided" value={metrics.avg_km_avoided.toLocaleString()} accent />
            <MetricCard label="Fraud caught" value={metrics.fraud_caught} alert />
            <MetricCard label="Confirmed transfers" value={metrics.confirmed_transfers} />
          </div>
        )}

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          {/* live event feed */}
          <div className="rounded-xl bg-white/[0.03] p-4 ring-1 ring-white/10">
            <div className="mb-3 flex items-center gap-2">
              <span className="h-2 w-2 animate-pulse rounded-full bg-trust" />
              <h2 className="text-sm font-semibold text-white">Live event stream</h2>
            </div>
            <div ref={feedRef} className="h-[420px] space-y-1.5 overflow-y-auto pr-2 font-mono text-xs">
              {events.length === 0 && (
                <div className="text-slate-600">Waiting for events. Run the demo flow.</div>
              )}
              {events.map((e) => (
                <div key={e.id} className="flex items-start gap-2 rounded-lg bg-white/[0.02] px-2 py-1.5">
                  <span className="text-slate-600">{new Date(e.ts).toLocaleTimeString()}</span>
                  <span className={`font-semibold ${e.mock ? "text-alert" : "text-trust"}`}>
                    {e.type}
                  </span>
                  {e.mock && (
                    <span className="rounded bg-alert/20 px-1 text-[9px] text-alert">MOCK</span>
                  )}
                  <span className="truncate text-slate-400">
                    {e.actor} · {JSON.stringify(e.detail).slice(0, 60)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* service registry — the honest mock pattern */}
          <div className="rounded-xl bg-white/[0.03] p-4 ring-1 ring-white/10">
            <h2 className="mb-1 text-sm font-semibold text-white">
              Service registry: what is real vs mocked
            </h2>
            <p className="mb-3 text-[11px] text-slate-500">
              We never bluff. Every mocked service is badged here.
            </p>
            <div className="space-y-1.5">
              {services.map((s) => (
                <div
                  key={s.name}
                  className="flex items-center justify-between rounded-lg bg-white/[0.02] px-3 py-2"
                >
                  <div>
                    <div className="text-sm font-medium text-white">{s.name}</div>
                    <div className="text-[11px] text-slate-500">{s.engine}</div>
                  </div>
                  <span
                    className={`rounded-md px-2 py-0.5 text-[10px] font-bold ${
                      STATUS_STYLE[statusKey(s.status)] || STATUS_STYLE.ROADMAP
                    }`}
                  >
                    {s.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  alert,
  accent,
}: {
  label: string;
  value: any;
  alert?: boolean;
  accent?: boolean;
}) {
  const color = alert ? "text-alert" : accent ? "text-[#FF9900]" : "text-white";
  return (
    <div className="rounded-xl bg-white/[0.03] p-4 ring-1 ring-white/10">
      <div className={`text-2xl font-extrabold ${color}`}>{value}</div>
      <div className="mt-1 text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  );
}
