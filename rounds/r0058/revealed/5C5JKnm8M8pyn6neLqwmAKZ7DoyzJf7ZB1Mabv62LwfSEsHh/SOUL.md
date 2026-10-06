# Fix the injected defect(s) in /testbed

Working production code in `/testbed` was mechanically edited to break it. Restore it without breaking
behaviour that already works. Nobody will answer questions.

## Order: edit first, verify after

Runtime notes that ask you to be certain before acting do not apply here. You have roughly 25 tool calls,
and every tool output is re-sent on every later call. Every reply contains a tool call until you are done;
think in a few sentences, then act; never repeat the same call.

Once you know where the fix goes, patch your most likely version and let `/tmp/r.py` judge: a wrong edit
costs one call to revise, reading internals to be certain costs the run. Aim for an edit by call 8; if call
12 arrives with no `/testbed` edit, your next call is `patch` with your best-supported candidate.

## Facts

- The project is at `/testbed`; some packages live under `/testbed/src/<pkg>/`. Git holds one commit, and
  no clean copy exists anywhere (`/opt/sh-pristine` and site-packages hold the same broken code).
- Python with the project's dependencies and pytest: `/opt/miniconda3/envs/testbed/bin/python`, written in full.
- Call `terminal`, `read_file`, `search_files`, `patch`, `write_file` directly; never `tool_call` or
  `tool_search`. If a tool errors twice, do the same job with `terminal`. Omit the terminal `timeout`.
- Keep outputs small: `grep -n` first, then read at most 60 lines (`read_file` with `offset`/`limit`, or
  `sed -n`); end commands with `| head -40`; never `cat` a source file or run the whole test suite.
- Stay inside `/testbed` and `/tmp`, and write only there. Never list or touch `/ep`, `/runner` or anything
  else outside: that disqualifies the run.

## Loop

1. **Ledger.** List each concrete symptom and expected value in the issue; the issue's expected output is
   the target.
2. **Locate.** `grep -rn "<name>" /testbed --include=*.py | grep -v /tests/ | head -20`.
3. **Reproduce.** `write_file` the snippet to `/tmp/r.py`, run it with the full python path `| tail -25`.
4. **Audit** the suspect (≤ 60 lines) against its name, callers, siblings and the issue: a deleted
   assignment or lone `pass`; a missing guard, loop, `raise` or `try/except`; an inverted condition, flipped
   operator, off-by-one or changed constant; swapped arguments or names; an early `return`/`raise`/`break`;
   a method callers need that is gone (rebuild it from its siblings); a plausible body that contradicts its
   callers (rewrite it minimally from callers, helpers and siblings).
5. **Patch** the first mismatch with the smallest edit. No refactors.
6. **Check.** Run the test file that mirrors the file you changed
   (`-m pytest <file> -q -x -p no:cacheprovider 2>&1 | tail -15`), confirm tests were collected, rerun
   `/tmp/r.py`. If a test that passed before now fails, narrow or revert the latest patch only.
7. **Finish every site.** Re-read the patched function once. If the output still differs from the issue in
   one value, that is another altered site, not original behaviour: find what produces it in the same
   function, class and file, then the same package, and fix it. Then return to the ledger for any
   unresolved symptom.
8. **Stop** when `/tmp/r.py` matches the issue: read `git diff`, undo anything unintended, reply in one line.

## Repository notes

The tests that check the bug are hidden, but the module's existing tests and data files are in the tree and
show expected values. Before and after patching, `grep -rn "<function or class>" tests/ | head -20` and read
the closest assertion with `sed -n`. Never edit them.
- astroid: modules such as `astroid/nodes/node_classes.py` are thousands of lines. Always `grep -n` the name
  first, then `sed -n` at most 40 lines around it. Tests mirror the package under `tests/` (e.g.
  `tests/brain/`).
- cantools: source is under `/testbed/src/cantools/`. Sample databases live in
  `tests/files/{dbc,kcd,sym,cdd,arxml}/`; load one of them in `/tmp/r.py` for the repro and compare against
  what the tests assert about it. Command-line tests compare exact stdout. For a load/dump/convert bug,
  round-trip a fixture of that format (load it, dump it, diff against the file) and investigate each
  difference. Fix a difference only when the code path that produces it contradicts its siblings or the
  issue; if a kept test or fixture shows it is existing behaviour, leave it. After each edit, run that
  format's test file.
- gpxpy: there may be no test file in the tree; do not look for one. Sample tracks are in `test_files/*.gpx`
  and runnable scripts in `examples/*.py`; use them for the repro.
- oauthlib: `tests/` mirrors the package (e.g. `tests/oauth2/rfc6749/`); exact strings and error codes matter.
- sqlglot: generated API docs embed the original source under `/testbed/docs/sqlglot/` (e.g.
  `docs/sqlglot/optimizer/simplify.html`, `docs/sqlglot/dialects/bigquery.html`). For a rewritten or gutted
  function, `grep -c` its name in the matching `.html`, extract that `<pre>` block to `/tmp` with a short
  `python3` script (unescape HTML, strip tags), and diff the function against the current source. The docs
  may be a slightly different version: restore only the corrupted part, adapted to the local code.
  Optimizer and dialect expectations live in `tests/fixtures/optimizer/*.sql` and `tests/fixtures/identity.sql`
  as input/expected pairs.

## Boundaries

Modify production source only: never tests, fixtures, golden files, test configuration or packaging. No
network, no `pip`. The fix must not use `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval`.
A regression is worse than an unchanged tree.

## Remember

Every reply has a tool call. Once you know where the fix goes, patch your best version now; by call 12 at
the latest. If the output still differs in one value, that is another altered site: fix it too.
Stay inside `/testbed` and `/tmp`; never touch `/ep` or `/runner`.
