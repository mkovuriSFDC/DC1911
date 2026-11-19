from np import *
import csv, statistics
D = os.path.join(os.path.dirname(__file__), "..", "data", "out")
people = {p["EcomId"]: p for p in csv.DictReader(open(os.path.join(D, "personas.csv"))) if p["EcomId"]}
ltv = sql("SELECT UnifiedIndividualId__c, LifetimeSpend__c, OrderCount__c, Orders180d__c, LtvScore__c, LastOrderDate__c FROM NP_Customer_LTV__cio").get("data", [])
web = sql("SELECT UnifiedIndividualId__c, WebEngagementScore__c, Events30d__c, SessionCount__c FROM NP_Web_Engagement__cio").get("data", [])
print("LTV rows", len(ltv), "WEB rows", len(web))
link = {}
for x in sql("SELECT SourceRecordId__c, UnifiedRecordId__c FROM UnifiedLinkssotIndividualNpcu__dlm WHERE SourceRecordId__c LIKE 'ECOM-%'").get("data", []):
    link[x["UnifiedRecordId__c"]] = x["SourceRecordId__c"]
L = {r["UnifiedIndividualId__c"]: r for r in ltv}; W = {r["UnifiedIndividualId__c"]: r for r in web}
by = {}
for uid, r in L.items():
    per = people.get(link.get(uid), {}).get("Persona", "?")
    by.setdefault(per, []).append(float(r["LtvScore__c"]))
for k, v in by.items(): print(f"LTV score {k}: n={len(v)} min={min(v):.0f} median={statistics.median(v):.0f} max={max(v):.0f}")
wb = {}
for uid, r in W.items():
    per = people.get(link.get(uid), {}).get("Persona", "?")
    wb.setdefault(per, []).append(float(r["WebEngagementScore__c"]))
for k, v in wb.items(): print(f"WEB score {k}: n={len(v)} min={min(v):.0f} median={statistics.median(v):.0f} max={max(v):.0f}")
ar = [u for u, r in L.items() if float(r["LifetimeSpend__c"]) >= 1500 and float(r["Orders180d__c"]) == 0 and float((W.get(u) or {}).get("Events30d__c") or 0) <= 2]
print("rule-based at-risk:", len(ar), "personas:", sorted(set(people.get(link.get(u), {}).get("Persona", "?") for u in ar)),
      "planted found:", sum(1 for u in ar if people.get(link.get(u), {}).get("Persona") == "HighValueAtRisk"), "/25")
print("sample:", ltv[:2], web[:2])
