#!/usr/bin/env python3
"""Northpeak Outfitters demo data generator (deterministic)."""
import csv, json, os, random
from datetime import datetime, timedelta, timezone

random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
NOW_ISO = TODAY.strftime("%Y-%m-%dT%H:%M:%SZ")

def iso(d): return d.strftime("%Y-%m-%dT%H:%M:%SZ")
def rand_date(start, end):
    s, e = start.timestamp(), end.timestamp()
    return datetime.fromtimestamp(random.uniform(s, e), tz=timezone.utc)

# ---------------- Stores ----------------
STORE_CITIES = [("Denver","CO"),("Boulder","CO"),("Fort Collins","CO"),("Colorado Springs","CO"),("Golden","CO"),
 ("Breckenridge","CO"),("Durango","CO"),("Aspen","CO"),("Salt Lake City","UT"),("Park City","UT"),("Ogden","UT"),
 ("Provo","UT"),("Moab","UT"),("St. George","UT"),("Seattle","WA"),("Bellevue","WA"),("Tacoma","WA"),("Spokane","WA"),
 ("Bellingham","WA"),("Olympia","WA"),("Leavenworth","WA"),("Portland","OR"),("Bend","OR"),("Eugene","OR"),("Salem","OR"),
 ("Hood River","OR"),("Ashland","OR"),("Boise","ID"),("Sun Valley","ID"),("Missoula","MT"),("Bozeman","MT"),("Whitefish","MT"),
 ("Jackson","WY"),("Flagstaff","AZ"),("Sedona","AZ"),("Santa Fe","NM"),("Taos","NM"),("Reno","NV"),("Truckee","CA"),("Mammoth Lakes","CA")]
STORES = [{"StoreId": f"NP-S{i+1:02d}", "City": c, "State": s} for i, (c, s) in enumerate(STORE_CITIES)]
AREA = {"CO": ["303","720","970"], "UT": ["801","435"], "WA": ["206","425","509"], "OR": ["503","541","971"],
        "ID": ["208"], "MT": ["406"], "WY": ["307"], "AZ": ["928"], "NM": ["505"], "NV": ["775"], "CA": ["530"]}

# ---------------- Catalog ----------------
CATALOG_RAW = {
 "Tents": [("Ridgeline 2P Backpacking Tent",389),("Basecamp 4P Family Tent",529),("Alpine Ultralight 1P Tent",449),("Summit Expedition 3P Tent",649),("Trailhead Footprint",45)],
 "Sleeping Bags": [("Glacier -7C Down Sleeping Bag",379),("Meadow 4C Synthetic Bag",149),("Polar Expedition -18C Bag",599),("Insulated Sleeping Pad R5",179),("Silk Sleeping Bag Liner",69)],
 "Backpacks": [("Traverse 65L Trekking Pack",289),("Daybreak 28L Daypack",129),("Summit Push 40L Alpine Pack",219),("Kids Explorer 18L Pack",59),("Hydration Bladder 3L",39)],
 "Footwear": [("Cascade Mid GTX Hiking Boot",229),("Talus Approach Shoe",159),("Ridgewalker Leather Boot",289),("Camp Recovery Slide",49),("Merino Hiking Socks 3-Pack",45)],
 "Jackets": [("Stormshell 3L Rain Jacket",349),("Firecrest Down Parka",459),("Switchback Fleece Hoodie",119),("Alpine Softshell Jacket",229),("Packable Wind Shell",99)],
 "Climbing": [("Granite Climbing Harness",89),("Crag Dynamic Rope 60m",249),("Vertex Climbing Helmet",99),("Edge Climbing Shoes",169),("Quickdraw Set of 6",119)],
 "Camp Kitchen": [("Blaze Canister Stove",79),("Titanium Cook Set",129),("Trail Coffee Press",35),("Camp Kitchen Table",149),("Insulated Food Jar",39)],
 "Trail Running": [("Skyline Trail Running Shoe",159),("Ultra Vest 12L",139),("Trail Running Shorts",59),("Headlamp 400 Lumens",49),("Running Poles Carbon",169)],
}
CATALOG = []
n = 1
for fam, items in CATALOG_RAW.items():
    for name, price in items:
        CATALOG.append({"ProductCode": f"NP-{n:03d}", "Name": name, "Family": fam, "Price": price}); n += 1
CATS = list(CATALOG_RAW.keys())
BY_CAT = {c: [p for p in CATALOG if p["Family"] == c] for c in CATS}

# ---------------- People ----------------
FIRST = [("William","Bill"),("Katherine","Kate"),("Robert","Bob"),("Elizabeth","Liz"),("Michael","Mike"),("Jennifer","Jen"),
 ("Christopher","Chris"),("Margaret","Maggie"),("Daniel","Dan"),("Rebecca","Becky"),("Matthew","Matt"),("Samantha","Sam"),
 ("Joseph","Joe"),("Alexandra","Alex"),("Anthony","Tony"),("Victoria","Vicky"),("Nicholas","Nick"),("Patricia","Pat"),
 ("Benjamin","Ben"),("Jessica","Jess"),("Thomas","Tom"),("Stephanie","Steph"),("Andrew","Andy"),("Natalie","Nat"),
 ("James","Jim"),("Olivia","Liv"),("Jonathan","Jon"),("Abigail","Abby"),("Timothy","Tim"),("Kimberly","Kim"),
 ("Emma",None),("Noah",None),("Liam",None),("Ava",None),("Mia",None),("Ethan",None),("Sofia",None),("Lucas",None),
 ("Chloe",None),("Mason",None),("Harper",None),("Logan",None),("Aria",None),("Owen",None),("Maya",None),("Caleb",None),
 ("Priya",None),("Diego",None),("Hana",None),("Mateo",None),("Aiko",None),("Ravi",None),("Ingrid",None),("Tariq",None)]
LAST = ["Anderson","Brooks","Carter","Dawson","Ellison","Fischer","Garcia","Hughes","Iverson","Jensen","Kowalski","Larsen",
 "Moreno","Nakamura","Olsen","Patel","Quinn","Ramirez","Sorensen","Thompson","Underwood","Vasquez","Whitaker","Yamada",
 "Zimmerman","Bennett","Chandler","Delgado","Erikson","Fletcher","Gallagher","Hartley","Ingram","Jacobs","Keller","Lindqvist",
 "McAllister","Novak","Ortega","Pearson","Reyes","Sullivan","Tanaka","Vaughn","Walsh","Abbott","Bishop","Coleman","Draper",
 "Everett","Foster","Griffin","Holloway","Kim","Lopez","Mercer","Nguyen","Okafor","Price","Rossi","Schmidt","Torres","Weber"]
TYPO = {"Katherine":"Katharine","Rebecca":"Rebeca","Jennifer":"Jenifer","Stephanie":"Stefanie","Natalie":"Nathalie",
        "Jonathan":"Jonathon","Abigail":"Abigale","Kimberly":"Kimberley","Matthew":"Mathew","Nicholas":"Nicolas",
        "Sofia":"Sophia","Aria":"Arya","Maya":"Maia","Caleb":"Kaleb","Chloe":"Khloe"}

used_names, used_emails, used_phones = set(), set(), set()
def unique_phone(state):
    while True:
        p = f"+1{random.choice(AREA[state])}555{random.randint(1000,9999)}"
        if p not in used_phones: used_phones.add(p); return p
def unique_email(local, domain):
    e, i = f"{local}@{domain}", 2
    while e in used_emails: e = f"{local}{i}@{domain}"; i += 1
    used_emails.add(e); return e

def new_person(idx, first=None, last=None):
    if first is None:
        while True:
            f, nick = random.choice(FIRST); l = random.choice(LAST)
            if (f, l) not in used_names: break
    else:
        f, nick, l = first[0], first[1], last
    used_names.add((f, l))
    store = random.choice(STORES)
    return {"PersonKey": f"P{idx:03d}", "First": f, "Nick": nick, "Last": l, "Store": store,
            "Email": unique_email(f"{f.lower()}.{l.lower()}", random.choice(["example.com","example.com","example.org"])),
            "Phone": unique_phone(store["State"])}

people = [new_person(i + 1) for i in range(195)]
# 5 deliberate near-miss pairs: same first+last as an existing person, different contact details -> must NOT merge
nm_people = []
for j in range(5):
    base = people[j * 7 + 3]
    used_names.discard((base["First"], base["Last"]))
    p = new_person(196 + j, first=(base["First"], base["Nick"]), last=base["Last"])
    p["NearMissOf"] = base["PersonKey"]; nm_people.append(p)
people += nm_people

# ---------------- Source coverage ----------------
groups = ["CEL"] * 50 + ["CE"] * 35 + ["EL"] * 30 + ["CL"] * 15 + ["C"] * 20 + ["E"] * 30 + ["L"] * 20
random.shuffle(groups)
for p, g in zip(people, groups): p["Sources"] = g
for p in nm_people: p["Sources"] = random.choice(["C", "E", "CE"])

# ---------------- Personas (only people with an e-com id have orders/web) ----------------
ecom_people = [p for p in people if "E" in p["Sources"]]
cel = [p for p in ecom_people if p["Sources"] == "CEL"]
others = [p for p in ecom_people if p["Sources"] != "CEL"]
random.shuffle(cel); random.shuffle(others)
at_risk = cel[:15] + others[:10]
rest = cel[15:] + others[10:]; random.shuffle(rest)
loyal, browsers, casual = rest[:30], rest[30:70], rest[70:]
for grp, name in [(at_risk,"HighValueAtRisk"),(loyal,"LoyalHighValue"),(browsers,"Browser"),(casual,"Casual")]:
    for p in grp: p["Persona"] = name
for p in people: p.setdefault("Persona", "StoreOnly")

# ---------------- Source records ----------------
crm, ecom, loy = [], [], []
eid, lid = 10001, 50001
def email_variant(e):
    r = random.random()
    if r < 0.35: return e.upper() if random.random() < 0.3 else e.title()
    if r < 0.5: return f"  {e} "
    return e

for p in people:
    p["Favs"] = random.sample(CATS, 2)
    if "C" in p["Sources"]:
        p["CrmEmail"] = email_variant(p["Email"]) .strip()
        crm.append({"PersonKey": p["PersonKey"], "FirstName": p["First"], "LastName": p["Last"], "Email": p["CrmEmail"].strip().lower() if random.random()<0.5 else p["CrmEmail"].strip(),
                    "Phone": p["Phone"], "MailingCity": p["Store"]["City"], "MailingState": p["Store"]["State"]})
    if "E" in p["Sources"]:
        p["EcomId"] = f"ECOM-{eid}"; eid += 1
        signup = rand_date(datetime(2023,1,1,tzinfo=timezone.utc), datetime(2025,6,1,tzinfo=timezone.utc))
        ecom.append({"CustomerId": p["EcomId"], "FirstName": p["First"], "LastName": p["Last"], "EmailAddress": email_variant(p["Email"]),
                     "PhoneNumber": p["Phone"], "City": p["Store"]["City"], "State": p["Store"]["State"],
                     "PreferredStoreId": p["Store"]["StoreId"], "MarketingOptIn": random.random() < 0.7,
                     "SignupDate": signup.strftime("%Y-%m-%d"), "LastModified": NOW_ISO})
    if "L" in p["Sources"]:
        p["LoyId"] = f"LOY-{lid}"; lid += 1
        r = random.random()
        first, email = p["First"], email_variant(p["Email"])
        if r < 0.4:   # personal email differs -> must match on name + phone
            email = unique_email(f"{p['First'][0].lower()}{p['Last'].lower()}{random.randint(10,99)}", "example.net")
            mode = random.random()
            if mode < 0.4 and p["Nick"]: first = p["Nick"]
            elif mode < 0.7 and p["First"] in TYPO: first = TYPO[p["First"]]
            p["LoyMatch"] = "name+phone"
        else:
            p["LoyMatch"] = "email"
        p["LoyFirst"], p["LoyEmail"] = first, email
        loy.append({"MemberId": p["LoyId"], "FirstName": first, "LastName": p["Last"], "EmailAddress": email, "PhoneNumber": p["Phone"],
                    "Tier": "Base Camp", "PointsBalance": 0, "LifetimePoints": 0,
                    "JoinDate": rand_date(datetime(2022,3,1,tzinfo=timezone.utc), datetime(2025,9,1,tzinfo=timezone.utc)).strftime("%Y-%m-%d"),
                    "HomeStoreId": p["Store"]["StoreId"], "LastModified": NOW_ISO})

# ---------------- Orders ----------------
orders, oid = [], 700001
def make_order(p, d, big=False):
    global oid
    cat = random.choice(p["Favs"]) if random.random() < 0.7 else random.choice(CATS)
    items = random.sample(BY_CAT[cat], random.randint(1, 3 if big else 2))
    if big and max(i["Price"] for i in items) < 200:
        items.append(max(BY_CAT[cat], key=lambda x: x["Price"]))
    total = round(sum(i["Price"] for i in items) * random.uniform(0.85, 1.0), 2)
    web = random.random() < 0.55
    orders.append({"OrderId": f"ORD-{oid}", "CustomerId": p["EcomId"], "OrderDate": iso(d), "Channel": "Web" if web else "Store",
                   "StoreId": "WEB" if web else (p["Store"]["StoreId"] if random.random()<0.8 else random.choice(STORES)["StoreId"]),
                   "OrderTotal": total, "ItemCount": len(items), "PrimaryCategory": cat, "ProductCode": items[0]["ProductCode"],
                   "LastModified": NOW_ISO}); oid += 1
    p.setdefault("Bought", set()).add(items[0]["ProductCode"])
    return total

START = datetime(2024, 11, 20, tzinfo=timezone.utc)
for p in ecom_people:
    spend = 0
    if p["Persona"] == "HighValueAtRisk":
        while spend < 1700:
            spend += make_order(p, rand_date(START, datetime(2026, 4, 30, tzinfo=timezone.utc)), big=True)
    elif p["Persona"] == "LoyalHighValue":
        while spend < 1600:
            spend += make_order(p, rand_date(START, TODAY - timedelta(days=2)), big=True)
        make_order(p, rand_date(TODAY - timedelta(days=90), TODAY - timedelta(days=1)))
    elif p["Persona"] == "Browser":
        for _ in range(random.randint(0, 2)):
            spend += make_order(p, rand_date(START, TODAY))
    else:
        for _ in range(random.randint(1, 4)):
            spend += make_order(p, rand_date(START, TODAY))
    p["Spend"] = round(spend, 2)

# ---------------- Web events ----------------
web, wid, sid = [], 1, 1
W = {"page_view":1, "product_view":2, "search":1, "add_to_cart":3, "wishlist":3}
def session(p, d):
    global wid, sid
    cat = random.choice(p["Favs"]) if random.random() < 0.75 else random.choice(CATS)
    for k in range(random.randint(3, 6)):
        et = random.choices(list(W), weights=[30, 40, 10, 12, 8])[0]
        prod = random.choice(BY_CAT[cat])
        web.append({"EventId": f"WEB-{wid:06d}", "CustomerId": p["EcomId"], "EventTimestamp": iso(d + timedelta(minutes=2*k)),
                    "EventType": et, "Category": cat, "ProductCode": "" if et in ("page_view","search") else prod["ProductCode"],
                    "SessionId": f"S-{sid:06d}", "Weight": W[et], "LastModified": NOW_ISO}); wid += 1
    sid += 1

for p in ecom_people:
    per = p["Persona"]
    if per == "Browser":
        for _ in range(random.randint(7, 10)): session(p, rand_date(TODAY - timedelta(days=150), TODAY))
        for _ in range(random.randint(2, 4)): session(p, rand_date(TODAY - timedelta(days=28), TODAY - timedelta(hours=3)))
    elif per == "LoyalHighValue":
        for _ in range(random.randint(4, 6)): session(p, rand_date(TODAY - timedelta(days=300), TODAY))
        session(p, rand_date(TODAY - timedelta(days=25), TODAY))
    elif per == "Casual":
        for _ in range(random.randint(1, 4)): session(p, rand_date(TODAY - timedelta(days=360), TODAY))
    elif per == "HighValueAtRisk":
        for _ in range(random.randint(0, 2)): session(p, rand_date(TODAY - timedelta(days=360), TODAY - timedelta(days=200)))

# ---------------- Loyalty tiers from total value ----------------
for row in loy:
    p = next(x for x in people if x.get("LoyId") == row["MemberId"])
    value = p.get("Spend", 0) + random.uniform(100, 900)   # store purchases outside e-com too
    row["LifetimePoints"] = int(value * 10)
    row["PointsBalance"] = int(row["LifetimePoints"] * random.uniform(0.15, 0.6))
    row["Tier"] = "Summit" if value >= 1800 else ("Trailblazer" if value >= 800 else "Base Camp")
    p["Tier"] = row["Tier"]

# ---------------- Write ----------------
def wcsv(name, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
def wjson(name, rows):
    with open(os.path.join(OUT, name), "w") as f: json.dump(rows, f, indent=1)

wcsv("crm_contacts.csv", crm)
wjson("ecom_customers.json", ecom); wjson("loyalty_members.json", loy)
wjson("orders.json", orders); wjson("web_events.json", web)
wcsv("products.csv", CATALOG); wjson("stores.json", STORES)
wcsv("personas.csv", [{"PersonKey": p["PersonKey"], "First": p["First"], "Last": p["Last"], "Email": p["Email"], "Phone": p["Phone"],
      "Sources": p["Sources"], "Persona": p["Persona"], "EcomId": p.get("EcomId",""), "LoyId": p.get("LoyId",""),
      "LoyMatch": p.get("LoyMatch",""), "LoyFirst": p.get("LoyFirst",""), "Spend": p.get("Spend",0), "Tier": p.get("Tier",""),
      "NearMissOf": p.get("NearMissOf",""), "Favs": "|".join(p["Favs"])} for p in people])
print(f"people={len(people)} crm={len(crm)} ecom={len(ecom)} loyalty={len(loy)} source_records={len(crm)+len(ecom)+len(loy)}")
print(f"orders={len(orders)} web_events={len(web)} products={len(CATALOG)}")
print("personas:", {k: sum(1 for p in people if p['Persona']==k) for k in ['HighValueAtRisk','LoyalHighValue','Browser','Casual','StoreOnly']})
print("loyalty match modes:", {k: sum(1 for p in people if p.get('LoyMatch')==k) for k in ['email','name+phone']})
