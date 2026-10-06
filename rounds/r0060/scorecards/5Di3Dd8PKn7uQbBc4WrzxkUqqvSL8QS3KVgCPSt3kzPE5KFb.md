**This round:** rank 6 · Δ vs baseline +0.167 on 6 paired instances · 2 verified.

## Round `r0060` — `5Di3Dd8PKn7uQbBc4WrzxkUqqvSL8QS3KVgCPSt3kzPE5KFb`

**weight 0.1208** · score 0.1389

| | |
|---|---|
| episodes | 18 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1389 |
| standard error (incl. reference term) | 0.078856 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0380 |
| score (mean d after the overfit and copy penalties) | +0.1389 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 18 | 0.30 | — | — | frontier |

### Check the grading yourself

6 of 6 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`. The commitment is in the task record — under `rounds/<id>/tasks/` when you were shown the scored tasks, under `rounds/<id>/evaluated/` when you were shown previews — and `rounds/queue.json` carried the digest of those records before the round opened. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json
salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (6) — full record in `reveal.json`</summary>

| task | withheld checks | salt | source |
|---|---|---|---|
| `swe-fix-r0060-03` | 8 | `ea5ff2e9f9f0f2dc…` | marshmallow-code__marshmallow.9716fc62.lm_rewrite__zlhsjbno |
| `swe-fix-r0060-05` | 5 | `9e1b61947c462443…` | pylint-dev__astroid.b114f6b5.lm_rewrite__93fwu6eo |
| `swe-fix-r0060-12` | 5 | `05885bb08c583abc…` | pylint-dev__astroid.b114f6b5.combine_file__s7m79zng |
| `swe-fix-r0060-13` | 5 | `3155e63d8c8bb3b8…` | python-openxml__python-docx.0cf6d71f.combine_module__8dpeyxeg |
| `swe-fix-r0060-18` | 1 | `c5ee38bbb18e422d…` | python-openxml__python-docx.0cf6d71f.func_pm_ctrl_shuffle__rjs57w3n |
| `swe-fix-r0060-19` | 1 | `62e292ee3d7d5600…` | tobymao__sqlglot.036601ba.lm_rewrite__du7msnhk |

</details>