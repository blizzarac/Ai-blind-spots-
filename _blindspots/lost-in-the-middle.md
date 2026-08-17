---
id: lost-in-the-middle
title: Lost in the middle
category: context-failures
severity: high
detection: statistical
models-affected: [general]
added: 2026-08-17
last-reviewed: 2026-08-17
trend: improving
summary: >-
  Retrieval from the context window is position-dependent — information
  placed mid-context is used markedly worse than the same information at the
  start or end.
sources:
  - title: "Liu et al., \"Lost in the Middle: How Language Models Use Long Contexts\" (TACL 2023)"
    url: https://arxiv.org/abs/2307.03172
  - title: "Reference implementation and data (nelson-liu/lost-in-the-middle)"
    url: https://github.com/nelson-liu/lost-in-the-middle
---

## The failure

A model with a long context window accepts your 40 documents, but whether it
*uses* a fact depends on where the fact landed. Accuracy as a function of
position traces a U-shape: strong at the beginning (primacy), strong at the
end (recency), degraded in the middle — in the original measurements,
mid-context accuracy on multi-document QA fell below answering with *no
documents at all*. "It fits in the window" and "it will be attended to" are
different claims.

### Minimal repro

Needle-in-a-haystack, self-assembled: take ~30 short unrelated documents,
insert one sentence containing a fact you invented (so it can't come from
training data), and ask for it. Run the identical prompt with the needle
placed first, middle (position ~15), and last. Repeat ~20× per position.

```text
Here are 30 project status notes.

[doc 1] ...
[doc 15] ... The Meridian project's build ID is KX-4471. ...
[doc 30] ...

What is the Meridian project's build ID? Answer from the notes above.
```

**Failure signature:** a significant accuracy dip at the middle position
relative to first/last. The effect size varies by model and context length —
on current frontier models with 30 short docs it may be small, so also test
at 50–75% of the model's maximum context, where the U-curve is more
pronounced.

**Documented:** Liu et al. (2023) measured the U-shaped curve on GPT-3.5-
Turbo (4k/16k), Claude 1.3 (100k), MPT-30B and LongChat-13B, on
multi-document QA and key-value retrieval; GPT-3.5-Turbo's mid-context
performance dropped ~20+ points below its closed-book baseline.
**Last checked:** 2026-08-17.

## Why it happens

Multiple contributing mechanisms, none fully settled: causal attention plus
positional encoding schemes (and their extrapolation tricks) systematically
favor early tokens, while recency is favored by the local structure of
next-token prediction; and training data rarely contains supervision that
rewards retrieving from deep middle positions — instruction-tuning examples
overwhelmingly put the relevant material near the question. The result is an
attention prior over positions that the model applies regardless of where
your important content actually is.

## Detection

- Position-sweep eval: before trusting any long-context pipeline, run the
  needle test above across positions and context lengths *on your model
  version and your document format* — the curve is not transferable.
- In RAG systems, log the rank/position of the retrieved chunk that
  contained the true answer for failed queries; a failure cluster at middle
  positions is this blind spot, not a retrieval-quality problem.
- Treat silent omission as the signature: the model doesn't say "I couldn't
  find it" — it answers from the wrong document or from parametric memory.

## Mitigation

- Order by importance, exploit the U: put the most relevant retrieved
  chunks at the very beginning and/or very end of the context; put the
  instructions and question at the end, after the documents.
- Re-rank before stuffing: retrieving 40 chunks and dumping them in order
  is strictly worse than re-ranking to 8 well-placed ones — more context is
  not more recall.
- For exhaustive tasks (audit every document), iterate: map over documents
  in small batches and reduce, rather than one giant window; position
  effects shrink as contexts shrink.

## Status

Improving measurably: long-context training recipes now target this
directly, and current frontier models post near-ceiling needle-retrieval
scores at lengths where 2023 models collapsed. But simple needle tests
understate real workloads — position sensitivity still shows up on
paraphrased facts, multi-hop aggregation, and very full windows. The
original benchmark remains a good harness; run it with your own needles at
your own lengths.
