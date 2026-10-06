**This round:** rank 10 · Δ vs baseline +0.042 on 6 paired instances · 2 verified.

## Round `r0061` — `5DPhKi77DLciQzNDr6iCZ2cD41oHcV75vLdf82d3crVnERN6`

**weight 0.0799** · score 0.1062

| | |
|---|---|
| episodes | 24 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1062 |
| standard error (incl. reference term) | 0.061408 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0276 |
| score (mean d after the overfit and copy penalties) | +0.1062 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 24 | 0.36 | — | — | frontier |

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
| `swe-fix-r0061-04` | 9 | `f497b1a2075c1bcb…` | pylint-dev__astroid.b114f6b5.combine_module__8xirwm1z |
| `swe-fix-r0061-05` | 6 | `4f88ced7ef155633…` | oauthlib__oauthlib.1fd52536.combine_file__dm5bqfwa |
| `swe-fix-r0061-10` | 4 | `27aaa1a0884bde5c…` | pylint-dev__astroid.b114f6b5.func_basic__w1sh9kvh |
| `swe-fix-r0061-12` | 5 | `43e3deff59c6f51a…` | oauthlib__oauthlib.1fd52536.func_basic__olaxlnuq |
| `swe-fix-r0061-14` | 3 | `49453a1e6596d707…` | tkrajina__gpxpy.09fc46b3.func_pm_ctrl_invert_if__5d48ok1a |
| `swe-fix-r0061-21` | 2 | `a2272f69a09e7fb8…` | pylint-dev__astroid.b114f6b5.func_pm_class_rm_funcs__cccngbh5 |

</details>