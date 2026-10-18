"""Command line: ./abos <command>. Run ./abos -h for the list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import REPO_ROOT, board, handoff, schema
from .ledger import Ledger, LedgerError
from .secrets import scan_files, staged_files


def _load_json(value: str) -> dict:
    path = Path(value)
    return json.loads(path.read_text() if path.exists() else value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abos", description="agent-business-os backbone tools (T0, no LLM)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    led = sub.add_parser("ledger", help="task ledger").add_subparsers(dest="action", required=True)
    led.add_parser("verify", help="check the hash chain")
    led.add_parser("list", help="one line per task")
    show = led.add_parser("show"); show.add_argument("task_id")
    add = led.add_parser("add", help="pre-flight + create a task"); add.add_argument("spec", help="JSON file or inline JSON")
    upd = led.add_parser("update"); upd.add_argument("task_id"); upd.add_argument("changes", help="JSON file or inline JSON")
    exp = led.add_parser("export-sqlite", help="build a SQLite copy for SQL queries")
    exp.add_argument("path", nargs="?", default=str(REPO_ROOT / "state" / "task-ledger" / "ledger.sqlite"))

    ho = sub.add_parser("handoff", help="handoff bundles").add_subparsers(dest="action", required=True)
    rec = ho.add_parser("receive"); rec.add_argument("file"); rec.add_argument("--product-id", default="PRD-PLATFORM")

    use = sub.add_parser("usage", help="usage ledger from status-line snapshots").add_subparsers(dest="action", required=True)
    use.add_parser("report", help="rebuild state/usage-ledger and reports/usage per day")

    lev = sub.add_parser("eval-local", help="run golden extraction tasks on a local Ollama model")
    lev.add_argument("--model", default="qwen2.5:3b")
    lev.add_argument("--no-grounding", action="store_true", help="score raw model output (baseline)")
    lev.add_argument("--holdout", action="store_true", help="use the held-out golden set")
    sub.add_parser("install-claude", help="copy reviewed settings + subagents into .claude/")
    sub.add_parser("board", help="regenerate state/status-board.md")
    sub.add_parser("test", help="run the test suite and store an immutable result record")
    sub.add_parser("schemas", help="check schemas only use supported keywords")

    sec = sub.add_parser("secrets", help="scan files for secrets")
    sec.add_argument("paths", nargs="*"); sec.add_argument("--staged", action="store_true")

    args = parser.parse_args(argv)
    ledger = Ledger()

    try:
        if args.cmd == "ledger":
            if args.action == "verify":
                problems = ledger.verify_chain()
                print("\n".join(problems) or f"OK: {len(ledger.events())} events, chain intact")
                return 1 if problems else 0
            if args.action == "list":
                for t in ledger.tasks().values():
                    print(f"{t['task_id']}  {t['priority']:<7} {t['status']:<22} {t['objective'][:80]}")
                return 0
            if args.action == "show":
                print(json.dumps(ledger.get(args.task_id), indent=2))
                return 0
            if args.action == "add":
                task, pre = ledger.create_task(_load_json(args.spec))
                print(json.dumps({"task_id": task["task_id"], "preflight": pre}, indent=2))
                board.write(ledger)
                return 0 if pre["result"] != "REJECTED" else 2
            if args.action == "update":
                task = ledger.update(args.task_id, _load_json(args.changes))
                print(f"{task['task_id']} -> {task['status']}")
                board.write(ledger)
                return 0
            if args.action == "export-sqlite":
                print(ledger.export_sqlite(Path(args.path)))
                return 0
        if args.cmd == "handoff":
            ack = handoff.receive(Path(args.file), ledger, product_id=args.product_id)
            print(json.dumps(ack, indent=2))
            board.write(ledger)
            return 0 if ack["result"].startswith("ACCEPTED") else 2
        if args.cmd == "usage":
            from .usage import report
            written = report()
            print("\n".join(str(p.relative_to(REPO_ROOT)) for p in written) or "no snapshots yet")
            return 0
        if args.cmd == "eval-local":
            from .localeval import run
            from .localeval import GOLDEN, HOLDOUT
            rec = run(args.model, golden=HOLDOUT if args.holdout else GOLDEN, grounding=not args.no_grounding)
            print(json.dumps({k: v for k, v in rec.items() if k != "rows"}, indent=2))
            return 0 if rec["result"] == "PASS" else 1
        if args.cmd == "install-claude":
            from .install import install
            changes = install()
            print("\n".join(changes) or "already up to date")
            print("Restart Claude Code in this folder to load the changes.")
            return 0
        if args.cmd == "board":
            print(board.write(ledger))
            return 0
        if args.cmd == "test":
            from .testrun import run
            record = run()
            print(json.dumps(record, indent=2))
            return record["exit_status"]
        if args.cmd == "schemas":
            problems = schema.check_all_schemas()
            print(json.dumps(problems, indent=2) if problems else "OK: all schemas use supported keywords")
            return 1 if problems else 0
        if args.cmd == "secrets":
            paths = staged_files(REPO_ROOT) if args.staged else [Path(p) for p in args.paths]
            found = scan_files(paths)
            for f, hits in found.items():
                for h in hits:
                    print(f"{f}:{h['line']}: {h['rule']} ({h['preview']})", file=sys.stderr)
            if found:
                print("BLOCKED: secret-like content found. Remove it, or move the file to private/.", file=sys.stderr)
                return 1
            return 0
    except LedgerError as exc:
        print(f"ledger error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
