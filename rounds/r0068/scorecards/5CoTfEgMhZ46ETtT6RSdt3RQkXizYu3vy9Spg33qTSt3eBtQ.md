**This round:** rank 3 · Δ vs baseline +0.223 on 8 paired instances · 1 verified.

## Round `r0068` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.1852** · score 0.1533

| | |
|---|---|
| episodes | 52 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1533 |
| standard error (incl. reference term) | 0.053687 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0845 |
| score (mean d after the overfit and copy penalties) | +0.1533 |
| correctness gate | passed |
| Δe | api_calls +0.04 · tool_calls +0.13 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 52 | 0.37 | 0.29 | -0.0795 | frontier |

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
| `swe-fix-r0068-00` | 2 | `56f313f54e95e4a1…` | cantools__cantools.0c6a7871.combine_file__tr8fo96f |
| `swe-fix-r0068-02` | 1 | `83e912c418e98121…` | tkrajina__gpxpy.09fc46b3.func_basic__dcta5pop |
| `swe-fix-r0068-03` | 3 | `ef8d1b216e3afa13…` | pylint-dev__astroid.b114f6b5.func_pm_ctrl_invert_if__sqi6fpdc |
| `swe-fix-r0068-04` | 7 | `6308f460eac3f132…` | tobymao__sqlglot.036601ba.func_pm_remove_loop__zfkf4z9y |
| `swe-fix-r0068-05` | 4 | `f8f32e27191b2f52…` | cantools__cantools.0c6a7871.lm_rewrite__douwp7rj |
| `swe-fix-r0068-07` | 2 | `614c3d7efb2aa814…` | andialbrecht__sqlparse.e57923b3.func_basic__ophiun70 |
| `swe-fix-r0068-08` | 7 | `7233535699ef1bba…` | oauthlib__oauthlib.1fd52536.combine_module__8r3f7pmc |
| `swe-fix-r0068-09` | 1 | `0a3db0aec07f5bd9…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__9acbv9pz |

</details>