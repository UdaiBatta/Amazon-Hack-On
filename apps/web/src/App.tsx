import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { api, GradeResult, VerifyResult } from "./lib/api";
import AmazonNav from "./components/AmazonNav";
import Orders from "./flows/orders/Orders";
import Scan from "./flows/scan/Scan";
import Verify from "./flows/verify/Verify";
import Certificate from "./flows/certificate/Certificate";
import Match from "./flows/match/Match";
import Journey from "./flows/journey/Journey";

export type Step = "orders" | "scan" | "verify" | "certificate" | "match" | "journey";

export type FlowState = {
  sessionId?: string;
  productName?: string;
  fraudMode: boolean;
  verify?: VerifyResult;
  grade?: GradeResult;
  transferId?: string;
};

export default function App() {
  const [step, setStep] = useState<Step>("orders");
  const [state, setState] = useState<FlowState>({ fraudMode: false });
  const patch = (p: Partial<FlowState>) => setState((s) => ({ ...s, ...p }));

  const restart = () => {
    setState({ fraudMode: false });
    setStep("orders");
  };

  return (
    <div className="flex min-h-screen flex-col bg-amzn-bg">
      <AmazonNav />

      <div className="flex flex-1 flex-col items-center justify-center gap-5 py-8">
        <div className="phone-shell">
          <div className="phone-notch" />
          <div className="scroll-area">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -24 }}
              transition={{ duration: 0.3 }}
            >
              {step === "orders" && (
                <Orders
                  onStart={async (sku, reason) => {
                    const s = await api.createSession(sku, reason);
                    patch({ sessionId: s.session_id, productName: s.product_name });
                    setStep("scan");
                  }}
                />
              )}
              {step === "scan" && state.sessionId && (
                <Scan
                  sessionId={state.sessionId}
                  productName={state.productName!}
                  onDone={() => setStep("verify")}
                />
              )}
              {step === "verify" && state.sessionId && (
                <Verify
                  sessionId={state.sessionId}
                  fraudMode={state.fraudMode}
                  onPass={(v) => {
                    patch({ verify: v });
                    setStep("certificate");
                  }}
                  onRestart={restart}
                />
              )}
              {step === "certificate" && state.sessionId && (
                <Certificate
                  sessionId={state.sessionId}
                  fraudMode={state.fraudMode}
                  identityConfidence={state.verify?.identity_confidence ?? 0}
                  onGraded={(g) => patch({ grade: g })}
                  onNext={() => setStep("match")}
                />
              )}
              {step === "match" && state.sessionId && (
                <Match
                  sessionId={state.sessionId}
                  onReserved={(transferId) => {
                    patch({ transferId });
                    setStep("journey");
                  }}
                />
              )}
              {step === "journey" && state.transferId && (
                <Journey transferId={state.transferId} onRestart={restart} />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Stage controls — driver only. Sets up the fraud moment (Section 7). */}
      <div className="flex w-full max-w-[420px] items-center justify-between rounded-2xl bg-white/70 px-4 py-3 text-xs shadow-sm">
        <label className="flex items-center gap-2 font-medium text-slate-700">
          <input
            type="checkbox"
            checked={state.fraudMode}
            onChange={(e) => patch({ fraudMode: e.target.checked })}
            className="h-4 w-4 accent-alert"
          />
          Scan the “swap” unit (fraud demo)
        </label>
        <button onClick={restart} className="font-semibold text-slate-500 hover:text-ink">
          ↺ Restart demo
        </button>
      </div>
      </div>
    </div>
  );
}
