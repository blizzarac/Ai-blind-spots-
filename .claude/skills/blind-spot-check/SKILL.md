---
name: blind-spot-check
description: >-
  Check work against the Blind Spot Atlas — an evidence-backed taxonomy of
  systematic LLM failure modes (confabulation, sycophancy, calibration,
  context failures, reasoning shortcuts, knowledge boundaries), each entry
  with detection and mitigation guidance. Use this whenever reviewing
  AI-generated code or text, designing or debugging anything built on an LLM
  (prompts, agents, RAG pipelines, chat products, eval suites), or when the
  user mentions hallucinations, model mistakes, AI reliability, "what could
  go wrong", or reviewing output that came from a model — even if they don't
  name the atlas.
---

# Blind Spot Check

The Blind Spot Atlas (https://blizzarac.github.io/Ai-blind-spots-/) documents
where LLMs *predictably* fail. Every entry is repro-backed and cited — no
folklore. Each has five sections: the failure, why it happens, **detection**
(how to catch it), **mitigation** (how to work around it), and status
(whether newer models improve it). This skill pulls the entries relevant to
the current task into context so the review or design work checks against
known failure modes instead of vibes.

## Step 1 — Fetch the relevant entries

Run the bundled script (Python 3 stdlib only). It fetches the live atlas,
falls back to a 24h cache and then to a bundled snapshot if the network is
blocked, and prints entries as markdown ready to reason over:

```bash
python3 scripts/fetch_atlas.py --categories <cat1,cat2> --format standard
```

Pick categories by task — pull the union when in doubt; the whole atlas is
small (~12 entries), so over-fetching is cheap:

| Task at hand | Categories to fetch |
|---|---|
| Reviewing AI-generated code | confabulation, reasoning-shortcuts, knowledge-boundaries |
| Reviewing AI-generated text/research/citations | confabulation, calibration, knowledge-boundaries |
| Designing prompts or agent loops | context-failures, sycophancy, reasoning-shortcuts |
| Building RAG / long-context pipelines | context-failures, knowledge-boundaries |
| Chat product / conversational UX | sycophancy, context-failures, calibration |
| Writing evals or QA for an LLM feature | everything: `--all` |
| Debugging weird model behavior | start `--all --format brief`, then `--ids` the suspects |

Useful flags:

- `--all` — every entry. `--list` — one line per entry (id, category, severity).
- `--ids invented-apis,phantom-citations` — specific entries.
- `--format brief|standard|full` — brief = summaries only; standard =
  summary + detection + mitigation (the default, right for most work);
  full = complete entry bodies including repro steps (use when writing
  evals, since repros seed test cases).
- `--url <url-or-path>` — alternate atlas (a fork, a local build).

If the script reports it used the bundled snapshot, say so in your output —
the snapshot is dated and the live atlas may have newer or corrected
entries.

## Step 2 — Apply the entries to the task

Don't paste the atlas at the user. Use it:

- **Reviewing:** treat each entry's *Detection* guidance as checklist items.
  Where an entry says a claim type is mechanically verifiable (imports,
  package names, citations, version numbers), actually verify — run the
  import, resolve the DOI, check the registry — rather than eyeballing.
- **Designing:** fold *Mitigation* guidance into the design you propose
  (e.g., re-rank + ends-placement for long context, paraphrase-retry for
  refusals, premise extraction before answering).
- **Writing evals:** the *Minimal repro* blocks in `--format full` are
  seed recipes — adapt them to the user's domain rather than copying the
  famous examples, which vendors patch specifically.
- **Cite what you used.** When a finding or recommendation traces to an
  atlas entry, name the entry id (e.g., "this is `invented-apis` — verify
  against the registry") and link it:
  `https://blizzarac.github.io/Ai-blind-spots-/blindspots/<id>/`. That lets
  the user read the mechanism and evidence themselves.
- **Stay honest about scope.** The atlas documents *systematic* failure
  modes with dated evidence. If something you notice isn't covered by an
  entry, say so plainly instead of stretching an entry to fit — and mention
  that the atlas takes contributions with repro steps.

## Category cheat sheet

- `confabulation` — invents specifics: APIs, packages, citations
- `sycophancy` — agrees instead of correcting: pushback flips, false premises
- `calibration` — confidence ≠ accuracy: assured wrongness, needless refusal
- `context-failures` — has it but doesn't use it: mid-context loss, instruction decay
- `reasoning-shortcuts` — pattern-match over compute: familiar-pattern override, token blindness
- `knowledge-boundaries` — edges of training data: cutoff staleness, long-tail fabrication
