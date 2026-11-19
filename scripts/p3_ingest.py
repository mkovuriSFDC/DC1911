from np import *
import sys, time
D = os.path.join(os.path.dirname(__file__), "..", "data", "out")
cdp, tenant = cdp_token()
JOBS = [("Northpeak_Commerce", "NpEcomCustomer", "ecom_customers.json"),
        ("Northpeak_Loyalty", "NpLoyaltyMember", "loyalty_members.json"),
        ("Northpeak_Commerce", "NpOrder", "orders.json"),
        ("Northpeak_Commerce", "NpWebEvent", "web_events.json")]
only = sys.argv[1:]
for conn, schema, fn in JOBS:
    if only and schema not in only: continue
    rows = json.load(open(os.path.join(D, fn)))
    ok = 0
    for i in range(0, len(rows), 300):
        batch = rows[i:i+300]
        code, resp = http("POST", f"https://{tenant}/api/v1/ingest/sources/{conn}/{schema}", cdp, {"data": batch})
        if code == 202: ok += len(batch)
        else: print("ERR", schema, i, code, str(resp)[:400])
        time.sleep(0.5)
    print(schema, f"accepted {ok}/{len(rows)}")
