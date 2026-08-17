---
id: invented-apis
title: Invented APIs and packages
category: confabulation
severity: high
detection: verifiable
models-affected: [general]
added: 2026-08-17
last-reviewed: 2026-08-17
trend: improving
summary: >-
  The model generates imports, function signatures, or package names that look
  idiomatic but don't exist — and installs of hallucinated packages are a real
  supply-chain attack surface.
sources:
  - title: "Spracklen et al., \"We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs\" (USENIX Security 2025)"
    url: https://arxiv.org/abs/2406.10279
  - title: "USENIX ;login: summary — Package Hallucinations: How LLMs Can Invent Vulnerabilities"
    url: https://www.usenix.org/publications/loginonline/we-have-package-you-comprehensive-analysis-package-hallucinations-code
---

## The failure

Asked for code against a real library, the model produces a method that the
library has never shipped — or recommends installing a package that doesn't
exist on PyPI or npm. The output is *idiomatic*: the invented name follows the
library's naming conventions, takes plausible arguments, and sits next to
perfectly real calls, which is exactly why review misses it.

### Minimal repro

Ask, with no tools or web access enabled:

```text
Using the Python `requests` library, show how to retry a request
with exponential backoff using the built-in retry helper on the
Session object.
```

**Failure signature:** `requests.Session` has no built-in retry helper —
retries live in `urllib3.util.Retry` mounted via an adapter. Models frequently
invent something like `session.retry(...)` or a `Session(retries=3)` kwarg, or
blend the urllib3 API into `requests` with wrong names. Any answer that calls
a retry method directly on `Session` is a confabulation.

**Documented:** Spracklen et al. (2024) generated 576,000 code samples across
16 models and found ~20% of package recommendations pointed to nonexistent
packages — 5.2% for commercial models (GPT-4: measured in-paper, GPT-3.5,
Gemini, Cohere) and 21.7% for open models, with hallucinated names highly
repeatable across runs. **Last checked:** 2026-08-17.

## Why it happens

Next-token prediction learns the *distribution* of API shapes, not a symbol
table. A method name is generated because it is probable given the
surrounding code, and "the method that *should* exist by this library's
conventions" is often more probable than the awkward real one. Nothing in the
sampling loop consults ground truth, so fluency and existence are decoupled.
Repeatability makes it worse: the same wrong-but-plausible name is sampled
again and again, which is what makes "slopsquatting" (pre-registering
commonly hallucinated package names with malicious code) a viable attack.

## Detection

This is the friendly case: existence claims are cheap to verify mechanically.

- Compile, import, or type-check every generated snippet before a human reads
  it; `ImportError`/`AttributeError` is your detector.
- Resolve every dependency the model suggests against the real registry
  (`pip index versions X`, `npm view X`) *before* installing. Treat a package
  the model named that has few downloads or a recent first-publish date as
  hostile until proven otherwise.
- In agent pipelines, run linters/LSP diagnostics on model output as a gate —
  unresolved symbols are a hard fail, not a warning.

## Mitigation

- Ground the model: put the actual signatures in context (paste the relevant
  docs, or use an agent setup that can read the installed package source).
  Hallucination rates drop sharply when the true API is in the window.
- Prefer tool-enabled workflows for dependency selection; never let a model
  pick a dependency name that goes straight into a lockfile without registry
  verification.
- Pin an allowlist of dependencies in agent environments so an invented
  package fails closed.

## Status

Improving but not solved: commercial models hallucinate packages at roughly a
quarter of the rate of open models in the Spracklen et al. measurements, and
tool-grounded coding agents (which can import and test) largely mask the
failure. The underlying mechanism is untouched, so it reappears whenever the
model answers from parametric memory — obscure libraries, old versions,
offline use. Re-verify on current models before assuming a rate.
