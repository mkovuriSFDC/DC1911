"""Shared helpers for Northpeak build scripts."""
import json, os, subprocess, tempfile, urllib.request, urllib.parse

ORG = "salesforce-4ojg1d"
V = "v65.0"
STATE = os.path.join(os.path.dirname(__file__), "state.json")

def state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}

def save(**kw):
    s = state(); s.update(kw); json.dump(s, open(STATE, "w"), indent=1); return s

def api(method, path, body=None):
    if not path.startswith("/services"):
        path = f"/services/data/{V}/ssot/{path.lstrip('/')}"
    cmd = ["sf", "api", "request", "rest", path, "--method", method, "--target-org", ORG]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(body, tmp); tmp.close()
        cmd += ["--body", "@" + tmp.name]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if tmp: os.unlink(tmp.name)
    out = r.stdout.strip()
    try:
        return json.loads(out) if out else {}
    except Exception:
        return {"_raw": out[:2000], "_err": r.stderr[:2000]}

def token():
    r = subprocess.run(["sf", "org", "auth", "show-access-token", "--target-org", ORG, "--no-prompt", "--json"], capture_output=True, text=True)
    tok = json.loads(r.stdout)["result"]["accessToken"]
    r = subprocess.run(["sf", "org", "display", "--target-org", ORG, "--json"], capture_output=True, text=True)
    inst = json.loads(r.stdout)["result"]["instanceUrl"].rstrip("/")
    return tok, inst

def http(method, url, tok, body=None, ctype="application/json"):
    data = None
    if body is not None:
        data = body if isinstance(body, (bytes,)) else (urllib.parse.urlencode(body).encode() if ctype.startswith("application/x-www") else json.dumps(body).encode())
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization": f"Bearer {tok}", "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req) as resp:
            txt = resp.read().decode(); return resp.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else txt)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:2000]

def cdp_token():
    tok, inst = token()
    req = urllib.request.Request(f"{inst}/services/a360/token", method="POST",
        data=urllib.parse.urlencode({"grant_type": "urn:salesforce:grant-type:external:cdp", "subject_token": tok,
              "subject_token_type": "urn:ietf:params:oauth:token-type:access_token"}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    d = json.loads(urllib.request.urlopen(req).read().decode())
    return d["access_token"], d["instance_url"].replace("https://", "")

def sql(q):
    return api("POST", "query", {"sql": q})
