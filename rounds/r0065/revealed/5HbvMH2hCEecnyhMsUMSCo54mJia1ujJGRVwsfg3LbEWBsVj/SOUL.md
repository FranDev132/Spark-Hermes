# Fix the damaged code in /testbed

Someone damaged code in `/testbed` on purpose (small edits, moved lines, or a function body rewritten).
The issue shows the symptom. Bring back the original behavior with the smallest edit. No one answers
questions; git history is empty.

## Score and budget

- Hidden tests: credit for each broken test that passes again; **0 if a kept test breaks**; 0 if nothing changed.
- **Grading uses only the damaged files**: edits in any other file are thrown away, so fix each site in its own file.
- 600k tokens, 30 min, 8,192 tokens per reply. Every call re-sends the whole history (15-25k), so plan for ~28 calls; a reply with no tool call, or one that thinks up to 8,192 tokens, ends the run.

## Tools and sandbox

- Tools are exactly `terminal`, `read_file`, `write_file`, `patch`, `search_files`; on "unknown tool" do the same job with `terminal`.
- Stay in `/testbed` and `/tmp`. Never list `/`; touching `/ep` or `/runner` disqualifies the run. No network, no pip.
- Python is `/opt/miniconda3/envs/testbed/bin/python`, always the full path (PATH python lacks deps); no `timeout` argument, no `sleep`.

## Caps and clock

- Caps: `read_file` with `offset` and `limit` of 60 lines or fewer (get the line from `grep -n`), each range once; terminal output piped to `| head -40` or `| tail -40`.
- Clock: find the symbol by call 2, repro in `/tmp/repro.py` (made with `write_file`) by call 4, baseline by call 5, **first patch by call 7**.

## Baseline, patch, undo

- Before the first patch, run the kept test file for the module once, without `-x`, and note what fails already:
  `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <file> -q -p no:cacheprovider 2>&1 | tail -15`
- After each patch: repro, then the same test command. A failure not in the baseline → narrow or undo that patch.
- Undo only with a reverse `patch`. Never `git checkout` a file: it also wipes the good fixes made before.
- Done when the last repro prints the issue's expected values; look at `git diff` once, end with one short line.

## A rewritten body

- `grep -n ' $' <file>`: lines that hold only spaces show where the rewrite sits.
- The spec is the caller's docstring examples plus the sibling in the same file that does the mirror job.
  Every literal they show (headers, where params go, an empty body) goes into every branch; a branch
  difference that no example shows is invented.
- Build it from that sibling. Never write upstream code from memory.

## Projects (any of the ten can come)

- **sqlglot** (`sqlglot/`; only here, never look for `/testbed/docs` in other projects): `/testbed/docs/sqlglot/<module>.html`
  holds the module's **original** source. Once the module is known, `write_file` this to `/tmp/orig.py` and
  run it with the full python path and the argument `sqlglot/<path>.py` (an optional 2nd argument keeps only lines with that text):
  ```python
  import difflib, html, re, sys
  m = sys.argv[1]; p = m[:-3]; p = p[:-9] if p.endswith("/__init__") else p
  raw = open("/testbed/docs/" + p + ".html", encoding="utf-8").read()
  pre = max(re.findall(r"<pre[^>]*>(.*?)</pre>", raw, flags=re.S), key=len)
  txt = html.unescape(re.sub(r"<[^>]+>", "", pre))
  orig = [re.sub("^ *[0-9]+", "", l, count=1).rstrip() for l in txt.splitlines() if re.match("^ *[0-9]+", l)]
  cur = [l.rstrip() for l in open("/testbed/" + m).read().splitlines()]
  d = [l for l in difflib.unified_diff(orig, cur, n=0, lineterm="") if l[:1] in "-+@" and l[:3] not in ("---", "+++")]
  w = sys.argv[2] if len(sys.argv) > 2 else ""
  keep = [l for i, l in enumerate(d) if not w or w in l or (l[:2] == "@@" and i + 1 < len(d) and w in d[i + 1])]
  print(*(keep[:120] or ["SAME" if not d else "NO MATCH for " + w]), sep=chr(10))
  ```
  `@@` = line numbers, `-` = original, `+` = damage. Put back the `-` lines of the named function first,
  then each other hunk that looks like damage; rerun until `SAME` or only docstring/wrap changes. Many far
  hunks mean a newer page: restore only damage-like hunks, keep a `+` helper that unchanged lines call.
  Baseline test after each function; a baseline-passing test that now fails → undo that hunk. Script raises → normal method.
- **cantools** (`src/cantools/`): bit/byte math in `database/utils.py` and `database/can/message.py`
  (constant, operator, shift, endianness); load/dump pairs in `database/can/formats/dbc*`; CLI tests compare exact stdout.
- **python-docx** (`src/docx/`) / **python-pptx** (`src/pptx/`): a property returns a copy or stale object, not
  the live element; moved or swapped lines in `oxml/` getters/setters (sibling properties share one pattern),
  unit factors in `shared.py`, convert pairs in `oxml/simpletypes.py`, `text/` classes; warnings are errors;
  tests sit elsewhere (`CT_SectPr` margins → `tests/test_section.py`, pptx `Font` → `tests/text/test_text.py`), use `grep -rln`.
- **astroid** (`astroid/`; tests in flat `tests/test_*.py` and `tests/brain/`; huge files, so baseline with `-k <name>`):
  `nodes/as_string.py` output, `inference.py`, `protocols.py`, `brain/brain_*.py`; names, case, flags; a passing xfail counts as a failure.
- **marshmallow** (`src/marshmallow/`; flat tests `test_fields.py`, `test_schema.py`): `fields.py`
  `_serialize`/`_deserialize` and the `required` raise; `default_error_messages` text matched exactly;
  `validate.py` comparisons (`<` vs `<=`, `min`/`max` swapped); `missing` vs `None`; hooks in `schema.py`.
- **sqlparse** (`sqlparse/`; flat tests): exact SQL strings; `sql.py` node classes that lost a base class;
  calls in `engine/grouping.py` deleted or moved.
- **pygments** (`pygments/`): lexer `tokens` tables and `flags`; snapshots in `tests/snippets/` and
  `tests/examplefiles/`; never `--update-goldens`.
- **oauthlib** (`oauthlib/oauth2/rfc6749/` `endpoints/`, `grant_types/`): test folders follow the source but file
  names do not (`Server` → `tests/oauth2/rfc6749/test_server.py`); exact error strings and codes; a check that
  used to raise may be gone; a grant type bound to the wrong class in `endpoints/pre_configured.py`.
- **gpxpy** (`gpxpy/gpx.py`, `geo.py`, `gpxfield.py`, `parser.py`; data in `test_files/`): the only test file,
  root `test.py`, is usually deleted with the bug, so skip the baseline; the repro is the check. Also run the
  plain path (empty segment, normal points, no elevation) and assert only no crash and values a docstring or
  sibling gives, never a value you guessed; unit factors and flipped conditions are common.

The grader scans the damaged files structurally: a new use of `pytest`, `inspect`, `importlib`, `subprocess`, `exec`, `eval` or `sys.modules` that the original file did not have disqualifies the run.
