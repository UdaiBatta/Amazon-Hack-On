import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip } from "react-leaflet";
import { api, MatchCandidate } from "../../lib/api";
import { PrimaryButton } from "../../components/ui";

type MatchData = Awaited<ReturnType<typeof api.matches>>;

export default function Match({
  sessionId,
  onReserved,
}: {
  sessionId: string;
  onReserved: (transferId: string) => void;
}) {
  const [disp, setDisp] = useState<{ path: string; explanation: string } | null>(null);
  const [data, setData] = useState<MatchData | null>(null);
  const [reserving, setReserving] = useState(false);

  useEffect(() => {
    (async () => {
      const d = await api.disposition(sessionId);
      setDisp(d);
      await new Promise((r) => setTimeout(r, 1400));
      const m = await api.matches(sessionId);
      setData(m);
    })();
  }, [sessionId]);

  const top: MatchCandidate | undefined = data?.candidates[0];
  const center = useMemo<[number, number]>(
    () => (data ? [data.seller.lat, data.seller.lng] : [30.3398, 76.3869]),
    [data]
  );

  async function reserve() {
    if (!top) return;
    setReserving(true);
    const r = await api.reserve(sessionId, top.buyer_id);
    onReserved(r.transfer_id);
  }

  return (
    <div className="min-h-[760px] bg-ink pt-12 text-white">
      {/* disposition decision card */}
      {disp && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-4 rounded-2xl bg-trust/15 p-3 ring-1 ring-trust/40"
        >
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-trust px-2 py-0.5 text-[10px] font-bold">{disp.path}</span>
            <span className="text-xs font-semibold text-trust">Disposition engine</span>
          </div>
          <p className="mt-1 text-[11px] leading-relaxed text-white/80">{disp.explanation}</p>
        </motion.div>
      )}

      {/* the map */}
      <div className="relative mt-3 h-[360px]">
        {data && (
          <MapContainer center={center} zoom={12} className="h-full w-full" zoomControl={false}>
            <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
            {/* demand pins */}
            {data.demand_pins.map((p) => (
              <CircleMarker
                key={p.buyer_id}
                center={[p.lat, p.lng]}
                radius={6}
                pathOptions={{ color: "#0e9f6e", fillColor: "#0e9f6e", fillOpacity: 0.5 }}
              />
            ))}
            {/* seller */}
            <CircleMarker
              center={[data.seller.lat, data.seller.lng]}
              radius={9}
              pathOptions={{ color: "#fff", fillColor: "#e02424", fillOpacity: 1 }}
            >
              <Tooltip permanent direction="top">You (Asha)</Tooltip>
            </CircleMarker>
            {/* matched buyer + route */}
            {top && (
              <>
                <Polyline
                  positions={[[data.seller.lat, data.seller.lng], [top.lat, top.lng]]}
                  pathOptions={{ color: "#0e9f6e", weight: 3, dashArray: "6 8" }}
                />
                <CircleMarker
                  center={[top.lat, top.lng]}
                  radius={9}
                  pathOptions={{ color: "#fff", fillColor: "#0e9f6e", fillOpacity: 1 }}
                >
                  <Tooltip permanent direction="bottom">
                    {top.buyer_name} · {top.distance_km} km
                  </Tooltip>
                </CircleMarker>
              </>
            )}
          </MapContainer>
        )}
        {!data && (
          <div className="grid h-full place-items-center text-sm text-white/50">
            Searching the demand network…
          </div>
        )}
      </div>

      {/* buyer reserve card */}
      {top && (
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="mx-4 mt-4 rounded-2xl bg-white p-4 text-ink"
        >
          <div className="text-xs uppercase tracking-widest text-trust">Buyer found</div>
          <div className="mt-1 flex items-center justify-between">
            <div>
              <div className="text-lg font-bold">{top.buyer_name}</div>
              <div className="text-xs text-slate-500">
                {top.distance_km} km away · wants Grade {top.condition_min}+ under ₹
                {top.max_price.toLocaleString()}
              </div>
            </div>
            <div className="text-right">
              <div className="text-xl font-extrabold">₹{data!.price.resale_value.toLocaleString()}</div>
              <div className="text-[10px] text-slate-400">Grade {data!.grade} · verified</div>
            </div>
          </div>
          <div className="mt-4">
            <PrimaryButton onClick={reserve} disabled={reserving}>
              {reserving ? "Reserving…" : "Reserve and schedule pickup"}
            </PrimaryButton>
          </div>
          <p className="mt-2 text-center text-[10px] text-slate-400">
            Courier carries a tamper-evident RELAY bag. Carrier booking is mocked (see ops).
          </p>
        </motion.div>
      )}
    </div>
  );
}
