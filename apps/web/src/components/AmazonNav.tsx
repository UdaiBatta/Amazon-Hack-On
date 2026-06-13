import { Link } from "react-router-dom";

// "relay.ai" wordmark with an Amazon-style smile arc.
function RelayLogo() {
  return (
    <div className="relative select-none pb-1 pr-1">
      <span className="text-[20px] font-bold lowercase leading-none tracking-tight text-white">
        relay
      </span>
      <span className="text-[11px] font-semibold text-[#FF9900]">.ai</span>
      <svg className="absolute -bottom-0.5 left-0" width="54" height="8" viewBox="0 0 54 8" fill="none">
        <path d="M2 2 C 16 9, 38 9, 51 1" stroke="#FF9900" strokeWidth="2" strokeLinecap="round" />
      </svg>
    </div>
  );
}

export default function AmazonNav({ user = "Asha" }: { user?: string }) {
  return (
    <div className="w-full">
      {/* main bar */}
      <div className="flex items-center gap-2 bg-[#131921] px-3 py-2 text-white sm:gap-3 sm:px-4">
        <Link
          to="/"
          className="flex items-end rounded border border-transparent px-1.5 py-1.5 hover:border-white/70"
        >
          <RelayLogo />
        </Link>

        <div className="hidden items-center gap-1 rounded border border-transparent px-1.5 py-1 hover:border-white/70 lg:flex">
          <span className="text-base">📍</span>
          <div className="leading-tight">
            <div className="text-[11px] text-gray-300">Deliver to {user}</div>
            <div className="text-[13px] font-bold">Patiala 147001</div>
          </div>
        </div>

        {/* search */}
        <div className="flex h-9 min-w-0 flex-1 overflow-hidden rounded-md">
          <select
            className="hidden h-full bg-[#f3f3f3] px-2 text-xs text-gray-700 sm:block"
            defaultValue="all"
          >
            <option value="all">All</option>
            <option>Electronics</option>
            <option>Renewed</option>
          </select>
          <input
            className="h-full min-w-0 flex-1 bg-white px-3 text-sm text-gray-900 outline-none"
            placeholder="Search verified second-life deals"
          />
          <button className="grid h-full w-11 place-items-center bg-[#FEBD69] text-[#131921] hover:bg-[#f3a847]">
            <span className="text-base">🔍</span>
          </button>
        </div>

        <div className="hidden leading-tight md:block">
          <div className="text-[11px] text-gray-300">Hello, {user}</div>
          <div className="text-[13px] font-bold">Account &amp; Lists</div>
        </div>

        {/* clearly visible role switch buttons */}
        <Link
          to="/buyer"
          target="_blank"
          className="shrink-0 rounded-md border border-white/40 px-3 py-1.5 text-[12px] font-semibold text-white hover:border-white hover:bg-white/10"
        >
          Buyer
        </Link>
        <Link
          to="/ops"
          target="_blank"
          className="shrink-0 rounded-md border border-[#FF9900] bg-[#FF9900]/15 px-3 py-1.5 text-[12px] font-semibold text-[#FF9900] hover:bg-[#FF9900]/25"
        >
          Ops
        </Link>
      </div>

      {/* secondary nav */}
      <div className="flex items-center gap-4 bg-[#232F3E] px-4 py-1.5 text-[13px] text-white">
        <span className="flex items-center gap-1 rounded border border-transparent px-1 font-bold hover:border-white/60">
          ☰ All
        </span>
        {["Today's Deals", "Amazon Renewed", "Returns & Orders", "Sell"].map((l) => (
          <span
            key={l}
            className="hidden rounded border border-transparent px-1 hover:border-white/60 md:inline"
          >
            {l}
          </span>
        ))}
        <span className="ml-auto font-semibold text-[#FF9900]">Returns that never return</span>
      </div>
    </div>
  );
}
