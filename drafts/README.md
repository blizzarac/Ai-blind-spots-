# Drafts

Entries in this folder are **not published** — they are excluded from the
Jekyll build and from `atlas.json`.

An entry lives here when it is plausible but lacks what publication
requires: a **minimal reproducible example, dated, with a model version**,
plus a citable source or a repro you actually ran.

This rule is the epistemics of the whole project. An AI (or a human)
writing about AI blind spots will confidently include blind spots that are
folklore rather than real. The repro requirement is what separates the
atlas from vibes.

To promote a draft:

1. Add the repro: exact prompt, failure signature, date, model version(s)
   observed, and sources.
2. Fill in all required frontmatter (see `schema/blindspot.schema.json`).
3. Move the file to `_blindspots/` and open a PR — CI validates it.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full checklist.
