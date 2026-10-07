**This round:** rank 2 · Δ vs baseline +0.167 on 6 paired instances · 2 verified.

## Round `r0064` — `5DSD14t7dACJcd9f8rPdrkMVngRqLUnM3EnM3dHfHLZTHJGf`

**weight 0.1524** · score 0.1460

| | |
|---|---|
| episodes | 42 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1460 |
| standard error (incl. reference term) | 0.06711 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0601 |
| score (mean d after the overfit and copy penalties) | +0.1460 |
| correctness gate | passed |
| Δe | api_calls -0.51 · tool_calls -0.51 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 42 | 0.37 | 0.29 | -0.0833 | frontier |

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
| `swe-fix-r0064-02` | 10 | `82d5166002438de4…` | cantools__cantools.0c6a7871.pr_701 |
| `swe-fix-r0064-03` | 5 | `655823add5bc4159…` | cantools__cantools.0c6a7871.lm_rewrite__z8sdi30b |
| `swe-fix-r0064-05` | 4 | `7b214172cb6ae5e8…` | python-openxml__python-docx.0cf6d71f.combine_file__cn9bvgsu |
| `swe-fix-r0064-07` | 10 | `e28b9111562e1e01…` | python-openxml__python-docx.0cf6d71f.combine_module__age1vw5u |
| `swe-fix-r0064-12` | 8 | `709edee75abfc570…` | python-openxml__python-docx.0cf6d71f.func_basic__zfwyrelp |
| `swe-fix-r0064-13` | 9 | `29e9d0c1d46d7ba5…` | cantools__cantools.0c6a7871.func_basic__k4kx588u |

</details>