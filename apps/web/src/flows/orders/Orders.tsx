import { useEffect, useState } from "react";
import { api, Order } from "../../lib/api";
import { PrimaryButton } from "../../components/ui";

export default function Orders({ onStart }: { onStart: (sku: string, reason: string) => void }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [reason, setReason] = useState("Changed my mind");
  const [picking, setPicking] = useState<Order | null>(null);

  useEffect(() => {
    api.orders().then((r) => setOrders(r.orders));
  }, []);

  return (
    <div className="min-h-[760px] bg-amzn-bg px-3 pb-8 pt-10">
      <h1 className="mb-1 px-1 text-lg font-bold text-[#0F1111]">Your Orders</h1>
      <div className="mb-3 flex gap-4 border-b border-amzn-border px-1 text-[13px]">
        <span className="border-b-2 border-amzn-orange pb-1 font-bold text-[#0F1111]">Orders</span>
        <span className="pb-1 text-amzn-link">Buy Again</span>
        <span className="pb-1 text-amzn-link">Not Yet Shipped</span>
      </div>

      {orders.map((o) => (
        <div key={o.order_id} className="mb-4 overflow-hidden rounded-lg border border-amzn-border bg-white">
          {/* order header band */}
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amzn-border bg-amzn-band px-4 py-2 text-[11px] text-gray-600">
            <div className="flex gap-6">
              <div>
                <div className="uppercase tracking-wide">Order placed</div>
                <div className="text-[12px] text-[#0F1111]">
                  {o.delivered_days_ago + 2} days ago
                </div>
              </div>
              <div>
                <div className="uppercase tracking-wide">Total</div>
                <div className="text-[12px] text-[#0F1111]">₹{o.price.toLocaleString()}</div>
              </div>
              <div className="hidden sm:block">
                <div className="uppercase tracking-wide">Ship to</div>
                <div className="text-[12px] text-amzn-link">Asha</div>
              </div>
            </div>
            <div className="text-right">
              <div className="uppercase tracking-wide">Order # {o.order_id}</div>
              <div className="text-amzn-link">View order details</div>
            </div>
          </div>

          {/* body */}
          <div className="p-4">
            <div className="mb-1 text-[15px] font-bold text-trust-dark">Delivered</div>
            <div className="mb-3 text-[12px] text-gray-600">
              Package was handed to resident
            </div>
            <div className="flex gap-3">
              <div className="grid h-20 w-20 shrink-0 place-items-center rounded bg-amzn-band text-3xl">
                🎧
              </div>
              <div className="flex-1">
                <div className="text-[14px] font-medium leading-snug text-amzn-link hover:text-amzn-price">
                  {o.name}
                </div>
                <div className="mt-1 text-[12px] text-gray-600">
                  Return window open through doorstep verification
                </div>

                {!picking && (
                  <div className="mt-3 flex flex-col gap-2">
                    <button className="rounded-full border border-amzn-border bg-white py-1.5 text-[13px] font-medium text-[#0F1111] shadow-sm hover:bg-amzn-band">
                      Buy it again
                    </button>
                    <button
                      onClick={() => setPicking(o)}
                      className="rounded-full border border-amzn-border bg-white py-1.5 text-[13px] font-medium text-[#0F1111] shadow-sm hover:bg-amzn-band"
                    >
                      Return or replace items
                    </button>
                  </div>
                )}
              </div>
            </div>

            {picking && (
              <div className="mt-4 space-y-3 border-t border-amzn-border pt-3">
                <div className="text-[13px] font-bold text-[#0F1111]">Reason for return</div>
                <select
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full rounded-md border border-amzn-border bg-amzn-band px-3 py-2 text-[13px]"
                >
                  <option>Changed my mind</option>
                  <option>Better price available</option>
                  <option>Item not as expected</option>
                </select>

                {/* The doorstep framing is the wow-beat (Section 2, Step 1) */}
                <div className="rounded-lg border border-trust/40 bg-trust-soft/50 p-3">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-amzn-orange px-1.5 py-0.5 text-[10px] font-bold text-amzn-squid">
                      NEW
                    </span>
                    <span className="text-[14px] font-bold text-trust-dark">Doorstep AI Return</span>
                  </div>
                  <p className="mt-1 text-[12px] leading-relaxed text-gray-700">
                    Verified in 3 minutes, picked up tomorrow. Your return starts at your door,
                    not at a warehouse.
                  </p>
                </div>

                <PrimaryButton onClick={() => onStart(o.sku, reason)}>
                  Start Doorstep AI Return
                </PrimaryButton>
              </div>
            )}
          </div>
        </div>
      ))}

      <p className="px-1 text-center text-[11px] text-gray-500">
        Verified second-life returns, powered by RELAY
      </p>
    </div>
  );
}
