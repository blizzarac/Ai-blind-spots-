---
id: multi-turn-decay
title: Instruction decay over long conversations
category: context-failures
severity: medium
detection: statistical
models-affected: [general]
added: 2026-08-17
last-reviewed: 2026-08-17
trend: persistent
summary: >-
  Constraints set early in a conversation stop being honored as turns
  accumulate — and once a model commits to a wrong assumption mid-dialogue,
  it rarely recovers.
sources:
  - title: "Laban et al., \"LLMs Get Lost in Multi-Turn Conversation\" (2025)"
    url: https://arxiv.org/abs/2505.06120
  - title: "Simulation code (microsoft/lost_in_conversation)"
    url: https://github.com/microsoft/lost_in_conversation
---

## The failure

Turn 1: "Always answer in English, keep code snippets under 20 lines, never
use pandas." Turn 14: the model replies with a 60-line pandas solution. No
single turn broke the rule — it eroded. The same erosion applies to the
model's own working state: an assumption adopted in an early turn (often to
fill in something you hadn't specified yet) persists even after later turns
contradict it. The conversation doesn't just forget your instructions; it
calcifies its own early guesses.

### Minimal repro

Give three arbitrary, checkable constraints in turn 1, then conduct 15
turns of ordinary, on-topic work that never mentions the constraints again.
Score each reply for compliance with all three.

```text
Turn 1: For this whole conversation: (1) prefix every reply with
        "OK:", (2) never use bullet lists, (3) write all Python
        identifiers in snake_case. Confirm, then help me build a
        small CLI tool for parsing CSV files.
Turns 2–16: ordinary follow-up requests about the tool.
```

**Failure signature:** compliance decays with turn number rather than
failing immediately — typically the visible-format rule (prefix) survives
longest and the content rules silently drop. Then test recovery: point out
the violation and continue; measure whether compliance is restored durably
or for one turn only.

**Documented:** Laban et al. (2025) simulated 200,000+ conversations across
15 models (including GPT-4.1, Gemini 2.5 Pro, Claude 3.7 Sonnet era) and
found an average 39% performance drop on six generation tasks when
instructions arrived sharded over turns instead of all at once — driven less
by declining capability than by exploding unreliability: models answer
prematurely, over-rely on their own earlier (wrong) attempts, and "when LLMs
take a wrong turn, they get lost and do not recover."
**Last checked:** 2026-08-17.

## Why it happens

Three mechanisms compound. Recency-weighted attention means turn-1
constraints compete against thousands of newer tokens (see
[lost in the middle](../lost-in-the-middle/) — early instructions
literally sit in the decaying part of the position curve as the chat grows).
Self-conditioning: the model's own prior outputs are context too, so every
reply that drifted slightly becomes evidence about what this conversation's
"style" is — drift is self-reinforcing, and an early wrong assumption gets
restated and thereby re-entrenched each turn. And training distribution:
assistant training heavily features short dialogues where instructions and
response are adjacent; 20-turn constraint-carrying is thinly represented.

## Detection

- Compliance probes in CI: for chat products, replay long scripted
  conversations and assert programmatically checkable constraints at every
  turn — decay curves per model version, not spot checks.
- In production, validate outputs against session-level constraints
  (format, language, forbidden APIs) with a deterministic checker on every
  turn, not just after the first response.
- Watch for assumption lock-in: when a long agent session goes wrong,
  inspect the earliest turns for an unforced assumption; the root cause is
  usually old, not recent.

## Mitigation

- Re-inject, don't trust memory: put standing constraints in the system
  prompt (which many stacks re-send every call) or mechanically re-append a
  constraint summary to each request rather than relying on turn-1 text.
- Prefer fresh contexts over long ones: Laban et al.'s practical corollary
  is that consolidating requirements and restarting ("compile the
  conversation into one complete prompt") outperforms continuing a lost
  conversation. Agent frameworks should checkpoint-and-restart rather than
  accumulate.
- Structure over prose: constraints enforced by tooling (linters, output
  schemas, response validators) don't decay; move whatever can be
  mechanically checked out of the prompt channel entirely.

## Status

Persistent. This is one of the better-measured failures of the current era,
and the 2025 measurements showed it across every model tested, including
reasoning models — sharded-instruction unreliability was roughly invariant
to model quality. Bigger context windows do not fix it (the information is
in-window; it's the *use* that decays). Expect incremental improvement as
multi-turn training data improves; design as if decay is a law.
