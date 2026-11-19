from np import *
import csv
D = os.path.join(os.path.dirname(__file__), "..", "data", "out")
crm = {r["PersonKey"]: r["ContactId"] for r in csv.DictReader(open(os.path.join(D, "crm_ids.csv")))}
people = list(csv.DictReader(open(os.path.join(D, "personas.csv"))))
link = {}
off = 0
while True:
    r = sql(f"SELECT SourceRecordId__c, UnifiedRecordId__c FROM UnifiedLinkssotIndividualNpcu__dlm ORDER BY SourceRecordId__c LIMIT 1000 OFFSET {off}")
    rows = r.get("data", [])
    for x in rows: link[x["SourceRecordId__c"]] = x["UnifiedRecordId__c"]
    if len(rows) < 1000: break
    off += 1000
# Contact ids in Data Cloud are 18-char
def cid(k):
    v = crm.get(k)
    return v
stats = {"people": 0, "fully_unified": 0, "split": 0, "missing": 0}
by_mode = {}
split_list = []
uid_of = {}
for p in people:
    ids = [i for i in [cid(p["PersonKey"]), p["EcomId"] or None, p["LoyId"] or None] if i]
    uids = {link.get(i) for i in ids}
    stats["people"] += 1
    if None in uids: stats["missing"] += 1; continue
    if len(uids) == 1: stats["fully_unified"] += 1; uid_of[p["PersonKey"]] = uids.pop()
    else:
        stats["split"] += 1; split_list.append((p["PersonKey"], p["Sources"], p["LoyMatch"], p["First"], p["LoyFirst"], p["Last"]))
    m = p["LoyMatch"] or "n/a"
    if len(ids) > 1:
        by_mode.setdefault(m, [0, 0]); by_mode[m][0] += 1; by_mode[m][1] += (len(uids) == 1 if isinstance(uids, set) else 1)
uniq = set(uid_of.values())
print(stats, "distinct unified ids for Northpeak people:", len(set(link.get(i) for p in people for i in [cid(p['PersonKey']), p['EcomId'] or None, p['LoyId'] or None] if i)))
print("multi-source people by loyalty match mode [total, unified]:", by_mode)
print("split examples:", split_list[:12])
# near misses: must NOT share uid with their look-alike
nm = [(p["PersonKey"], p["NearMissOf"]) for p in people if p["NearMissOf"]]
print("near-miss merged wrongly:", [(a, b) for a, b in nm if a in uid_of and b in uid_of and uid_of[a] == uid_of[b]], "of", len(nm))
save(ir_stats={**stats, "by_mode": by_mode})
