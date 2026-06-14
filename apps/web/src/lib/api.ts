// Typed API client for the RELAY backend. Talks through the Vite /api proxy.

const BASE = "/api";

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

function form(data: Record<string, string | boolean | number>): FormData {
  const fd = new FormData();
  Object.entries(data).forEach(([k, v]) => fd.append(k, String(v)));
  return fd;
}

export type CaptureStep = { key: string; instruction: string; required: boolean };
export type Order = {
  order_id: string;
  sku: string;
  name: string;
  price: number;
  delivered_days_ago: number;
  returnable: boolean;
};
export type Defect = {
  type: string;
  location: string;
  size_cm: number | null;
  severity: "cosmetic" | "minor" | "moderate" | "major";
  affects_function: boolean;
  confidence: number;
};
export type VerifyResult = {
  identity_confidence: number;
  embedding_sim: number;
  phash_dist: number;
  serial_match: boolean;
  detected_serial: string;
  expected_serial: string;
  verdict: "pass" | "extra_angle" | "fraud";
  trust_score: number;
  trust_passed: boolean;
  behavioral_flags: string[];
};
export type GradeResult = {
  grade: string;
  score: number;
  confidence: number;
  rationale: string;
  defects: Defect[];
  price: { resale_value: number; instant_refund: number; pct_of_new: number; rationale: string };
  certificate_id: string;
  ai_source: string;
};
export type MatchCandidate = {
  buyer_id: string;
  buyer_name: string;
  lat: number;
  lng: number;
  distance_km: number;
  max_price: number;
  condition_min: string;
  fit: number;
};

export const api = {
  orders: () => req<{ orders: Order[] }>("/catalog/orders"),

  createSession: (sku: string, reason: string) =>
    req<{ session_id: string; checklist: CaptureStep[]; product_name: string }>(
      "/sessions",
      { method: "POST", body: form({ sku, reason }) }
    ),

  submitFrame: (sid: string, step_key: string, quality_score = 0.93, image?: Blob) => {
    const fd = new FormData();
    fd.append("step_key", step_key);
    fd.append("quality_score", String(quality_score));
    if (image) fd.append("image", image, `${step_key}.jpg`);
    return req<{ accepted: boolean; reason?: string; next_step: string | null; scan_complete?: boolean }>(
      `/sessions/${sid}/frames`,
      { method: "POST", body: fd }
    );
  },

  verify: (sid: string, fraud_mode: boolean) =>
    req<VerifyResult>(`/sessions/${sid}/verify`, {
      method: "POST",
      body: form({ fraud_mode }),
    }),

  grade: (sid: string, fraud_mode: boolean) =>
    req<GradeResult>(`/sessions/${sid}/grade`, {
      method: "POST",
      body: form({ fraud_mode }),
    }),

  disposition: (sid: string) =>
    req<{ path: string; explanation: string; match_count: number; price: any }>(
      `/sessions/${sid}/disposition`,
      { method: "POST" }
    ),

  matches: (sid: string) =>
    req<{
      seller: { lat: number; lng: number };
      candidates: MatchCandidate[];
      demand_pins: { buyer_id: string; lat: number; lng: number }[];
      price: any;
      grade: string;
      certificate_id: string;
    }>(`/matches/${sid}`),

  reserve: (sid: string, buyer_id: string) =>
    req<{ transfer_id: string; tracking: string; label_url: string; pickup_window: string }>(
      `/matches/${sid}/reserve`,
      { method: "POST", body: form({ buyer_id }) }
    ),

  confirm: (transfer_id: string) =>
    req<{
      status: string;
      journey: {
        relay: { distance_km: number; warehouses: number; days: number; hops: number };
        old_world: { distance_km: number; warehouses: number; days: number };
        km_avoided: number;
        co2e_avoided_kg: number;
      };
    }>(`/transfers/${transfer_id}/confirm`, { method: "POST" }),

  certificate: (id: string) => req<any>(`/certificates/${id}`),

  opsServices: () =>
    req<{ ai_mode: string; services: { name: string; engine: string; status: string }[] }>(
      "/ops/services"
    ),
  opsMetrics: () => req<any>("/ops/metrics"),
  opsEvents: () => req<{ events: any[] }>("/ops/events"),

  buyerFeed: (buyer_id: string) =>
    req<{
      buyer_id: string;
      buyer_name: string;
      cards: {
        session_id: string;
        product_name: string;
        grade: string;
        price: number;
        distance_km: number;
        certificate_id: string;
        state: string;
        reserved: boolean;
        transfer_id: string | null;
        tracking: string | null;
        transfer_status: string | null;
        defect_count: number;
        identity_confidence: number | null;
      }[];
    }>(`/buyer/${buyer_id}/feed`),
};
