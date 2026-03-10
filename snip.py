#!/usr/bin/env python3
"""snip — local code snippet manager.

Zero dependencies. Save, search, tag, and retrieve code snippets from the CLI.

Usage:
    snip.py add "name" --lang python --tags "web,api" < snippet.py
    snip.py add "name" --lang python -c "print('hello')"
    snip.py get "name"
    snip.py list [--lang python] [--tag web]
    snip.py search "query"
    snip.py rm "name"
    snip.py export [--json]
"""

import argparse
import json
import sys
import time
from pathlib import Path

STORE = Path.home() / ".local" / "share" / "snip" / "snippets.json"


def load() -> dict:
    if STORE.exists():
        return json.loads(STORE.read_text())
    return {}


def save(data: dict):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, indent=2))


# ANSI
C = "\033[36m"
G = "\033[32m"
Y = "\033[33m"
D = "\033[2m"
B = "\033[1m"
R = "\033[0m"


def cmd_add(args):
    data = load()
    name = args.name

    if args.code:
        code = args.code
    else:
        code = sys.stdin.read()

    if not code.strip():
        print("Error: no snippet content provided", file=sys.stderr)
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    data[name] = {
        "code": code,
        "lang": args.lang or "",
        "tags": tags,
        "desc": args.desc or "",
        "created": time.strftime("%Y-%m-%d %H:%M"),
        "updated": time.strftime("%Y-%m-%d %H:%M"),
    }
    save(data)
    print(f"{G}✓{R} Saved snippet: {B}{name}{R} ({len(code)} chars)")


def cmd_get(args):
    data = load()
    name = args.name

    if name not in data:
        # Fuzzy match
        matches = [k for k in data if name.lower() in k.lower()]
        if len(matches) == 1:
            name = matches[0]
        elif matches:
            print(f"Multiple matches: {', '.join(matches)}")
            return
        else:
            print(f"Snippet '{name}' not found.", file=sys.stderr)
            sys.exit(1)

    snippet = data[name]
    if args.raw:
        print(snippet["code"], end="")
    else:
        print(f"{B}{name}{R}", end="")
        if snippet["lang"]:
            print(f" {D}({snippet['lang']}){R}", end="")
        if snippet["tags"]:
            print(f" {C}[{', '.join(snippet['tags'])}]{R}", end="")
        print()
        if snippet.get("desc"):
            print(f"{D}{snippet['desc']}{R}")
        print(f"{'─' * 40}")
        print(snippet["code"], end="")
        if not snippet["code"].endswith("\n"):
            print()


def cmd_list(args):
    data = load()
    if not data:
        print("No snippets saved.")
        return

    filtered = data.items()
    if args.lang:
        filtered = [(k, v) for k, v in filtered if v.get("lang", "").lower() == args.lang.lower()]
    if args.tag:
        filtered = [(k, v) for k, v in filtered if args.tag.lower() in [t.lower() for t in v.get("tags", [])]]

    filtered = list(filtered)
    if not filtered:
        print("No matching snippets.")
        return

    print(f"📋 {len(filtered)} snippet{'s' if len(filtered) != 1 else ''}:\n")
    for name, s in sorted(filtered):
        lang = f" {D}({s['lang']}){R}" if s.get("lang") else ""
        tags = f" {C}[{', '.join(s['tags'])}]{R}" if s.get("tags") else ""
        lines = s["code"].count("\n") + 1
        print(f"  {B}{name}{R}{lang}{tags} {D}({lines}L, {s.get('created', '?')}){R}")
        if s.get("desc"):
            print(f"    {D}{s['desc']}{R}")


def cmd_search(args):
    data = load()
    query = args.query.lower()

    matches = []
    for name, s in data.items():
        score = 0
        if query in name.lower():
            score += 3
        if query in s.get("desc", "").lower():
            score += 2
        if query in s.get("code", "").lower():
            score += 1
        if any(query in t.lower() for t in s.get("tags", [])):
            score += 2
        if score > 0:
            matches.append((name, s, score))

    matches.sort(key=lambda x: -x[2])

    if not matches:
        print(f"No snippets matching '{args.query}'.")
        return

    print(f"🔍 {len(matches)} result{'s' if len(matches) != 1 else ''} for '{args.query}':\n")
    for name, s, score in matches:
        lang = f" ({s['lang']})" if s.get("lang") else ""
        print(f"  {B}{name}{R}{lang}")
        # Show first matching line
        for line in s["code"].split("\n"):
            if query in line.lower():
                print(f"    {D}...{line.strip()[:60]}{R}")
                break


def cmd_rm(args):
    data = load()
    if args.name not in data:
        print(f"Snippet '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    del data[args.name]
    save(data)
    print(f"✓ Deleted snippet: {args.name}")


def cmd_export(args):
    data = load()
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for name, s in sorted(data.items()):
            print(f"### {name}")
            if s.get("lang"):
                print(f"```{s['lang']}")
            else:
                print("```")
            print(s["code"], end="")
            if not s["code"].endswith("\n"):
                print()
            print("```\n")


def main():
    parser = argparse.ArgumentParser(description="snip — code snippet manager")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("add", help="Add a snippet")
    p.add_argument("name")
    p.add_argument("--lang", "-l", help="Language")
    p.add_argument("--tags", "-t", help="Comma-separated tags")
    p.add_argument("--desc", "-d", help="Description")
    p.add_argument("--code", "-c", help="Inline code (or pipe stdin)")

    p = sub.add_parser("get", help="Get a snippet")
    p.add_argument("name")
    p.add_argument("--raw", "-r", action="store_true", help="Raw output only")

    p = sub.add_parser("list", help="List snippets")
    p.add_argument("--lang", "-l", help="Filter by language")
    p.add_argument("--tag", "-t", help="Filter by tag")

    p = sub.add_parser("search", help="Search snippets")
    p.add_argument("query")

    p = sub.add_parser("rm", help="Remove a snippet")
    p.add_argument("name")

    p = sub.add_parser("export", help="Export all snippets")
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    {"add": cmd_add, "get": cmd_get, "list": cmd_list,
     "search": cmd_search, "rm": cmd_rm, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    main()
