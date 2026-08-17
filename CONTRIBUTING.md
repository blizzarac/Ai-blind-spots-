# Contributing to the Blind Spot Atlas

This document is written so that a human — or an AI agent with no prior
context — can add a valid entry by following it literally.

## The one rule

**Every published entry needs a reproducible example, dated, with a model
version.** If you cannot provide one, put the entry in `drafts/` instead of
`_blindspots/`. Drafts don't publish and don't appear in `atlas.json`.

This rule exists because an AI writing about AI blind spots will confidently
include blind spots that are folklore rather than real. If you are an AI
agent contributing here: this rule is about *you*. Do not cite papers from
memory — verify every URL resolves and every title matches before
committing. Do not invent observation dates or model versions.

## Adding an entry, step by step

1. **Check for duplicates.** Read `atlas.json` (or list `_blindspots/`).
   If your failure mode is a special case of an existing entry, extend that
   entry instead.

2. **Create `_blindspots/<id>.md`** where `<id>` is kebab-case
   (`^[a-z0-9]+(-[a-z0-9]+)*$`) and equals the filename. Start from the
   template below.

3. **Fill the frontmatter.** All fields are required; the schema is
   `schema/blindspot.schema.json` and CI enforces it:

   | field | allowed values |
   |---|---|
   | `id` | kebab-case, = filename |
   | `title` | 3–80 chars |
   | `category` | `confabulation`, `sycophancy`, `calibration`, `context-failures`, `reasoning-shortcuts`, `knowledge-boundaries` |
   | `severity` | `low`, `medium`, `high` — impact when it fires in an engineering workflow |
   | `detection` | `verifiable` (mechanically checkable per instance), `statistical` (a rate over a batch), `manual` (needs human judgment) |
   | `models-affected` | non-empty list; use `[general]` unless family-specific |
   | `added`, `last-reviewed` | `YYYY-MM-DD` |
   | `trend` | `improving`, `persistent`, `worsening`, `unclear` — must match what the Status section says |
   | `summary` | 40–400 chars, one or two sentences |
   | `sources` | non-empty list of `{title, url}`; `url` must be `https://` and must resolve |

4. **Write the five sections, in this order, with these exact headings:**
   - `## The failure` — one paragraph plus a `### Minimal repro` block
     containing: the exact prompt in a fenced code block, a **Failure
     signature** (what output counts as the failure — make it checkable), a
     **Documented** line naming model versions and dates for the evidence,
     and a `**Last checked:** YYYY-MM-DD` line.
   - `## Why it happens` — the mechanistic explanation (next-token
     prediction, RLHF pressure, tokenization, attention — whatever actually
     drives it). No hand-waving; if the mechanism is contested, say so.
   - `## Detection` — how to catch it in production: verifiable claims,
     self-consistency checks, eval designs.
   - `## Mitigation` — prompting patterns, tooling, and when to just not
     use an LLM.
   - `## Status` — does this improve with newer models? Link evidence.
     Must agree with the `trend` field.

5. **Validate locally:**

   ```bash
   pip install pyyaml jsonschema
   python3 scripts/validate_entries.py
   ```

   Fix everything it reports. CI runs the same script on your PR.

6. **Open a PR** with one entry per PR. In the PR description, state where
   the repro evidence comes from: a paper (link it), a public incident
   (link it), or your own run (paste the transcript, date, and model
   version).

## Evidence standards

- **Repro prompts must be runnable by a stranger.** No "ask it something
  obscure" — the exact text, plus what counts as failure.
- **Statistical failures need rates, not anecdotes.** If the failure is
  stochastic, the repro must say how many runs and what signature to
  measure.
- **Date everything.** Model behavior changes; an undated observation is
  unusable. `last-reviewed` is when a human (or agent) last confirmed the
  entry's claims still hold.
- **Distinguish documented from expected.** "Documented: GPT-4, 2024
  (paper)" is evidence. "This probably also affects newer models" is a
  hypothesis — label it as one.
- **Famous repros go stale.** Vendors patch meme examples specifically
  (see `token-level-blindness`). Prefer repro *recipes* (how to construct
  a fresh instance) over single celebrated instances.

## Updating an entry

- Re-verified the claims? Bump `last-reviewed`.
- Behavior changed on new models? Update `## Status` and `trend` — do not
  delete the historical evidence; the trajectory is data.
- Repro no longer reproduces on any current model and no successor repro
  exists? Move the entry to `drafts/` with a note. The atlas must only
  assert what currently holds or is clearly marked historical.

## For AI agents specifically

- `atlas.json` is the machine-readable index: categories, metadata,
  summaries, full body text, and source URLs for every published entry.
- Before writing, fetch and read at least one cited source for the entry
  you're touching. If a URL 404s, fixing that citation *is* the
  contribution.
- Run the validator before committing. If it fails, fix the entry, not the
  validator.
- Never weaken `scripts/validate_entries.py` or the schema to make an
  entry pass.
