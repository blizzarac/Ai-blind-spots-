---
id: token-level-blindness
title: Token-level blindness
category: reasoning-shortcuts
severity: low
detection: verifiable
models-affected: [general]
added: 2026-08-17
last-reviewed: 2026-08-17
trend: improving
summary: >-
  Counting letters, manipulating characters, and precise arithmetic on digit
  strings fail systematically because the model never sees characters — it
  sees tokens.
sources:
  - title: "McCoy et al., \"Embers of Autoregression\" (PNAS 2024) — counting and character-task probability effects"
    url: https://arxiv.org/abs/2309.13638
---

## The failure

"How many r's are in strawberry?" became a meme because models kept saying
two. The same root failure shows up as: wrong character counts, botched
string reversal, failed acrostics, unreliable "words ending in -ing"
filters, off-by-one in enumerated lists, and arithmetic errors that cluster
on carrying and digit alignment. These look like trivial reasoning bugs;
they're actually input-representation bugs, which is why they coexist with
graduate-level performance on other tasks — and why users who extrapolate
from "can't count letters" to "can't reason" (or from "solves math
olympiad problems" to "can count anything") both misjudge the tool.

### Minimal repro

```text
1. How many times does the letter "e" appear in the word
   "perseverance"? Answer with a number only.
2. Reverse the string "acknowledgment" character by character.
3. List exactly 17 animals. Number them.
```

**Failure signature:** (1) any answer but 4; (2) any deviation in the
reversed string (compare mechanically); (3) a list of 16 or 18. "Answer
with a number only" matters: it suppresses chain-of-thought workarounds, and
the failure is in the direct pathway. Models with visible reasoning enabled
often pass by spelling the word out letter-by-letter first — run the repro
in both modes and note which one you're actually measuring; production calls
with thinking disabled or exhausted get the direct pathway.

**Documented:** counting was one of McCoy et al.'s core tasks — accuracy
was strongly modulated by whether the *answer* was a high-probability number
(GPT-4 counted 30-item lists far better than 29-item lists), demonstrating
the output-prior mechanism on top of the tokenization one. The
strawberry/r's failure was reproduced publicly across GPT-4o, Claude 3, and
Llama 3-era models throughout 2024. **Last checked:** 2026-08-17.

## Why it happens

BPE-style tokenizers map "strawberry" to one or two tokens; the letter-level
composition of a token is not part of the input — the model only knows a
token's spelling to the extent training text happened to discuss it
("straw" + "berry", spelling bees, rhymes). Character operations therefore
run on remembered facts about tokens rather than on the characters
themselves. Counting adds a second mechanism: transformers have no built-in
loop counter, so exact cardinality must be simulated in fixed-depth
computation, which degrades with length and gets pulled toward
high-frequency round numbers (the Embers effect). Digit arithmetic inherits
both problems via multi-digit tokens.

## Detection

- Fully verifiable: character-level claims can be checked with one line of
  code. In any pipeline where the model filters, counts, sorts, or
  transforms strings, assert the result mechanically — `len()`, regex,
  checksum — and treat the model's number as a proposal.
- Audit for hidden instances: "summarize in exactly 50 words", "keep lines
  under 80 chars", "generate a 10-item list" are all count constraints the
  model will violate at some rate; grep your prompts for numeric
  constraints and add validators for each.

## Mitigation

- Move the operation out of the model: counting, reversing, exact-length
  formatting, and arithmetic belong in code. The strongest pattern is
  model-writes-code-that-computes rather than model-computes — tool-enabled
  agents largely bypass this blind spot.
- If the model must do it, force decomposition: "spell the word one letter
  per line, marking each e, then count the marks." Externalizing state into
  generated tokens substitutes for the missing loop counter.
- Design tolerant constraints: "about 50 words" where exactness doesn't
  matter, plus a truncating validator where it does.

## Status

Improving through two routes that don't fix the core: reasoning modes
decompose spelling tasks into token-externalized steps (and vendors patched
the famous memes specifically — strawberry now passes on frontier models,
so use less famous words when testing), and tool use sidesteps the
representation entirely. The tokenized input remains character-blind, so
novel character-level tasks without decomposition still fail. Byte-level
model architectures would remove the root cause; none is deployed at the
frontier as of this review.
