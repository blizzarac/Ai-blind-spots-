---
layout: default
title: Home
---

# Blind Spot Atlas

A field guide to systematic AI failure modes — where LLMs *predictably* fail.
Not a gotcha collection: a taxonomy. Each entry explains the failure, why it
happens mechanistically, how to detect it in production, and how to work
around it.

Every published entry carries a **dated, reproducible example** with a model
version. Entries without one live in `drafts/` and don't publish — an AI
writing about AI blind spots will otherwise confidently include folklore, so
the repro rule is the epistemics of the whole thing.

## Use it as a machine

The entire atlas is exported as a single JSON file, so an agent can consume it
as a skill source — e.g. inject the relevant blind spots into a review agent's
context:

```bash
curl -s {{ site.url }}{{ site.baseurl }}/atlas.json | jq '.entries[] | select(.category == "confabulation")'
```

## Entries

{% for cat in site.data.categories %}
### [{{ cat[1].title }}]({{ '/categories/' | append: cat[0] | append: '/' | relative_url }})

{{ cat[1].description }}

{% assign entries = site.blindspots | where: "category", cat[0] | sort: "id" %}
{% for e in entries %}- **[{{ e.title }}]({{ e.url | relative_url }})** <span class="badge severity-{{ e.severity }}">{{ e.severity }}</span> — {{ e.summary }}
{% endfor %}
{% endfor %}
