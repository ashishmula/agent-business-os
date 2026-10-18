# AgentOps features, in plain English

This project is a small operating system for AI agents: it lets several AI helpers work on one project safely, cheaply and without forgetting things. "AgentOps" is the job of keeping AI agents observable (you can see what they did), safe (they can't do damage), affordable (they don't waste money or usage) and reliable (you can prove they work).

Each feature below says what it is, why it matters, where it lives and how it is proven. Use it to explain the project in your own words.

## 1. Task ledger: the agents' shared diary
- **What:** every task and every change to it is written as one line in `state/task-ledger/events.jsonl`. Each line carries a fingerprint (hash) of the line before it, like links in a chain.
- **Why:** agents forget between sessions. The diary means a new session reads what's done instead of guessing or redoing work. If anyone edits an old line, the chain breaks and `./abos ledger verify` says so.
- **Proof:** `tests/unit/test_a_spec.py`, `test_d_resilience.py` (a crash in the middle of a write no longer breaks the diary).

## 2. Model router: the right-sized worker for each job
- **What:** `./abos route <task_type>` picks which AI model should do a job, from free scripts up to the most capable model, using `config/routing-rules.toml`.
- **Why:** using the most expensive model for everything wastes usage; using a weak one for important work gives bad results. Each job type has a "floor": important work is never handed to a model below it.
- **Proof:** `tests/unit/test_c_routing.py`. In Phase 3, 1,056 test routes were checked and none went below its floor.

## 3. Governor: the fuel gauge
- **What:** the status line (`tools/hooks/statusline.py`) records how full the agent's memory window is and how much of the plan's usage is spent. `prompt_nudge.py` warns at set levels, and `precompact.py` saves a checkpoint before memory is squeezed.
- **Why:** an agent that runs out of memory mid-task loses its place. Warnings and checkpoints let it stop cleanly and pick up again.
- **Proof:** `tests/unit/test_b_hooks.py`. Thresholds live in `config/budgets.toml`.

## 4. Loop breaker: the fuse box
- **What:** `tools/hooks/loop_breaker.py` runs before every tool call. It remembers fingerprints of the last 20 calls. If the agent tries the exact same action a 4th time in a row, or 7 times within 20 calls, the call is blocked with a message telling it to change approach or ask.
- **Why:** a stuck agent can repeat the same failing step for hours and burn your usage. Like a fuse, this trips before the damage. It only counts exact repeats, so normal busy work (many different steps) is never blocked.
- **Proof:** `tests/unit/test_c_loop_breaker.py`: repeats are blocked, ping-pong loops are blocked, 40 different calls pass, and a broken history file never stops work. Limits are in `config/budgets.toml`.

## 5. Guard and sandbox: locks on the doors
- **What:** two layers. The real lock is Claude Code's operating-system sandbox and deny rules (`config/claude-code-settings.json`): the agent physically can't read keys, `.env` files or `private/`. On top, `tools/hooks/guard.py` refuses risky commands early and asks Ashish before anything outside the project (pushing code, installing packages, sending messages).
- **Why:** an AI agent can be tricked by text it reads (prompt injection). Rules written in a prompt can be talked around; locks enforced by the system can't.
- **Proof:** `tests/unit/test_b_hooks.py`, `test_c_adversarial.py`, and `tools/live/permission-probe.sh` (a live probe run after each Claude Code upgrade). In Phase 3 all 7 live attacks were blocked; see `reports/phase-3/adversarial-suite.md`.

## 6. Developer + 3 testers loop: no one marks their own homework
- **What:** a builder agent writes code; three separate tester agents check it: A for the spec, B for how parts work together, C for attacks and regressions. All traffic goes through the orchestrator.
- **Why:** an agent that tests its own code tends to pass it. In Phase 3 the testers found 13 defects in one new command that its own spec tests had passed.
- **Proof:** `reports/phase-3/dev-test-loop.md`. Every test run is stored as a record that can't be quietly changed (`./abos test`).

## 7. Local model with a fact check
- **What:** a small free model on the Mac (qwen2.5:3b through Ollama) does simple data extraction, and a code check (`tools/abos/grounding.py`) confirms every value it returns really appears in the source text.
- **Why:** small models make things up. The check turns "probably right" into "verified or rejected", and private content never leaves the Mac.
- **Proof:** `tests/unit/test_c_grounding.py`, `test_b_localeval.py`, with golden test sets in `tests/eval/golden-tasks/`.

## 8. Secret and memory scans
- **What:** `./abos secrets` and a pre-commit hook stop keys from being committed; `./abos scan-memory` flags instruction-like text planted in memory files.
- **Why:** a leaked key or a poisoned memory note can steer every future session.
- **Proof:** `tests/unit/test_c_adversarial.py`.

## 9. Independent review at the gates
- **What:** at each phase gate a different AI (Muse) reviews the evidence before the project moves on (decision DEC-0002).
- **Why:** a second model catches blind spots the first one shares with itself.
- **Proof:** `reports/phase-2/muse/`, `decisions/DEC-0002-claude-primary-muse-gate-review.md`.

## Honest limits (say these in an interview; it shows judgement)
- The router is advice: nothing forces a live session to obey it.
- The ledger and test records are hash-checked, not signed, so someone with write access could forge them.
- The loop breaker catches exact repeats only; an agent that loops with slightly different arguments each time is not caught yet.
- Costs are watched as plan usage %, not dollars, because the project runs on a Claude Pro plan. A hard dollar cap is required before any pay-per-use API is added (`PROMPT.md` Section 2, Phase 5).
- No live dashboard yet. A local OpenTelemetry → Grafana view is a possible next step.
