#!/usr/bin/env python3
"""Privacy check: this repository is public and must never contain personal
data (rule number one). Blocks phone numbers, e-mail addresses, WhatsApp ids,
group invite links and personal folder paths — and, on a Mac where the app is
installed, every name, keyword and folder from the local config.json.

Usage:
  python3 scripts/privacy_check.py --staged        files staged for commit (pre-commit hook)
  python3 scripts/privacy_check.py --message FILE  a commit message (commit-msg hook)
  python3 scripts/privacy_check.py --all           every tracked file (CI, manual check)
  python3 scripts/privacy_check.py --history       every version of every file ever committed

Matches are printed masked, so the check itself never prints the data.
"""
import json, os, re, subprocess, sys

# Fictional or technical values that are allowed on purpose.
ALLOW = {
    "+55 11 91234-5678",          # fictional example in a docstring
    "noreply@anthropic.com",      # commit co-author line
    "gui@users.noreply.local",    # anonymous git author
}
# Technical identifiers that may contain a word from someone's config without
# being personal data. Keep this empty unless there is a real need.
ALLOW_TEXT = ()
PATTERNS = {
    "phone number": re.compile(r"\+\d{1,3}[\s-]?\(?\d{2,3}\)?[\s-]?9?\d{4}[\s-]?\d{4}"),
    "e-mail address": re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
    "WhatsApp id": re.compile(r"\d{8,}(?:-\d+)?@(?:g\.us|s\.whatsapp\.net|lid)"),
    "group invite link": re.compile(r"chat\.whatsapp\.com/(?:invite/)?[A-Za-z0-9]{16,}"),
    "personal folder path": re.compile(r"/Users/(?!Shared/)[A-Za-z][\w.-]*"),
}
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".icns", ".pdf", ".zip")
CONFIG = os.path.expanduser(
    "~/Library/Application Support/WhatsApp Sync/config.json")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          check=True).stdout


def personal_terms():
    """Names, keywords and folders from this Mac's own config (never sent
    anywhere: only used to look for them in the repository)."""
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return set()
    terms = {cfg.get("meu_nome", "")}
    for c in cfg.get("conversas", []):
        if isinstance(c, dict):
            terms |= {c.get("nome", ""), c.get("arquivo", "")}
            terms |= set(c.get("pastas") or [])
    for t in cfg.get("assuntos", []):
        terms |= {t.get("nome", "")} | set(t.get("palavras", [])) | set(t.get("pastas", []))
    terms |= set(cfg.get("palavras", [])) | set(cfg.get("voz_arquivos", []))
    terms |= set(cfg.get("convites", {}).values())
    # short or very common words would only cause false alarms
    common = {"sistema", "energia", "solar", "keyword", "example topic", "me"}
    return {t.strip() for t in terms
            if t and len(t.strip()) >= 5 and t.strip().lower() not in common}


def mask(s):
    return s[:3] + "…" + s[-2:] if len(s) > 6 else "…"


def scan(name, text, terms):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for kind, rx in PATTERNS.items():
            for m in rx.finditer(line):
                if m.group(0) not in ALLOW:
                    hits.append(f"{name}:{n}: {kind} ({mask(m.group(0))})")
        low = line.lower()
        for a in ALLOW_TEXT:
            low = low.replace(a, "")
        for t in terms:
            if t.lower() in low:
                hits.append(f"{name}:{n}: name/keyword/folder from your config ({mask(t)})")
    return hits


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"
    terms, hits = personal_terms(), []
    if mode == "--message":
        with open(sys.argv[2], encoding="utf-8", errors="replace") as f:
            hits = scan("commit message", f.read(), terms)
    elif mode == "--history":
        seen = set()
        for rev in git("rev-list", "--all").split():
            for line in git("ls-tree", "-r", rev).splitlines():
                meta, path = line.split("\t", 1)
                sha = meta.split()[2]
                if sha in seen or path.lower().endswith(SKIP_EXT):
                    continue
                seen.add(sha)
                hits += scan(f"{rev[:7]}:{path}", git("cat-file", "-p", sha), terms)
        for rev in git("rev-list", "--all").split():
            hits += scan(f"{rev[:7]} message", git("log", "-1", "--format=%B", rev), terms)
    else:
        files = (git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
                 if mode == "--staged" else git("ls-files")).splitlines()
        for path in files:
            if path.lower().endswith(SKIP_EXT):
                continue
            text = (git("show", f":{path}") if mode == "--staged"
                    else open(path, encoding="utf-8", errors="replace").read())
            hits += scan(path, text, terms)
    if hits:
        print("Privacy check FAILED — this repository is public; remove these:")
        print("\n".join("  " + h for h in sorted(set(hits))))
        print("Use fictional examples (e.g. +55 11 91234-5678). Personal settings "
              "belong only in ~/Library/Application Support/WhatsApp Sync/.")
        return 1
    print(f"Privacy check passed ({mode[2:]}"
          + (f", {len(terms)} personal terms from your config" if terms else "") + ").")
    return 0


if __name__ == "__main__":
    sys.exit(main())
