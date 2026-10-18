"""Command line: ./abos <command>. Run ./abos -h for the list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import REPO_ROOT, board, handoff, schema
from .ledger import Ledger, LedgerError
from .secrets import scan_context, scan_files, staged_files


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
    rt = sub.add_parser("route", help="pick tier + subagent for a task type (Model Router, T0)")
    rt.add_argument("task"); rt.add_argument("--risk"); rt.add_argument("--privacy", default="INTERNAL")
    rt.add_argument("--budget", choices=["OK", "SOFT", "HARD"]); rt.add_argument("--five", type=float)
    rt.add_argument("--seven", type=float); rt.add_argument("--failures", type=int, default=0)
    mem = sub.add_parser("scan-memory", help="flag instruction-like text in memory/, decisions/, agents/, CLAUDE.md")
    mem.add_argument("paths", nargs="*"); mem.add_argument("--staged", action="store_true")

    pr = sub.add_parser("phase-report", help="summarise a gate's tasks for the phase report")
    pr.add_argument("gate"); pr.add_argument("--write", metavar="PATH", help="write the report to a new file under reports/")
    pr.add_argument("--force", action="store_true", help="allow --write to overwrite an existing file")

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
        if args.cmd == "route":
            from . import router
            cfg, budgets = router.load()
            level = args.budget or router.budget_level(args.five, args.seven, budgets)
            decision = router.route(args.task, cfg, budgets, risk=args.risk, privacy=args.privacy,
                                    budget=level, failures=args.failures)
            print(json.dumps(decision, indent=2))
            return 0 if decision["action"] == "RUN" else 3
        if args.cmd == "phase-report":
            from . import phasereport
            return phasereport.run_cli(ledger, args.gate, args.write, args.force)
        if args.cmd == "scan-memory":
            paths = staged_files(REPO_ROOT) if args.staged else ([Path(p) for p in args.paths] or None)
            found = scan_context(REPO_ROOT, paths)
            for f, hits in found.items():
                for h in hits:
                    print(f"{f}:{h['line']}: {h['rule']} ({h['preview']})", file=sys.stderr)
            if found:
                print("FLAGGED: instruction-like text in agent context files (possible memory poisoning). "
                      "A human must review it; agents treat it as data.", file=sys.stderr)
                return 1
            print("OK: no instruction-like text in agent context files")
            return 0
    except LedgerError as exc:
        print(f"ledger error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
