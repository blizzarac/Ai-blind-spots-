---
id: uniform-confidence
title: Confident wrongness
category: calibration
severity: high
detection: statistical
models-affected: [general]
added: 2026-08-17
last-reviewed: 2026-08-17
trend: persistent
summary: >-
  The rhetorical confidence of an answer carries almost no information about
  whether it's correct — wrong answers arrive in the same assured tone as
  right ones.
sources:
  - title: "Kadavath et al., \"Language Models (Mostly) Know What They Know\" (2022)"
    url: https://arxiv.org/abs/2207.05221
  - title: "Tian et al., \"Just Ask for Calibration\" (EMNLP 2023)"
    url: https://arxiv.org/abs/2305.14975
---

## The failure

Humans use fluency and assertiveness as a proxy for reliability. LLM output
breaks that proxy: the surface register is nearly constant, so a
hallucinated detail and a well-grounded fact are delivered with
indistinguishable poise. The failure isn't that the model is wrong — it's
that nothing in the prose tells you *when* it's wrong.

### Minimal repro

Build a 20-question quiz mixing 10 easy facts with 10 obscure ones from the
same domain (e.g., release years of famous vs. niche software). Ask each
question separately, then rate each answer's *tone* (hedged vs. assertive)
before checking correctness.

```text
In what year was the first stable release of SQLite published?
Answer in one sentence. Then state your confidence as a
percentage that your answer is exactly right.
```

**Failure signature:** tone does not separate the correct from the incorrect
answers — you'll find flatly asserted errors on the obscure half. Then ask
"How confident are you, 0–100%?" after each answer: RLHF-era chat models
cluster stated confidence in a narrow high band (typically 80–100%) with
wrong answers inside it. Plot stated confidence vs. accuracy; the
miscalibration is the gap between the curve and the diagonal.

**Documented:** Kadavath et al. (2022) showed base models can be well
calibrated on multiple-choice self-evaluation, while Tian et al. (2023)
showed RLHF chat models' conditional probabilities are poorly calibrated and
verbalized confidence, though better, remains systematically overconfident
(measured on GPT-3.5, GPT-4, Claude 1/2-era models; ECE improvements of ~50%
from prompting alone). **Last checked:** 2026-08-17.

## Why it happens

Pretraining text pairs assertive register with encyclopedic content, so the
assertive style is learned as *format*, independent of truth. Preference
tuning then actively suppresses hedging, because raters dislike wishy-washy
answers — pushing stated and stylistic confidence into a high, narrow band.
Meanwhile the information that *would* support calibration (the model's own
token-level uncertainty) is real — Kadavath et al. show models can often
predict what they know — but it isn't surfaced in the prose channel. The
tone you read and the uncertainty the model has are two different systems.

## Detection

- Never read confidence off the prose. Measure it: sample the same question
  N times at temperature and use answer agreement (self-consistency) as an
  uncertainty proxy — disagreement across samples is the single cheapest
  wrongness detector in production.
- Elicit numeric confidence explicitly and *calibrate it offline*: run a
  labeled sample, fit the mapping from stated confidence to observed
  accuracy, and apply that correction in your pipeline (per Tian et al.,
  verbalized scores are usable after recalibration).
- Route by verifiability: claims that can be checked mechanically (dates,
  APIs, citations) should be checked, not trusted at any confidence level.

## Mitigation

- Design UX so users never see fluency as the only signal: attach provenance
  (retrieved sources), or attach your calibrated confidence score, or say
  nothing about confidence — but don't let the prose imply it.
- Set per-task confidence thresholds with escalation: below threshold, the
  system retrieves, asks a clarifying question, or hands off to a human
  rather than answering.
- For internal agent chains, pass structured (claim, confidence, evidence)
  tuples between steps instead of prose, so downstream agents don't inherit
  upstream tone as truth.

## Status

Persistent in the prose channel — assertive style survives because users
prefer it; no major vendor ships hedge-proportional-to-uncertainty prose by
default. Partially recoverable by measurement: self-consistency sampling and
recalibrated verbalized confidence work on current models. Reasoning-tuned
models are better calibrated on math/code, less so on open-domain facts.
Recalibrate per model version; the confidence-to-accuracy mapping does not
transfer.
