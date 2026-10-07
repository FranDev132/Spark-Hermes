**This round:** rank 2 · Δ vs baseline +0.300 on 6 paired instances · 3 verified.

## Round `r0062` — `5DSD14t7dACJcd9f8rPdrkMVngRqLUnM3EnM3dHfHLZTHJGf`

**weight 0.1534** · score 0.2211

| | |
|---|---|
| episodes | 30 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.2211 |
| standard error (incl. reference term) | 0.075311 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.1247 |
| score (mean d after the overfit and copy penalties) | +0.2211 |
| correctness gate | passed |
| Δe | api_calls -0.45 · tool_calls -0.31 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 30 | 0.37 | — | — | frontier |

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
| `swe-fix-r0062-01` | 2 | `003cbc80eddacc94…` | oauthlib__oauthlib.1fd52536.lm_rewrite__6g73itv9 |
| `swe-fix-r0062-02` | 3 | `255af3413a947a26…` | oauthlib__oauthlib.1fd52536.combine_module__bazpipkm |
| `swe-fix-r0062-03` | 5 | `653d9b73de690738…` | andialbrecht__sqlparse.e57923b3.combine_file__41rrr227 |
| `swe-fix-r0062-04` | 2 | `f0319a9a56140902…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__4qyelle2 |
| `swe-fix-r0062-06` | 2 | `b4b3c6de9e45e1e6…` | cantools__cantools.0c6a7871.lm_rewrite__rl02thh5 |
| `swe-fix-r0062-08` | 7 | `92a23de3c969657c…` | oauthlib__oauthlib.1fd52536.func_basic__m6knx949 |

</details>