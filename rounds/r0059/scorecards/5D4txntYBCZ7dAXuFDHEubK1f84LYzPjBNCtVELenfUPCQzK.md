**This round:** rank 8 · Δ vs baseline +0.083 on 6 paired instances · 1 verified.

## Round `r0059` — `5D4txntYBCZ7dAXuFDHEubK1f84LYzPjBNCtVELenfUPCQzK`

**weight 0.0219** · score 0.0250

| | |
|---|---|
| episodes | 12 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0250 |
| standard error (incl. reference term) | 0.046262 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0250 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 12 | 0.35 | — | — | frontier |

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
| `swe-fix-r0059-03` | 1 | `a543ac4a54cd06fe…` | python-openxml__python-docx.0cf6d71f.func_basic__923nask1 |
| `swe-fix-r0059-07` | 4 | `334edf4518925db6…` | python-openxml__python-docx.0cf6d71f.combine_module__n1c3tg34 |
| `swe-fix-r0059-16` | 5 | `d030251f5fc7fe34…` | cantools__cantools.0c6a7871.combine_file__wpoq4uzr |
| `swe-fix-r0059-17` | 4 | `c664391536ec58e9…` | python-openxml__python-docx.0cf6d71f.func_basic__k0mxg987 |
| `swe-fix-r0059-19` | 2 | `8e8c1544354b85d5…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__ot4ynxcc |
| `swe-fix-r0059-20` | 5 | `3bd708c21d02caa0…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__9for4o3n |

</details>