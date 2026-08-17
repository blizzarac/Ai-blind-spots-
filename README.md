# Blind Spot Atlas

A field guide to systematic AI failure modes — where LLMs *predictably*
fail. Not a gotcha collection: a taxonomy. Each entry explains the failure,
why it happens mechanistically, how to detect it in production, and how to
work around it.

**Site:** https://blizzarac.github.io/Ai-blind-spots-/
**Machine-readable index:** https://blizzarac.github.io/Ai-blind-spots-/atlas.json

## Categories

| category | covers |
|---|---|
| confabulation | invented APIs and packages, phantom citations |
| sycophancy | agreement under pushback, false premise acceptance |
| calibration | confident wrongness, refusing what it knows |
| context-failures | lost in the middle, instruction decay over long chats |
| reasoning-shortcuts | familiar-pattern override, token-level blindness |
| knowledge-boundaries | cutoff blindness, popularity bias |

## What keeps it honest

Every published entry carries a **minimal reproducible example, dated, with
a model version**, and cited sources. Entries without a repro live in
[`drafts/`](drafts/) and don't publish. CI
([`.github/workflows/validate.yml`](.github/workflows/validate.yml))
schema-validates every entry against
[`schema/blindspot.schema.json`](schema/blindspot.schema.json) and rejects
entries missing the repro block.

Why so strict: an AI writing about AI blind spots will confidently include
blind spots that are folklore rather than real. The repro rule isn't
hygiene — it's the epistemics of the whole thing.

## Using the atlas as a skill source

`atlas.json` contains every entry's metadata, summary, full body text, and
sources — one fetch gives an agent the whole taxonomy:

```bash
# All confabulation entries, for injection into a code-review agent:
curl -s https://blizzarac.github.io/Ai-blind-spots-/atlas.json \
  | jq '[.entries[] | select(.category == "confabulation")]'

# Just the detection guidance across all entries:
curl -s https://blizzarac.github.io/Ai-blind-spots-/atlas.json \
  | jq -r '.entries[] | "## \(.title)\n\(.summary)\n"'
```

## Repository layout

```
_blindspots/     published entries (one markdown file per blind spot)
drafts/          plausible but unverified entries — never published
categories/      one page per category
schema/          JSON Schema for entry frontmatter
scripts/         validate_entries.py — run before committing
_layouts/, _data/, _config.yml   Jekyll (GitHub Pages native, no build CI)
atlas.json       Liquid template that renders the machine-readable index
```

## Local development

GitHub Pages builds the site natively — no CI needed. To preview locally:

```bash
gem install bundler && bundle install
bundle exec jekyll serve   # http://localhost:4000/Ai-blind-spots-/
```

To validate entries (same check CI runs):

```bash
pip install pyyaml jsonschema
python3 scripts/validate_entries.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — written so an AI agent can follow
it cold. New entries via PR; one entry per PR; the validator is the
gatekeeper.
