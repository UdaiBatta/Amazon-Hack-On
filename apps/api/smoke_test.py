"""End-to-end smoke test of the full demo spine (happy path + fraud path).

Run: .venv/bin/python smoke_test.py
"""
from starlette.testclient import TestClient

from main import app

c = TestClient(app)


def line(label, val):
    print(f"  {label:28} {val}")


def happy_path():
    print("\n=== HAPPY PATH ===")
    r = c.post("/sessions", data={"sku": "SKU-HP-01"}).json()
    sid = r["session_id"]
    line("session", sid)
    line("checklist steps", [s["key"] for s in r["checklist"]])

    for step in r["checklist"]:
        fr = c.post(f"/sessions/{sid}/frames", data={"step_key": step["key"]}).json()
        assert fr["accepted"], fr
    line("scan_complete", fr["scan_complete"])

    v = c.post(f"/sessions/{sid}/verify", data={"fraud_mode": "false"}).json()
    line("identity_confidence", v["identity_confidence"])
    line("serial_match", v["serial_match"])
    line("trust_passed", v["trust_passed"])
    assert v["trust_passed"]

    g = c.post(f"/sessions/{sid}/grade", data={"fraud_mode": "false"}).json()
    line("grade", g["grade"])
    line("score", g["score"])
    line("resale", g["price"]["resale_value"])
    line("ai_source", g["ai_source"])
    cert_id = g["certificate_id"]

    d = c.post(f"/sessions/{sid}/disposition").json()
    line("disposition", d["path"])
    assert d["path"] == "DIRECT_RELAY", d

    m = c.get(f"/matches/{sid}").json()
    top = m["candidates"][0]
    line("top buyer", f'{top["buyer_name"]} @ {top["distance_km"]} km')
    line("demand pins", len(m["demand_pins"]))

    res = c.post(f"/matches/{sid}/reserve", data={"buyer_id": top["buyer_id"]}).json()
    line("tracking", res["tracking"])

    cert = c.get(f"/certificates/{cert_id}").json()
    line("certificate grade", cert["grade"])
    line("custody events", len(cert["custody_timeline"]))

    # find transfer id
    conf = c.post(f"/transfers/{res['transfer_id']}/confirm").json()
    line("journey relay km", conf["journey"]["relay"]["distance_km"])
    line("km avoided", conf["journey"]["km_avoided"])
    assert conf["refund_released"]


def fraud_path():
    print("\n=== FRAUD PATH (swap unit) ===")
    r = c.post("/sessions", data={"sku": "SKU-HP-01"}).json()
    sid = r["session_id"]
    for step in r["checklist"]:
        c.post(f"/sessions/{sid}/frames", data={"step_key": step["key"]})
    v = c.post(f"/sessions/{sid}/verify", data={"fraud_mode": "true"}).json()
    line("detected_serial", v["detected_serial"])
    line("expected_serial", v["expected_serial"])
    line("verdict", v["verdict"])
    line("trust_passed", v["trust_passed"])
    line("flags", v["behavioral_flags"])
    assert not v["trust_passed"], "fraud should be caught"
    assert v["verdict"] == "fraud"


def ops_check():
    print("\n=== OPS ===")
    s = c.get("/ops/services").json()
    line("ai_mode", s["ai_mode"])
    line("services", len(s["services"]))
    mt = c.get("/ops/metrics").json()
    line("fraud_caught", mt["fraud_caught"])


def buyer_feed():
    print("\n=== BUYER FEED ===")
    # run a fresh happy path so a match exists for Rohan
    r = c.post("/sessions", data={"sku": "SKU-HP-01"}).json()
    sid = r["session_id"]
    for step in r["checklist"]:
        c.post(f"/sessions/{sid}/frames", data={"step_key": step["key"]})
    c.post(f"/sessions/{sid}/verify", data={"fraud_mode": "false"})
    c.post(f"/sessions/{sid}/grade", data={"fraud_mode": "false"})
    c.post(f"/sessions/{sid}/disposition")

    feed = c.get("/buyer/buyer_rohan/feed").json()
    line("buyer", feed["buyer_name"])
    line("cards", len(feed["cards"]))
    assert feed["cards"], "Rohan should see the match"
    card = feed["cards"][0]
    line("card grade/price", f'{card["grade"]} / ₹{card["price"]}')
    line("reserved", card["reserved"])
    assert not card["reserved"]

    # buyer reserves
    res = c.post(f"/matches/{sid}/reserve", data={"buyer_id": "buyer_rohan"}).json()
    tid = res["transfer_id"]
    # idempotent: reserving again returns the same transfer
    res2 = c.post(f"/matches/{sid}/reserve", data={"buyer_id": "buyer_rohan"}).json()
    line("idempotent reserve", res2["transfer_id"] == tid)
    assert res2["transfer_id"] == tid

    feed2 = c.get("/buyer/buyer_rohan/feed").json()
    line("now reserved", feed2["cards"][0]["reserved"])
    assert feed2["cards"][0]["reserved"]

    conf = c.post(f"/transfers/{tid}/confirm").json()
    line("confirmed km", conf["journey"]["relay"]["distance_km"])


if __name__ == "__main__":
    happy_path()
    fraud_path()
    buyer_feed()
    ops_check()
    print("\nALL SMOKE TESTS PASSED ✅")
