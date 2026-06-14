import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { api } from "../../lib/api";
import { CountUp } from "../../components/ui";

const BUYER_ID = "buyer_rohan";
type Card = Awaited<ReturnType<typeof api.buyerFeed>>["cards"][number];

export default function BuyerView() {
  const [name, setName] = useState("Rohan");
  const [cards, setCards] = useState<Card[]>([]);
  const [busy, setBusy] = useState(false);
  const [journey, setJourney] = useState<any>(null);
  const [seen, setSeen] = useState(false);

  async function refresh() {
    const f = await api.buyerFeed(BUYER_ID);
    setName(f.buyer_name);
    setCards(f.cards);
    if (f.cards.length) setSeen(true);
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 2000);
    return () => clearInterval(t);
  }, []);

  const card = cards[0];

  async function reserve() {
    if (!card) return;
    setBusy(true);
    await api.reserve(card.session_id, BUYER_ID);
    await refresh();
    setBusy(false);
  }

  async function confirm() {
    if (!card?.transfer_id) return;
    setBusy(true);
    const c = await api.confirm(card.transfer_id);
    setJourney(c.journey);
    await refresh();
    setBusy(false);
  }

  return (
    <div className="flex min-h-screen flex-col bg-amzn-bg">
      <div className="flex items-center justify-between bg-amzn-squid px-4 py-2 text-white">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🛒</span>
          <div>
            <div className="text-[15px] font-bold lowercase">
              relay<span className="text-amzn-orange">.ai</span> · buyer
            </div>
            <div className="text-[10px] text-gray-300">{name}'s demand feed · Patiala</div>
          </div>
        </div>
        <a
          href="/"
          className="rounded border border-white/40 px-3 py-1.5 text-xs font-semibold text-white hover:border-white"
        >
          Seller view ↗
        </a>
      </div>
      <div className="bg-amzn-navy px-4 py-1.5 text-[12px] font-semibold text-amzn-orange">
        Verified second-life deals near you
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-5 py-8">
      <header className="hidden">
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-trust font-bold text-white">B</div>
          <div>
            <div className="text-sm font-bold tracking-tight text-ink">RELAY · Buyer</div>
            <div className="text-[10px] text-slate-500">{name}'s demand feed</div>
          </div>
        </div>
        <a href="/" className="rounded-lg bg-ink/90 px-3 py-1.5 text-xs font-semibold text-white">
          Seller view ↗
        </a>
      </header>

      <div className="phone-shell">
        <div className="phone-notch" />
        <div className="scroll-area bg-white">
          <div className="min-h-[760px] px-5 pb-8 pt-12">
            <div className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
              Wishlist · matches near you
            </div>

            {/* empty state */}
            {!card && (
              <div className="mt-24 text-center text-slate-400">
                <div className="text-5xl">🛰️</div>
                <p className="mt-4 text-sm">
                  No matches yet.
                  <br />
                  {seen
                    ? "Item handed off."
                    : "Run a return on the seller view — verified items nearby appear here."}
                </p>
                <div className="mt-6 rounded-2xl bg-slate-50 p-3 text-left text-xs text-slate-500">
                  <div className="font-semibold text-slate-600">Your active wishlist</div>
                  <div className="mt-1">🎧 JBL Tune 770NC · Grade C+ · under ₹4,500</div>
                </div>
              </div>
            )}

            <AnimatePresence mode="wait">
              {card && (
                <motion.div
                  key={card.session_id + card.state}
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -24 }}
                >
                  {/* push card */}
                  <div className="rounded-2xl border border-trust/30 bg-trust-soft/40 p-3">
                    <div className="flex items-center gap-2 text-trust-dark">
                      <span className="rounded-md bg-trust px-1.5 py-0.5 text-[10px] font-bold text-white">
                        MATCH
                      </span>
                      <span className="text-xs font-semibold">Verified item found nearby</span>
                    </div>
                  </div>

                  <div className="mt-4 rounded-3xl border border-slate-100 p-4 shadow-sm">
                    <div className="flex gap-3">
                      <div className="grid h-16 w-16 shrink-0 place-items-center rounded-xl bg-slate-100 text-3xl">
                        🎧
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-bold leading-tight text-ink">{card.product_name}</div>
                        <div className="mt-0.5 text-xs text-slate-500">
                          {card.distance_km} km away · {card.defect_count} defect(s) noted
                        </div>
                        <div className="mt-1 flex items-center gap-2">
                          <span className="rounded-md bg-ink px-1.5 py-0.5 text-[10px] font-bold text-white">
                            Grade {card.grade}
                          </span>
                          {card.identity_confidence != null && (
                            <span className="text-[10px] text-trust-dark">
                              {(card.identity_confidence * 100).toFixed(0)}% identity verified
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-extrabold text-ink">
                          ₹{card.price.toLocaleString()}
                        </div>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center gap-2 rounded-xl bg-slate-50 p-2 text-[11px] text-slate-500">
                      <span className="text-trust">🛡</span>
                      AI inspection certificate · {card.certificate_id}
                    </div>

                    {/* state-driven CTA */}
                    {!card.reserved && (
                      <button
                        onClick={reserve}
                        disabled={busy}
                        className="mt-4 w-full rounded-full border border-[#FCD200] bg-amzn-yellow py-3 font-medium text-[#0F1111] shadow-sm hover:bg-amzn-yellowHover disabled:opacity-50"
                      >
                        {busy ? "Reserving…" : "Reserve this item"}
                      </button>
                    )}

                    {card.reserved && card.transfer_status !== "confirmed" && !journey && (
                      <div className="mt-4">
                        <div className="rounded-2xl bg-slate-50 p-3 text-xs text-slate-600">
                          <div className="font-semibold text-ink">Reserved ✓</div>
                          <div className="mt-1">Tracking {card.tracking}</div>
                          <div>Pickup tomorrow 10:00 to 12:00 · tamper-evident RELAY bag</div>
                        </div>
                        <button
                          onClick={confirm}
                          disabled={busy}
                          className="mt-3 w-full rounded-full bg-amzn-squid py-3 font-medium text-white hover:bg-amzn-navy disabled:opacity-50"
                        >
                          {busy ? "Releasing…" : "Confirm received as described"}
                        </button>
                      </div>
                    )}

                    {journey && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="mt-4 rounded-2xl bg-trust/10 p-4 text-center ring-1 ring-trust/40"
                      >
                        <div className="text-3xl">✓</div>
                        <div className="mt-1 text-sm font-bold text-trust-dark">
                          Payment released
                        </div>
                        <div className="mt-3 text-2xl font-extrabold text-ink">
                          <CountUp to={journey.relay.distance_km} decimals={1} /> km · 0 warehouses
                        </div>
                        <div className="mt-1 text-xs text-slate-500">
                          vs old world {journey.old_world.distance_km.toLocaleString()} km ·{" "}
                          {journey.old_world.warehouses} warehouses
                        </div>
                        <div className="mt-3 text-xs font-semibold text-trust-dark">
                          The item never touched a warehouse.
                        </div>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <p className="max-w-[420px] px-4 text-center text-[11px] text-slate-400">
        This view polls the buyer demand feed live. Reserve here or on the seller view, bookings
        are idempotent.
      </p>
      </div>
    </div>
  );
}
