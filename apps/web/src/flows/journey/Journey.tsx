import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "../../lib/api";
import { CountUp, PrimaryButton } from "../../components/ui";

type Conf = Awaited<ReturnType<typeof api.confirm>>;

export default function Journey({
  transferId,
  onRestart,
}: {
  transferId: string;
  onRestart: () => void;
}) {
  const [conf, setConf] = useState<Conf | null>(null);

  useEffect(() => {
    api.confirm(transferId).then(setConf);
  }, [transferId]);

  if (!conf) {
    return (
      <div className="grid min-h-[760px] place-items-center bg-ink text-white/60">
        Confirming handoff…
      </div>
    );
  }

  const j = conf.journey;
  return (
    <div className="min-h-[760px] bg-ink px-6 pb-8 pt-16 text-white">
      <motion.div
        initial={{ scale: 0.6 }}
        animate={{ scale: 1 }}
        className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-trust text-3xl"
      >
        ✓
      </motion.div>
      <h2 className="mt-4 text-center text-xl font-bold">Item received as described</h2>
      <p className="mt-1 text-center text-sm text-white/60">Refund &amp; payment released.</p>

      {/* old world */}
      <div className="mt-8 rounded-2xl bg-white/5 p-4">
        <div className="text-[10px] uppercase tracking-widest text-white/40">Old world</div>
        <div className="mt-1 flex items-center justify-between">
          <Metric value={j.old_world.distance_km} label="km" />
          <Metric value={j.old_world.warehouses} label="warehouses" />
          <Metric value={j.old_world.days} label="days" />
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-xs text-white/40">
          📦 → ✈ → 🏭 → 🏭 → ✈ → 🏠
        </div>
      </div>

      {/* relay */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-4 rounded-2xl bg-trust/15 p-4 ring-1 ring-trust/50"
      >
        <div className="text-[10px] uppercase tracking-widest text-trust">RELAY</div>
        <div className="mt-1 flex items-center justify-between">
          <div className="text-center">
            <div className="text-2xl font-extrabold text-trust">
              <CountUp to={j.relay.distance_km} decimals={1} />
            </div>
            <div className="text-[10px] text-white/50">km</div>
          </div>
          <Metric value={j.relay.warehouses} label="warehouses" highlight />
          <Metric value={j.relay.hops} label="hop" highlight />
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-xs text-trust">🏠 → 🚚 → 🏠</div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.1 }}
        className="mt-8 text-center"
      >
        <div className="text-3xl font-extrabold leading-tight">
          The item never
          <br />
          touched a warehouse.
        </div>
        <div className="mt-3 text-sm text-white/60">
          <CountUp to={j.km_avoided} decimals={0} /> km and {j.co2e_avoided_kg} kg CO₂e avoided.
        </div>
      </motion.div>

      <div className="mt-8">
        <PrimaryButton onClick={onRestart}>Run the demo again</PrimaryButton>
      </div>
    </div>
  );
}

function Metric({
  value,
  label,
  highlight,
}: {
  value: number;
  label: string;
  highlight?: boolean;
}) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-extrabold ${highlight ? "text-trust" : "text-white"}`}>
        <CountUp to={value} />
      </div>
      <div className="text-[10px] text-white/50">{label}</div>
    </div>
  );
}
