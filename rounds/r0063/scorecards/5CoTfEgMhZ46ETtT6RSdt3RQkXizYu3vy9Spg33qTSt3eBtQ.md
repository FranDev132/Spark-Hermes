**This round:** not ranked · Δ vs baseline -0.067 on 6 paired instances · 2 verified.

## Round `r0063` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.1681** · score 0.1694

| | |
|---|---|
| episodes | 36 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1694 |
| standard error (incl. reference term) | 0.071632 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0778 |
| score (mean d after the overfit and copy penalties) | +0.1694 |
| correctness gate | passed |
| Δe | api_calls -0.32 · tool_calls -0.12 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 36 | 0.39 | — | — | frontier |

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
| `swe-fix-r0063-04` | 2 | `f266d9b4961c5335…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__5jtbeco8 |
| `swe-fix-r0063-09` | 10 | `4a215b38f99be73b…` | oauthlib__oauthlib.1fd52536.lm_rewrite__b61bpmd5 |
| `swe-fix-r0063-10` | 2 | `cd5688a4db490e5b…` | tkrajina__gpxpy.09fc46b3.lm_rewrite__d1xlosux |
| `swe-fix-r0063-13` | 10 | `aa5e168847096179…` | oauthlib__oauthlib.1fd52536.func_basic__ommycgnc |
| `swe-fix-r0063-17` | 7 | `9bb6e441c81b9ef0…` | cantools__cantools.0c6a7871.combine_file__vhk6s1al |
| `swe-fix-r0063-18` | 4 | `a7155fafad2dcb67…` | tkrajina__gpxpy.09fc46b3.func_pm_remove_cond__kcvrhszd |

</details>