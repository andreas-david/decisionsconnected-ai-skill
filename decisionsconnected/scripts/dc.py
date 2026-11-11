#!/usr/bin/env python3
"""DecisionsConnected: Entscheidungen eines Projekts lesen, als Entwurf dokumentieren und kommentieren.

Der Schlüssel kommt aus der Umgebungsvariable DC_API_TOKEN (nie als Argument, nie in Dateien). Optional: DC_API_URL.
Jeder Befehl entspricht genau einem Endpunkt der Schnittstelle /v1 (siehe references/api.md). Nur die Standardbibliothek.
"""
import argparse
import atexit
import difflib
import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

__version__ = "1.2.0"
BASE = os.environ.get("DC_API_URL", "https://api.decisionsconnected.com").rstrip("/")

HINTS = {
    "scan_pending": "Die Texte des Projekts sind noch nicht durch AI Data Veil geprüft. Die KI sieht erst etwas, wenn die Projektleitung die Prüfung abgeschlossen hat (Beteiligte, KI-Teilnehmer, „Jetzt prüfen“).",
    "pseudonymizer_unavailable": "AI Data Veil ist gerade nicht erreichbar. Aus Datenschutzgründen kommt dann nichts durch. Später noch einmal versuchen.",
    "veil_key_invalid": "Der Schlüssel der Firma bei AI Data Veil wurde abgelehnt. Die Verwaltung der Firma muss ihn prüfen.",
    "veil_quota": "Das Limit bei AI Data Veil ist erreicht.",
    "scope_missing": "Die Projektleitung hat dieser KI dieses Recht nicht gegeben (Beteiligte, KI-Teilnehmer, Rechte).",
    "not_logged_in": "Der Schlüssel ist ungültig, gelöscht oder der KI-Zugang der Firma ist aus (DC_API_TOKEN prüfen).",
    "too_many_attempts": "Zu viele Anfragen. Kurz warten.",
}


REPO = "https://github.com/andreas-david/decisionsconnected-ai-skill"
VERSION_URL = os.environ.get("DC_UPDATE_URL", "https://raw.githubusercontent.com/andreas-david/decisionsconnected-ai-skill/main/VERSION")


def _ver(v):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except ValueError:
        return (0,)


def update_hint():
    """Höchstens einmal am Tag die neueste Skill-Version abfragen (nur die Datei VERSION) und bei einem neueren Stand einen Hinweis ausgeben.
    Installiert nichts, sendet nichts außer dem Abruf. Abschalten: DC_NO_UPDATE_CHECK=1."""
    if os.environ.get("DC_NO_UPDATE_CHECK"):
        return
    base = os.environ.get("DC_CACHE_DIR") or os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache"), "decisionsconnected-skill")
    state = os.path.join(base, "update.json")
    latest, checked, noted = None, 0, 0
    try:
        with open(state, encoding="utf-8") as f:
            d = json.load(f)
        latest, checked, noted = d.get("latest"), float(d.get("checked", 0)), float(d.get("noted", 0))
    except Exception:
        pass
    if time.time() - checked > 86400:
        try:
            req = urllib.request.Request(VERSION_URL, headers={"User-Agent": "dc-skill/" + __version__})
            with urllib.request.urlopen(req, timeout=2, context=ssl_context()) as r:
                got = r.read(64).decode("utf-8", "replace").strip()
            if len(got.split(".")) == 3 and all(x.isdigit() for x in got.split(".")):
                latest = got
        except Exception:
            pass  # kein Netz oder kein Zugriff: still bleiben
        checked = time.time()
    newer = bool(latest) and _ver(latest) > _ver(__version__)
    show = newer and time.time() - noted > 86400  # der Hinweis kommt höchstens einmal am Tag
    try:
        os.makedirs(base, exist_ok=True)
        with open(state, "w", encoding="utf-8") as f:
            json.dump({"latest": latest, "checked": checked, "noted": time.time() if show else noted}, f)
    except Exception:
        pass
    if show:
        print("Hinweis: Skill-Update verfügbar (installiert %s, neu %s). Dem Nutzer mitteilen; nicht selbst installieren. "
              "Aktualisieren: im Klon des Skills `git pull` und `install.sh <projekt>` ausführen. Änderungen: %s/blob/main/CHANGELOG.md" % (__version__, latest, REPO), file=sys.stderr)


def ssl_context():
    """Zertifikate prüfen, nie abschalten. Manche Python-Installationen (zum Beispiel von python.org auf dem Mac) bringen keine Zertifikate mit:
    dann certifi oder das Bündel des Systems nutzen."""
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats().get("x509_ca", 0) > 0:
        return ctx
    try:
        import certifi  # type: ignore
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    for cafile in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt", "/etc/pki/tls/certs/ca-bundle.crt", "/etc/ssl/ca-bundle.pem"):
        if os.path.isfile(cafile):
            return ssl.create_default_context(cafile=cafile)
    return ctx


def call(method, path, body=None, query=None):
    token = os.environ.get("DC_API_TOKEN", "").strip()
    if not token:
        sys.exit("Fehler: DC_API_TOKEN ist nicht gesetzt. Den Schlüssel in der Umgebung hinterlegen (nicht in Dateien oder im Chat).")
    url = BASE + path + ("?" + urllib.parse.urlencode({k: v for k, v in (query or {}).items() if v not in (None, "")}) if query else "")
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + token, "Accept": "application/json", "Content-Type": "application/json", "User-Agent": "dc-skill/" + __version__})
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl_context()) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8")).get("error", "")
        except Exception:
            err = ""
        sys.exit("Fehler %s (%s). %s" % (e.code, err or "unbekannt", HINTS.get(err, "")))
    except urllib.error.URLError as e:
        hint = " Python findet keine Zertifikate: `pip install certifi` oder (macOS) „Install Certificates.command“ ausführen." if "CERTIFICATE" in str(e.reason) else ""
        sys.exit("Fehler: DecisionsConnected nicht erreichbar (%s).%s" % (e.reason, hint))


def idem(*parts):
    """Gleicher Inhalt, gleicher Schlüssel: Ein wiederholter Aufruf legt nichts doppelt an."""
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:40]


STOP = set("""wie welche welcher welches welchen welchem wir uns unser unsere der die das den dem des ein eine einen einem einer und oder mit von auf für fuer im in an am zu zum zur bei nach vor
ist sind wird werden soll sollen sollten wollen wollen muss müssen kann können darf dürfen nehmen nutzen verwenden benutzen wählen entscheiden setzen legen machen geben
wann warum wo was wer wozu damit dann nur auch noch schon später jetzt neu neue""".split())


def _norm(t):
    return re.sub(r"[^a-z0-9äöüß ]+", " ", (t or "").lower()).split()


def _content(t):
    return {w for w in _norm(t) if w not in STOP and len(w) > 2}


def similar(title, options, c):
    """Ähnlichkeit einer vorhandenen Entscheidung c zur geplanten Frage (0 bis 1): Schreibweise des Titels, gemeinsame Inhaltswörter und Optionen."""
    a, b = " ".join(_norm(title)), " ".join(_norm(c["title"]))
    t = difflib.SequenceMatcher(None, a, b).ratio()
    ca, cb = _content(title), _content(c["title"])
    cw = len(ca & cb) / len(ca | cb) if (ca and cb) else 0
    mine = {" ".join(_norm(o)) for o in options}
    theirs = {" ".join(_norm(o["title"])) for o in c.get("options", [])}
    j = len(mine & theirs) / len(mine | theirs) if (mine | theirs) else 0
    return max(t, 0.5 * t + 0.5 * j if j else 0, cw if cw >= 0.6 else 0, 0.6 * cw + 0.4 * j if (cw >= 0.4 and j >= 0.3) else 0)


def cmd_ask(a):
    """Entscheidungsbedarf melden, ohne Rückfrage: Gibt es die Frage schon, kommt die vorhandene Entscheidung zurück; sonst entsteht ein Entwurf fürs Team."""
    options = [o.strip() for o in (a.option or []) if o.strip()]
    if len(options) < 2:
        sys.exit("Fehler: Mindestens zwei Optionen angeben (--option), auch „Beim Bisherigen bleiben“ oder „Nichts tun“.")
    title = a.title.strip()
    if not title.endswith("?"):
        title += "?"
    if not a.force:
        existing = call("GET", "/v1/decisions", query={"limit": 500})["decisions"]
        hits = sorted(((similar(title, options, c), c) for c in existing), key=lambda x: -x[0])
        hits = [(r, c) for r, c in hits if r >= 0.72][:3]
        if hits:
            out({"result": "exists", "matches": [{"key": c["key"], "status": c["status"], "title": c["title"], "acceptedOption": c.get("acceptedOption"),
                                                   "options": [o["title"] for o in c.get("options", [])], "similarity": round(r, 2), "url": c["url"]} for r, c in hits],
                 "advice": "Gibt es die Frage schon? Ist sie entschieden, ist die gewählte Option bindend. Ist sie offen oder ein Entwurf, nicht doppelt anlegen: bei neuem Kontext mit `comment KEY --text …` ergänzen und mit einer dokumentierten Annahme weiterarbeiten oder den Zweig pausieren. Nur wenn es wirklich eine andere Frage ist, mit --force trotzdem anlegen."})
            return
    parts = [a.context.strip()] if a.context else []
    if a.source:
        parts.append("Quelle: " + a.source.strip())
    parts.append("Blockiert Arbeit: " + ("ja" if a.blocking else "nein") + ".")
    if a.assume:
        parts.append("Annahme bis zur Entscheidung: " + a.assume.strip())
    parts.append("Gestellt von einem autonomen KI-Agenten. Bitte prüfen, veröffentlichen und entscheiden.")
    body = {"title": title, "description": "\n\n".join(parts), "options": [{"title": o} for o in options]}
    if a.thread:
        body["thread"] = a.thread
    if a.due:
        body["dueDate"] = a.due
    parents = []
    for p in a.parent or []:
        bits = p.split(":")
        if len(bits) < 2:
            sys.exit("Fehler: --parent erwartet VORGÄNGER:OPTION[:TYP].")
        parents.append({"decision": bits[0], "option": bits[1], "type": bits[2] if len(bits) > 2 else "based_on", "others": "no_effect"})
    if parents:
        body["parents"] = parents
    body["idempotencyKey"] = idem("ask", body)
    r = call("POST", "/v1/drafts", body)
    out({"result": "drafted", "draft": r["draft"], "assumption": a.assume or None, "blocking": bool(a.blocking),
         "advice": "Die Frage liegt als Entwurf beim Projektteam (Verantwortliche sehen sie unter „Braucht dich“). Entscheiden darf nur ein Mensch. Arbeite " +
                   ("vorläufig mit der genannten Annahme weiter und halte sie im Ergebnis fest" if a.assume and not a.blocking else "an anderem weiter und pausiere diesen Zweig" if a.blocking else "an anderem weiter") +
                   ". Später mit `answer %s` nachsehen." % r["draft"]["key"]})


def cmd_answer(a):
    """Hat das Team entschieden? Liefert den Stand einer Frage."""
    d = call("GET", "/v1/decision", query={"key": a.key})
    x = d["decision"]
    res = {"key": x["key"], "title": x["title"], "status": x["status"], "decided": x["status"] == "decided", "acceptedOption": x.get("acceptedOption"),
           "reason": x.get("reason"), "needsReview": x.get("needsReview"), "url": x["url"]}
    res["advice"] = ("Entschieden: Die gewählte Option ist jetzt bindend, richte die Arbeit danach aus (und passe frühere Annahmen an)." if res["decided"]
                     else "Noch nicht entschieden (Status %s). Weiter mit der dokumentierten Annahme oder pausieren; später erneut nachsehen." % x["status"])
    out(res)


def out(data, compact=False):
    if compact and isinstance(data.get("decisions"), list):
        for c in data["decisions"]:
            opts = " | ".join(("✓ " if o.get("accepted") else "") + o["title"] for o in c.get("options", []))
            print("%s  %-8s  %s%s" % (c["key"], c["status"], c["title"], ("   [" + opts + "]") if opts else ""))
        print("(%s Entscheidungen)" % data.get("total", len(data["decisions"])))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    atexit.register(update_hint)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version="dc.py " + __version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("projects", help="Projekte des Schlüssels mit Zählern und Rechten")
    p = sub.add_parser("list", help="Entscheidungen auflisten")
    p.add_argument("--project"); p.add_argument("--status", help="z. B. open,voting,decided,draft"); p.add_argument("--thread"); p.add_argument("--limit", type=int)
    p.add_argument("--compact", action="store_true", help="eine Zeile je Entscheidung")
    p = sub.add_parser("search", help="Entscheidungen nach Text durchsuchen (Titel, Optionen, Strang)")
    p.add_argument("text"); p.add_argument("--compact", action="store_true")
    p = sub.add_parser("show", help="Eine Entscheidung mit Optionen, Beschreibung, Begründung, Kommentaren"); p.add_argument("key")
    p = sub.add_parser("graph", help="Knoten und Kanten"); p.add_argument("--project")
    p = sub.add_parser("impact", help="Folgen einer Änderung je Option"); p.add_argument("key")
    p = sub.add_parser("draft", help="Entscheidungsentwurf anlegen (JSON aus Datei oder Standardeingabe)")
    p.add_argument("--file", help="JSON-Datei; ohne Angabe oder mit - wird von der Standardeingabe gelesen")
    p = sub.add_parser("option", help="Option an einem eigenen Entwurf ergänzen"); p.add_argument("key"); p.add_argument("--title", required=True); p.add_argument("--description", default="")
    p = sub.add_parser("comment", help="Kommentar schreiben"); p.add_argument("key"); p.add_argument("--text", required=True); p.add_argument("--option")
    p = sub.add_parser("link", help="Verbindung vorschlagen (bleibt angefragt, bis ein Mensch sie annimmt)")
    p.add_argument("--child", required=True); p.add_argument("--parent", required=True); p.add_argument("--option", required=True, help="Schlüssel der Option des Vorgängers")
    p.add_argument("--type", default="based_on", choices=["based_on", "check", "no_effect", "blocks", "ends"]); p.add_argument("--others", default="no_effect", choices=["based_on", "check", "no_effect", "blocks", "ends"])
    p = sub.add_parser("ask", help="Entscheidungsbedarf melden (ohne Rückfrage): vorhandene Entscheidung finden oder Entwurf fürs Team anlegen")
    p.add_argument("--title", required=True, help="die Frage"); p.add_argument("--option", action="append", help="eine Option (mindestens zwei)")
    p.add_argument("--context", default="", help="Kontext: worum geht es, warum jetzt"); p.add_argument("--source", help="Quelle: Datei, PR, Aufgabe")
    p.add_argument("--assume", help="Annahme, mit der vorläufig weitergearbeitet wird"); p.add_argument("--blocking", action="store_true", help="die Frage blockiert die Arbeit")
    p.add_argument("--parent", action="append", help="VORGÄNGER:OPTION[:TYP], mehrfach möglich"); p.add_argument("--thread"); p.add_argument("--due", help="JJJJ-MM-TT")
    p.add_argument("--force", action="store_true", help="auch anlegen, wenn eine ähnliche Frage existiert")
    p = sub.add_parser("answer", help="Hat das Team entschieden? Stand einer Frage"); p.add_argument("key")
    a = ap.parse_args()

    if a.cmd == "projects":
        out(call("GET", "/v1/projects"))
    elif a.cmd == "list":
        out(call("GET", "/v1/decisions", query={"project": a.project, "status": a.status, "thread": a.thread, "limit": a.limit}), a.compact)
    elif a.cmd == "search":
        d = call("GET", "/v1/decisions", query={"limit": 500})
        t = a.text.lower()
        d["decisions"] = [c for c in d["decisions"] if t in json.dumps([c["title"], [o["title"] for o in c["options"]], c.get("thread"), c.get("threads")], ensure_ascii=False).lower()]
        d["total"] = len(d["decisions"])
        out(d, a.compact)
    elif a.cmd == "show":
        out(call("GET", "/v1/decision", query={"key": a.key}))
    elif a.cmd == "graph":
        out(call("GET", "/v1/graph", query={"project": a.project}))
    elif a.cmd == "impact":
        out(call("GET", "/v1/impact", query={"key": a.key}))
    elif a.cmd == "draft":
        raw = sys.stdin.read() if a.file in (None, "-") else open(a.file, encoding="utf-8").read()
        try:
            body = json.loads(raw)
        except ValueError as e:
            sys.exit("Fehler: Der Entwurf ist kein gültiges JSON (%s)." % e)
        body.setdefault("idempotencyKey", idem("draft", body))
        out(call("POST", "/v1/drafts", body))
    elif a.cmd == "option":
        out(call("POST", "/v1/options", {"decision": a.key, "title": a.title, "description": a.description}))
    elif a.cmd == "comment":
        body = {"decision": a.key, "text": a.text}
        if a.option:
            body["option"] = a.option
        body["idempotencyKey"] = idem("comment", body)
        out(call("POST", "/v1/comments", body))
    elif a.cmd == "ask":
        cmd_ask(a)
    elif a.cmd == "answer":
        cmd_answer(a)
    elif a.cmd == "link":
        out(call("POST", "/v1/links", {"child": a.child, "parent": a.parent, "option": a.option, "type": a.type, "others": a.others}))


if __name__ == "__main__":
    main()
