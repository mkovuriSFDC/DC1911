from np import *
import time, sys
L = "UnifiedLinkssotIndividualNpcu__dlm"
def dint(col): return f"(YEAR({col})*10000+MONTH({col})*100+DAY({col}))"
od, ts = "NP_Order__dlm.OrderDate__c", "NP_Web_Event__dlm.EventTimestamp__c"
LTV = (f"SELECT {L}.UnifiedRecordId__c AS UnifiedIndividualId__c, "
       f"SUM(NP_Order__dlm.OrderTotal__c) AS LifetimeSpend__c, "
       f"COUNT(NP_Order__dlm.OrderId__c) AS OrderCount__c, "
       f"MAX({od}) AS LastOrderDate__c, "
       f"SUM(CASE WHEN {dint(od)} >= 20260523 THEN 1 ELSE 0 END) AS Orders180d__c, "
       f"SUM(NP_Order__dlm.OrderTotal__c * CASE WHEN {dint(od)} >= 20260523 THEN 0.04 WHEN {dint(od)} >= 20251119 THEN 0.028 ELSE 0.016 END) AS LtvScore__c "
       f"FROM NP_Order__dlm JOIN {L} ON NP_Order__dlm.CustomerId__c = {L}.SourceRecordId__c "
       f"GROUP BY {L}.UnifiedRecordId__c")
WEB = (f"SELECT {L}.UnifiedRecordId__c AS UnifiedIndividualId__c, "
       f"SUM(NP_Web_Event__dlm.Weight__c * CASE WHEN {dint(ts)} >= 20261020 THEN 3 WHEN {dint(ts)} >= 20260821 THEN 1.5 ELSE 0.5 END) AS WebEngagementScore__c, "
       f"SUM(CASE WHEN {dint(ts)} >= 20261020 THEN 1 ELSE 0 END) AS Events30d__c, "
       f"APPROX_COUNT_DISTINCT(NP_Web_Event__dlm.SessionId__c) AS SessionCount__c, "
       f"MAX({ts}) AS LastWebVisit__c "
       f"FROM NP_Web_Event__dlm JOIN {L} ON NP_Web_Event__dlm.CustomerId__c = {L}.SourceRecordId__c "
       f"GROUP BY {L}.UnifiedRecordId__c")
CIS = {"NP_Customer_LTV": ("Northpeak Customer Lifetime Value", "Lifetime spend, order recency and recency-weighted LTV score per unified customer", LTV),
       "NP_Web_Engagement": ("Northpeak Web Engagement", "Recency-weighted web engagement score per unified customer", WEB)}
for api_name, (label, desc, expr) in CIS.items():
    r = api("POST", "calculated-insights", {"apiName": api_name, "displayName": label, "description": desc, "definitionType": "CALCULATED_METRIC",
        "expression": expr, "publishScheduleInterval": "TWELVE", "publishScheduleStartDateTime": "2026-11-20T02:00:00.000Z"})
    print(api_name, json.dumps(r)[:500])
