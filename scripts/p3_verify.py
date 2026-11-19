from np import *
s = state(); st = s["streams"]
def count(t, where=""):
    r = sql(f"SELECT COUNT(*) AS c FROM {t} {where}")
    try: return r["data"][0][0] if isinstance(r["data"][0], list) else list(r["data"][0].values())[0]
    except Exception: return json.dumps(r)[:200]
for k, v in st.items(): print("DLO", k, count(v["dlo"]))
for t in ["NP_Order__dlm", "NP_Web_Event__dlm", "NP_Loyalty_Member__dlm"]: print("DMO", t, count(t))
print("Individual ECOM", count("ssot__Individual__dlm", "WHERE ssot__Id__c LIKE 'ECOM-%'"))
print("Individual LOY", count("ssot__Individual__dlm", "WHERE ssot__Id__c LIKE 'LOY-%'"))
print("Individual NP contacts", count("ssot__Individual__dlm", "WHERE ssot__PrimaryAccountId__c = '001gL00002AVRtDQAX'"))
print("CPEmail ECOM/LOY", count("ssot__ContactPointEmail__dlm", "WHERE ssot__Id__c LIKE 'ECOM-%' OR ssot__Id__c LIKE 'LOY-%'"))
print("CPPhone ECOM/LOY", count("ssot__ContactPointPhone__dlm", "WHERE ssot__Id__c LIKE 'ECOM-%' OR ssot__Id__c LIKE 'LOY-%'"))
