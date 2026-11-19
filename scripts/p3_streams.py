from np import *
import time
s = state(); conns = s["connections"]
STREAMS = [
 ("NP_Ecom_Customers", "NP Ecom Customers", "Northpeak_Commerce", "NpEcomCustomer", "Profile", "CustomerId", None),
 ("NP_Loyalty_Members", "NP Loyalty Members", "Northpeak_Loyalty", "NpLoyaltyMember", "Profile", "MemberId", None),
 ("NP_Orders", "NP Orders", "Northpeak_Commerce", "NpOrder", "Engagement", "OrderId", "OrderDate"),
 ("NP_Web_Events", "NP Web Events", "Northpeak_Commerce", "NpWebEvent", "Engagement", "EventId", "EventTimestamp"),
]
streams = s.get("streams", {})
for name, label, conn, schema, cat, pk, evt in STREAMS:
    if name in streams: continue
    dlo = {"label": label, "category": cat, "recordModifiedFieldName": "LastModified", "dataspaceInfo": [{"name": "default"}],
           "dataLakeFieldInputRepresentations": [{"name": pk, "label": pk, "dataType": "Text", "isPrimaryKey": True}]}
    if evt: dlo["eventDateTimeFieldName"] = evt
    body = {"label": label, "name": name, "datastreamType": "INGESTAPI",
            "connectorInfo": {"connectorType": "IngestApi", "connectorDetails": {"name": conns[conn]["name"], "events": [schema]}},
            "dataLakeObjectInfo": dlo, "refreshConfig": {"refreshMode": "UPSERT"}}
    r = api("POST", "data-streams", body)
    if isinstance(r, dict) and r.get("dataLakeObjectInfo"):
        streams[name] = {"stream": r.get("name"), "dlo": r["dataLakeObjectInfo"].get("name"), "status": r.get("status")}
        save(streams=streams); print(name, streams[name])
    else:
        print("FAIL", name, json.dumps(r)[:600])
    time.sleep(3)
