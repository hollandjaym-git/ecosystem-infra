#!/usr/bin/env python3
"""Daily-ish advisory watch: tells Telegram the day a Node/PHP/npm security fix lands that we have not applied.

Read-only and stdlib-only, like digest.py (it reuses its env loader and Telegram sender). Checks:
  * Node runtime  - every running container's `node -v` vs the newest release on its major line
                    (nodejs.org/dist/index.json), flagging security releases and end-of-life majors (endoflife.date).
  * npm packages  - every package-lock.json in the app checkouts, queried against OSV (api.osv.dev).
                    HIGH/CRITICAL on production deps pages; moderate/low are only counted.
  * PHP           - nothing runs PHP today; if a php image/container ever appears it is compared to php.net, and a
                    new upstream PHP release is mentioned once as FYI.

It only messages when something is NEW (or still unpatched after REMIND_DAYS), plus a "resolved" note when a
finding clears, so quiet days are silent. A crash sends "CVE watch FAILED". State: state/cve-watch.json.

  python3 cve_watch.py --dry-run     # print what it would send, send nothing, save nothing
  python3 cve_watch.py --status      # print everything currently open
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digest import load_env, run, telegram  # noqa: E402

HERE = Path(__file__).resolve().parent
REMIND_DAYS = 3
UA = {"user-agent": "alpinepost-cve-watch/1.0"}
LOCK_GLOBS = os.environ.get("CVE_WATCH_LOCK_GLOBS", "").split(",") if os.environ.get("CVE_WATCH_LOCK_GLOBS") else [
    "/home/deploy/*/backend/package-lock.json", "/home/deploy/*/frontend/package-lock.json"]
SEV_RANK = {"LOW": 1, "MODERATE": 2, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def get_json(url, body=None, timeout=25):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={**UA, "content-type": "application/json"} if body is not None else UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


# ── Node runtime ───────────────────────────────────────────────────────────────────────────────
def node_findings():
    index = get_json("https://nodejs.org/dist/index.json")
    try:
        eol = {str(r["cycle"]): r for r in get_json("https://endoflife.date/api/nodejs.json")}
    except Exception:
        eol = {}
    latest = {}  # major -> newest release dict
    for rel in index:  # index is newest-first
        major = rel["version"].lstrip("v").split(".")[0]
        latest.setdefault(major, rel)

    out = []
    rc, names, _ = run(["docker", "ps", "--format", "{{.Names}}|{{.Image}}"])
    for line in names.splitlines():
        name, _, image = line.partition("|")
        rc, ver, _ = run(["docker", "exec", name, "node", "-v"], timeout=15)
        if rc != 0 or not ver.strip().startswith("v"):
            continue
        cur = ver.strip().lstrip("v")
        major = cur.split(".")[0]
        want = latest.get(major)
        e = eol.get(major)
        if e and str(e.get("eol")) not in ("False", "false") and str(e.get("eol")) <= datetime.now(timezone.utc).strftime("%Y-%m-%d"):
            out.append((f"node-eol:{name}", "crit", f"{name} runs Node {cur} (line {major} is end-of-life since {e['eol']}, no more fixes)",
                        f"Move {name}'s Dockerfile to a supported node:<N>-alpine and rebuild"))
        elif want and vtuple(want["version"].lstrip("v")) > vtuple(cur):
            new = want["version"].lstrip("v")
            sec = bool(want.get("security"))
            # any release between cur and newest on this line flagged security?
            sec = sec or any(r.get("security") and r["version"].lstrip("v").split(".")[0] == major
                             and vtuple(r["version"].lstrip("v")) > vtuple(cur) for r in index)
            out.append((f"node:{name}:{new}", "crit" if sec else "warn",
                        f"{name} runs Node {cur}; {new} is out" + (" (SECURITY release)" if sec else ""),
                        "docker pull node:%s-alpine && rebuild with --pull (docker compose up -d --build --pull always <backend>)" % major))
    return out


# ── npm via OSV ────────────────────────────────────────────────────────────────────────────────
def lock_packages(path):
    data = json.loads(Path(path).read_text())
    pk = {}
    for p, meta in data.get("packages", {}).items():
        if not p or "node_modules/" not in p:
            continue
        name = p.rsplit("node_modules/", 1)[1]
        ver = meta.get("version")
        if ver and not meta.get("link"):
            pk[(name, ver)] = bool(meta.get("dev"))
    return pk


def npm_findings(state):
    from glob import glob
    locks = sorted({p for g in LOCK_GLOBS for p in glob(g)})
    where = {}  # (name, ver) -> {"apps": set, "dev": bool}
    for lock in locks:
        app = "/".join(Path(lock).parts[-3:-1])  # e.g. fitness/backend
        for key, dev in lock_packages(lock).items():
            w = where.setdefault(key, {"apps": set(), "dev": True})
            w["apps"].add(app)
            w["dev"] = w["dev"] and dev
    keys = list(where)
    hits = {}  # (name, ver) -> [vuln ids]
    for i in range(0, len(keys), 800):
        chunk = keys[i:i + 800]
        res = get_json("https://api.osv.dev/v1/querybatch",
                       {"queries": [{"package": {"name": n, "ecosystem": "npm"}, "version": v} for n, v in chunk]}, timeout=60)
        for key, r in zip(chunk, res["results"]):
            ids = [v["id"] for v in r.get("vulns", [])]
            if ids:
                hits[key] = ids
    cache = state.setdefault("osv", {})
    out, minor = [], 0
    for key, ids in hits.items():
        for vid in ids:
            if vid not in cache:
                try:
                    v = get_json(f"https://api.osv.dev/v1/vulns/{vid}")
                    cache[vid] = {"sev": (v.get("database_specific", {}).get("severity") or "UNKNOWN").upper(),
                                  "summary": (v.get("summary") or vid)[:110],
                                  "fixed": sorted({e["fixed"] for a in v.get("affected", []) for rg in a.get("ranges", [])
                                                   for e in rg.get("events", []) if "fixed" in e})[:3]}
                except Exception:
                    cache[vid] = {"sev": "UNKNOWN", "summary": vid, "fixed": []}
            info = cache[vid]
            w = where[key]
            if SEV_RANK.get(info["sev"], 0) < 3 or w["dev"]:
                minor += 1
                continue
            sev = "crit" if info["sev"] == "CRITICAL" else "warn"
            fix = f"upgrade to {', '.join(info['fixed'])}" if info["fixed"] else "no fixed version listed"
            out.append((f"npm:{vid}:{key[0]}@{key[1]}", sev,
                        f"{key[0]}@{key[1]} [{info['sev']}] {info['summary']} ({', '.join(sorted(w['apps']))})",
                        f"{fix}; run `npm audit fix` in the app's backend/frontend, commit the lockfile, deploy"))
    return out, minor, len(locks), len(keys)


# ── PHP (only matters if PHP is ever deployed) ──────────────────────────────────────────────────
def php_findings(state):
    out = []
    try:
        rel = get_json("https://www.php.net/releases/active.php")
    except Exception:
        return out
    newest = sorted((b["version"] for major in rel.values() for b in major.values()), key=vtuple)[-1]
    rc, images, _ = run(["docker", "ps", "--format", "{{.Names}}|{{.Image}}"])
    deployed = [l.split("|")[0] for l in images.splitlines() if "php" in l.lower()]
    if deployed:
        for l in images.splitlines():
            name, _, image = l.partition("|")
            if "php" in l.lower():
                m = re.search(r"php[:\-]?(\d+\.\d+(?:\.\d+)?)", image)
                if m and vtuple(m.group(1)) < vtuple(newest) and m.group(1).count(".") == 2:
                    out.append((f"php:{name}:{newest}", "crit", f"{name} runs PHP {m.group(1)}; {newest} is out",
                                "pull the newer php image tag and rebuild"))
    elif state.get("php_seen") != newest:
        if state.get("php_seen"):
            out.append((f"php-fyi:{newest}", "info", f"New PHP release {newest} upstream. Nothing we run uses PHP, so no action.", ""))
        state["php_seen"] = newest
    return out


# ── main ───────────────────────────────────────────────────────────────────────────────────────
def fmt(sev, line, fix):
    icon = {"crit": "🔴", "warn": "🟡", "info": "🔵"}[sev]
    return f"{icon} {line}" + (f"\n    fix: {fix}" if fix else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--config", default=str(HERE / "config.json"))
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    own_env = load_env(cfg.get("own_env_file", ""))
    tg_env = load_env(cfg["telegram_env_file"])
    token = own_env.get("TELEGRAM_BOT_TOKEN") or tg_env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = own_env.get("TELEGRAM_CHAT_ID") or tg_env.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
    state_file = Path(cfg["state_dir"]) / "cve-watch.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    now = datetime.now(timezone.utc)

    try:
        findings, errors = [], []
        for label, fn in (("node", node_findings), ("php", lambda: php_findings(state))):
            try:
                findings += fn()
            except Exception as e:
                errors.append(f"{label} check failed ({type(e).__name__})")
        minor = locks = pkgs = 0
        try:
            f, minor, locks, pkgs = npm_findings(state)
            findings += f
        except Exception as e:
            errors.append(f"npm check failed ({type(e).__name__})")

        seen = state.setdefault("seen", {})
        keys_now = {k for k, *_ in findings}
        new, remind = [], []
        for k, sev, line, fix in findings:
            first = seen.get(k)
            if first is None:
                new.append((sev, line, fix))
                seen[k] = {"first": now.isoformat(), "last_alert": now.isoformat()}
            elif sev != "info" and (now - datetime.fromisoformat(seen[k]["last_alert"])).days >= REMIND_DAYS:
                remind.append((sev, line, fix))
                seen[k]["last_alert"] = now.isoformat()
        resolved = [k for k in list(seen) if k not in keys_now]
        for k in resolved:
            del seen[k]

        if args.status:
            for k, sev, line, fix in findings:
                print(fmt(sev, line, fix))
            print(f"\n{locks} lockfiles, {pkgs} unique packages, {minor} moderate/low/dev advisories not paged; errors: {errors or 'none'}")
            return

        parts = []
        if new:
            parts.append("🚨 NEW security items\n" + "\n".join(fmt(*n) for n in new))
        if remind:
            parts.append(f"⏰ Still unpatched after {REMIND_DAYS}+ days\n" + "\n".join(fmt(*n) for n in remind))
        if resolved:
            parts.append("✅ Cleared: " + ", ".join(k.split(":")[1] if k.startswith("npm") else k for k in resolved))
        if errors:
            parts.append("⚠️ " + "; ".join(errors))
        if parts:
            msg = "🛡️ CVE watch\n\n" + "\n\n".join(parts) + "\n\nReply 'patch' in Claude Code and I'll rebuild, test, commit and (with your OK) deploy."
        else:
            msg = None

        if args.dry_run:
            print(msg or f"(quiet: nothing new; {len(findings)} open item(s); {locks} lockfiles/{pkgs} packages checked)")
            return
        if msg:
            if not (token and chat):
                raise RuntimeError("Telegram not configured")
            telegram(token, chat, msg)
        state["last_run"] = now.isoformat()
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=1))
    except Exception as e:
        if token and chat and not args.dry_run and not args.status:
            try:
                telegram(token, chat, f"⚠️ CVE watch FAILED: {type(e).__name__}")
            except Exception:
                pass
        raise


if __name__ == "__main__":
    main()
