**This round:** rank 1 · Δ vs baseline +0.194 on 6 paired instances · 2 verified.

## Round `r0058` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 6 |
| mean d (your share of checks passed − the baseline's, same instances) | — |
| standard error (incl. reference term) | — |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0000 |
| correctness gate | not passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** 6 window episodes < 8

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 6 | 0.36 | — | — | unknown |

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
| `swe-fix-r0058-02` | 2 | `5cc9e2decd5e88ef…` | tobymao__sqlglot.036601ba.lm_rewrite__663t8rx9 |
| `swe-fix-r0058-08` | 5 | `0fb5ea0d274bdc20…` | oauthlib__oauthlib.1fd52536.combine_file__yuzvccsq |
| `swe-fix-r0058-13` | 5 | `b6ec08503780c4c5…` | tkrajina__gpxpy.09fc46b3.func_pm_remove_cond__tsjih5g6 |
| `swe-fix-r0058-16` | 6 | `e46501d49ca01a2a…` | pylint-dev__astroid.b114f6b5.func_basic__wprw8nys |
| `swe-fix-r0058-20` | 6 | `96c3da6a16f2fabb…` | tobymao__sqlglot.036601ba.combine_file__bdzyxq2y |
| `swe-fix-r0058-22` | 7 | `d36620a2e63bd033…` | cantools__cantools.0c6a7871.func_basic__dj8jkeg1 |

</details>