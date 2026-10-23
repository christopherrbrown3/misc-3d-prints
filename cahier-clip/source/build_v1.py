#!/usr/bin/env python3
"""Cahier clip-on page marker v1 — SolidCraft MCP build.

One-piece spring clip for a Moleskine Cahier pocket (90x140 page):
U-profile (bottom plate + bridge + top tongue with lead-in ramp),
30 mm wide, 0.9 mm walls, 1.1 mm grip gap, 'CRB' engraved on the tongue.
Profile sketch in XY (x = depth into book, y = stack), extruded along Z.
"""
import json, subprocess, sys, os

CLI = os.path.expanduser("~/workspace/solidcraft/target/debug/solidcraft-cli")
OUT = os.path.expanduser("~/workspace/solidcraft/cahier-clip")
os.makedirs(OUT, exist_ok=True)

proc = subprocess.Popen(
    [CLI, "mcp", "--allow-path", OUT],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr,
    text=True, bufsize=1,
)

rid = 0
def call(method, params=None):
    global rid
    rid += 1
    msg = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        msg["params"] = params
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    resp = json.loads(proc.stdout.readline())
    if "error" in resp:
        raise RuntimeError(f"{method} error: {resp['error']}")
    return resp.get("result")

def tool(name, args):
    r = call("tools/call", {"name": name, "arguments": args})
    out = []
    for c in r.get("content", []):
        if c.get("type") == "text":
            try: out.append(json.loads(c["text"]))
            except Exception: out.append({"_raw": c["text"][:300]})
    return out

def batch(cmds, label):
    r = tool("batch", {"commands": cmds, "verbose": False})
    ok = r[0].get("ok")
    print(f"[{label}] ok={ok} completed={r[0].get('completed')}")
    if not ok:
        print("FAILED:", json.dumps(r[0].get("failed"), indent=1)[:800])
    return ok

def measure(label):
    r = tool("measure", {})
    print(f"[measure {label}]", json.dumps(r)[:400])
    return r

init = call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "cahier-clip", "version": "1"}})
print("server:", init["serverInfo"]["name"], init["serverInfo"]["version"])
proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
proc.stdin.flush()

tool("new_design", {"name": "CahierClip"})

# --- stage 1: U-profile + extrude 30 mm wide ---
profile = [[0, 0], [44, 0], [44, 0.9], [2, 0.9], [2, 2.0],
           [33, 2.0], [37, 1.65], [37, 2.9], [0, 2.9]]
# shoelace expected area
area = 0.0
for i in range(len(profile)):
    x1, y1 = profile[i]; x2, y2 = profile[(i + 1) % len(profile)]
    area += x1 * y2 - x2 * y1
print("expected profile area mm^2:", abs(area) / 2, "-> volume ~", abs(area) / 2 * 30)

ok = batch([
    {"command": "sketch.create", "params": {"plane": "XY", "name": "Profile"}},
    {"command": "sketch.line", "params": {"points": profile, "closed": True}},
    {"command": "sketch.finish", "params": {}},
    {"command": "solid.extrude", "params": {"distance": 30, "name": "ClipBody"}},
], "profile extrude")
if not ok: sys.exit(1)
m1 = measure("after body")

# --- stage 2: CRB monogram engraved on the tongue top face (y = 2.9) ---
ok = batch([
    {"command": "sketch.create", "params": {
        "plane": {"origin": [0, 2.9, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]},
        "name": "Monogram"}},
    {"command": "sketch.text", "params": {"text": "CRB", "at": [10, 11.5], "height": 7}},
    {"command": "sketch.finish", "params": {}},
    {"command": "solid.extrude", "params": {"sketch": "Monogram", "distance": 0.35,
                                            "operation": "cut", "name": "Engrave"}},
], "monogram engrave")
m2 = measure("after engrave")

# --- stage 3: try small fillets on bridge outer corners + tongue tip top edge ---
for pt in ([0, 0, 15], [0, 2.9, 15], [37, 2.9, 15]):
    r = tool("execute", {"command": "solid.fillet",
                         "params": {"edges": [pt], "radius": 0.6}})
    print("fillet", pt, "->", json.dumps(r)[:220])
measure("final")

r = tool("inspect_design", {})
print("inspect:", json.dumps(r)[:600])

r = tool("screenshot", {"path": os.path.join(OUT, "cahier-clip.png")})
print("screenshot:", json.dumps(r)[:200])

r = tool("export", {"format": "stl", "path": os.path.join(OUT, "cahier-clip.stl")})
print("export:", json.dumps(r)[:300])

r = tool("save", {"path": os.path.join(OUT, "cahier-clip.solidcraft")})
print("save:", json.dumps(r)[:200])
proc.kill()
print("DONE")
