from np import *

T, N, B, D, DT = "Text", "Number", "Boolean", "Date", "DateTime"
def f(name, typ): return {"name": name, "label": name, "dataType": typ}

SCHEMAS = {
 "Northpeak_Commerce": [
  ("NpEcomCustomer", [("CustomerId",T),("FirstName",T),("LastName",T),("EmailAddress",T),("PhoneNumber",T),("City",T),("State",T),
                      ("PreferredStoreId",T),("MarketingOptIn",B),("SignupDate",D),("LastModified",DT)]),
  ("NpOrder", [("OrderId",T),("CustomerId",T),("OrderDate",DT),("Channel",T),("StoreId",T),("OrderTotal",N),("ItemCount",N),
               ("PrimaryCategory",T),("ProductCode",T),("LastModified",DT)]),
  ("NpWebEvent", [("EventId",T),("CustomerId",T),("EventTimestamp",DT),("EventType",T),("Category",T),("ProductCode",T),
                  ("SessionId",T),("Weight",N),("LastModified",DT)]),
 ],
 "Northpeak_Loyalty": [
  ("NpLoyaltyMember", [("MemberId",T),("FirstName",T),("LastName",T),("EmailAddress",T),("PhoneNumber",T),("Tier",T),
                       ("PointsBalance",N),("LifetimePoints",N),("JoinDate",D),("HomeStoreId",T),("LastModified",DT)]),
 ],
}

conns = state().get("connections", {})
for label, schemas in SCHEMAS.items():
    if label not in conns:
        r = api("POST", "connections", {"connectorType": "IngestApi", "label": label, "name": label})
        print(label, json.dumps(r)[:400])
        conns[label] = {"id": r["id"], "name": r["name"], "tenant": r.get("tenantSpecificEndpoint")}
        save(connections=conns)
    body = {"schemas": [{"label": s, "name": s, "schemaType": "IngestApi", "fields": [f(n, t) for n, t in flds]} for s, flds in schemas]}
    r = api("PUT", f"connections/{conns[label]['id']}/schema", body)
    print("schema", label, json.dumps(r)[:300])
    r = api("GET", f"connections/{conns[label]['id']}/schema")
    print("verify", label, [s["name"] for s in r.get("schemas", [])])
