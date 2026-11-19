from np import *
import time
s = state(); st = s["streams"]

# wait for streams ACTIVE
for _ in range(30):
    r = api("GET", "data-streams?limit=200")
    stat = {d["name"]: d.get("status") for d in r.get("dataStreams", [])}
    pend = [v["stream"] for v in st.values() if stat.get(v["stream"]) != "ACTIVE"]
    if not pend: break
    print("waiting", pend); time.sleep(10)

def F(n, t, pk=False): return {"name": n, "label": n, "dataType": t, "isPrimaryKey": pk}
DMOS = {
 "NP_Loyalty_Member": ("NP Loyalty Member", "PROFILE", [F("MemberId","Text",True),F("CustomerRef","Text"),F("Tier","Text"),F("PointsBalance","Number"),
     F("LifetimePoints","Number"),F("JoinDate","Date"),F("HomeStoreId","Text"),F("LastModified","DateTime")]),
 "NP_Order": ("NP Order", "ENGAGEMENT", [F("OrderId","Text",True),F("CustomerId","Text"),F("OrderDate","DateTime"),F("Channel","Text"),F("StoreId","Text"),
     F("OrderTotal","Number"),F("ItemCount","Number"),F("PrimaryCategory","Text"),F("ProductCode","Text"),F("LastModified","DateTime")]),
 "NP_Web_Event": ("NP Web Event", "ENGAGEMENT", [F("EventId","Text",True),F("CustomerId","Text"),F("EventTimestamp","DateTime"),F("EventType","Text"),
     F("Category","Text"),F("ProductCode","Text"),F("SessionId","Text"),F("Weight","Number"),F("LastModified","DateTime")]),
}
dmos = s.get("dmos", {})
for name, (label, cat, fields) in DMOS.items():
    if name in dmos: continue
    r = api("POST", "data-model-objects", {"name": name, "label": label, "description": "Northpeak demo", "dataSpaceName": "default", "category": cat, "fields": fields})
    if isinstance(r, dict) and r.get("name"):
        dmos[name] = r["name"]; save(dmos=dmos); print("DMO", r["name"], r.get("id"))
    else:
        print("DMO FAIL", name, json.dumps(r)[:600])
time.sleep(10)

def m(pairs): return [{"sourceFieldDeveloperName": a + "__c", "targetFieldDeveloperName": b} for a, b in pairs]
E, L = st["NP_Ecom_Customers"]["dlo"], st["NP_Loyalty_Members"]["dlo"]
MAPS = [
 (E, "ssot__Individual__dlm", m([("CustomerId","ssot__Id__c"),("CustomerId","ssot__PartyId__c"),("FirstName","ssot__FirstName__c"),
                                 ("LastName","ssot__LastName__c"),("LastModified","ssot__LastModifiedDate__c")])),
 (E, "ssot__ContactPointEmail__dlm", m([("CustomerId","ssot__Id__c"),("CustomerId","ssot__PartyId__c"),("EmailAddress","ssot__EmailAddress__c")])),
 (E, "ssot__ContactPointPhone__dlm", m([("CustomerId","ssot__Id__c"),("CustomerId","ssot__PartyId__c"),("PhoneNumber","ssot__TelephoneNumber__c")])),
 (L, "ssot__Individual__dlm", m([("MemberId","ssot__Id__c"),("MemberId","ssot__PartyId__c"),("FirstName","ssot__FirstName__c"),
                                 ("LastName","ssot__LastName__c"),("LastModified","ssot__LastModifiedDate__c")])),
 (L, "ssot__ContactPointEmail__dlm", m([("MemberId","ssot__Id__c"),("MemberId","ssot__PartyId__c"),("EmailAddress","ssot__EmailAddress__c")])),
 (L, "ssot__ContactPointPhone__dlm", m([("MemberId","ssot__Id__c"),("MemberId","ssot__PartyId__c"),("PhoneNumber","ssot__TelephoneNumber__c")])),
 (L, "NP_Loyalty_Member__dlm", m([("MemberId","MemberId__c"),("MemberId","CustomerRef__c"),("Tier","Tier__c"),("PointsBalance","PointsBalance__c"),
     ("LifetimePoints","LifetimePoints__c"),("JoinDate","JoinDate__c"),("HomeStoreId","HomeStoreId__c"),("LastModified","LastModified__c")])),
 (st["NP_Orders"]["dlo"], "NP_Order__dlm", m([(x, x + "__c") for x in ["OrderId","CustomerId","OrderDate","Channel","StoreId","OrderTotal","ItemCount","PrimaryCategory","ProductCode","LastModified"]])),
 (st["NP_Web_Events"]["dlo"], "NP_Web_Event__dlm", m([(x, x + "__c") for x in ["EventId","CustomerId","EventTimestamp","EventType","Category","ProductCode","SessionId","Weight","LastModified"]])),
]
maps = s.get("maps", {})
for src, tgt, fm in MAPS:
    key = f"{src}->{tgt}"
    if key in maps: continue
    r = api("POST", "data-model-object-mappings", {"sourceEntityDeveloperName": src, "targetEntityDeveloperName": tgt, "fieldMapping": fm})
    if isinstance(r, dict) and r.get("status"):
        maps[key] = r.get("developerName"); save(maps=maps); print("MAP OK", key, r["status"], len(r.get("fieldMappings", [])))
    else:
        print("MAP FAIL", key, json.dumps(r)[:600])
    time.sleep(2)
