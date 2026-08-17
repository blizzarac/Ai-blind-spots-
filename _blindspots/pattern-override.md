---
id: pattern-override
title: Familiar-pattern override
category: reasoning-shortcuts
severity: medium
detection: manual
models-affected: [general]
added: 2026-08-17
last-reviewed: 2026-08-17
trend: persistent
summary: >-
  When a problem closely resembles a famous one, the model answers the famous
  version — the memorized template overrides the details you actually
  changed.
sources:
  - title: "McCoy et al., \"Embers of Autoregression\" (PNAS 2024)"
    url: https://arxiv.org/abs/2309.13638
  - title: "McCoy et al., \"When a language model is optimized for reasoning, does it still show embers of autoregression?\" (2024) — same effects in OpenAI o1"
    url: https://arxiv.org/abs/2410.01792
---

## The failure

Present a variant of a classic puzzle with one load-bearing detail changed,
and the model solves the *classic*, not your variant. The changed detail is
read, sometimes even repeated back — and then the memorized solution
template takes over anyway. This is the failure mode behind wrong answers to
trick questions the model "should" find trivial, and it generalizes beyond
puzzles: any input that is a near-duplicate of a high-frequency training
pattern (a famous algorithm, a standard contract clause, a well-known API
flow) risks being autocompleted toward the canonical version.

### Minimal repro

```text
A man and his son are in a car accident. The man dies at the scene.
The son is rushed to the hospital. The surgeon — who is the boy's
father — looks at him and says "I can't operate on this boy."
Why not?
```

**Failure signature:** the classic riddle's answer ("the surgeon is his
mother") — which is incoherent here, since the surgeon is stated to be the
father (the puzzle as given has no gender twist; a coherent answer must
grapple with the contradiction, e.g. two fathers, or note the setup is
inconsistent with the father having died). Other reliable instances: Monty
Hall with *transparent* doors, the trolley problem where the lever does
nothing, "which weighs more, a pound of feathers or two pounds of bricks."
Failure is graded manually because near-miss answers vary in how much of
the template they import.

**Documented:** McCoy et al. (2023/2024) established the general law —
LLM accuracy tracks the probability of the task and of the output under the
training distribution even in deterministic problems (e.g., GPT-4: 51%
on shift-cipher decoding for rot-13, which is common online, vs. 13% for
rot-2, which is rare — same algorithm, different familiarity). The 2024
follow-up found o1, an explicit reasoning model, still shows the same
qualitative sensitivity, attenuated. **Last checked:** 2026-08-17.

## Why it happens

Next-token prediction rewards reproducing high-probability continuations,
and a near-verbatim famous puzzle makes the famous answer overwhelmingly
probable. The changed detail contributes a few tokens of evidence against
millions of training-set repetitions of the canonical form — the prior
wins. This is not (only) shallow token matching: McCoy et al. show the
effect persists when reasoning is correct step-by-step until the final
answer snaps to the familiar one, i.e. the output prior contaminates even
otherwise-sound derivations.

## Detection

- Perturbation testing: for any task class you rely on, take known-answer
  items, change one load-bearing detail, and check the answer changes
  accordingly. A model that scores the same on original and perturbed sets
  is pattern-matching, not solving.
- Ask for the answer *and* an explicit restatement of the givens first;
  a mismatch between the (correct) restatement and the (template) answer is
  the fingerprint of override.
- Be most suspicious exactly where the model is most fluent: high
  familiarity is the risk factor, so "easy, standard-looking" inputs
  deserve the perturbation check more than exotic ones.

## Mitigation

- Break the surface match: rename entities, reorder clauses, or translate
  the problem into a schematic form (variables instead of the story) before
  asking — distance from the memorized surface weakens the prior.
- Force serial processing: "list each stated fact and mark how it differs
  from the classic version of this problem, then solve" makes the changed
  detail part of the output path. Extended-thinking modes help for the same
  reason, but incompletely (see the o1 result).
- Don't use LLMs as the sole checker for near-boilerplate artifacts
  (contracts, configs, standard algorithms) where the dangerous edit is
  precisely a small deviation from the canonical form — that's the exact
  geometry of this blind spot. Diff against the canonical form
  mechanically instead.

## Status

Persistent, with attenuation: reasoning-optimized models do better on
low-probability variants but the sensitivity to task/output probability
survives (measured directly on o1; the "embers" framing has held up across
model generations). Treat familiarity-dependence as a standing property of
autoregressive LLMs until a model demonstrates otherwise under perturbation
testing.
