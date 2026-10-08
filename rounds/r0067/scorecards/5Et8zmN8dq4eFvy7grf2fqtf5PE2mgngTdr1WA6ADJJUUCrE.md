**This round:** not ranked · Δ vs baseline +0.000 on 8 paired instances · 2 verified.

## Round `r0067` — `5Et8zmN8dq4eFvy7grf2fqtf5PE2mgngTdr1WA6ADJJUUCrE`

**weight 0.0245** · score 0.0175

| | |
|---|---|
| episodes | 38 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0175 |
| standard error (incl. reference term) | 0.033137 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0175 |
| correctness gate | passed |
| Δe | api_calls +0.32 · tool_calls +0.50 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 50 | 0.38 | 0.29 | -0.0911 | frontier |

### Check the grading yourself

8 of 8 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`. The commitment is in the task record — under `rounds/<id>/tasks/` when you were shown the scored tasks, under `rounds/<id>/evaluated/` when you were shown previews — and `rounds/queue.json` carried the digest of those records before the round opened. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json
salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (8) — full record in `reveal.json`</summary>

| task | withheld checks | salt | source |
|---|---|---|---|
| `swe-fix-r0067-04` | 10 | `059823b5ac77759c…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__wirmnh32 |
| `swe-fix-r0067-10` | 4 | `41ce03d2cd4bc745…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__cmfzyvwe |
| `swe-fix-r0067-15` | 1 | `3ac75fba327be0ac…` | pylint-dev__astroid.b114f6b5.pr_2277 |
| `swe-fix-r0067-16` | 1 | `ef3c7c556d07abf8…` | tkrajina__gpxpy.09fc46b3.func_pm_op_change__e6zkx3tu |
| `swe-fix-r0067-18` | 8 | `d37a49af612c306a…` | oauthlib__oauthlib.1fd52536.func_pm_remove_cond__au9r9u5l |
| `swe-fix-r0067-20` | 3 | `34a157462bd90538…` | pylint-dev__astroid.b114f6b5.func_basic__fm3g5c5t |
| `swe-fix-r0067-22` | 3 | `ade524dc2f6cf6b1…` | marshmallow-code__marshmallow.9716fc62.func_pm_ctrl_shuffle__ig827qbg |
| `swe-fix-r0067-25` | 2 | `5bf30c44d09e8ee5…` | cantools__cantools.0c6a7871.func_pm_remove_assign__tnjcndmn |

</details>