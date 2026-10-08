# Restore the injected bug in /testbed

A tool mechanically edited working code in the Python project at `/testbed` so it misbehaves. Put it back.
The tests that caught the edit were removed; the rest of the suite remains. You are scored by the share of
those removed tests that pass after your change, and the task scores **zero** if any test that passed before
now fails. No one answers questions.

## This page overrides the runtime notes that follow it

Any instruction below to gather prerequisites or become certain before acting is reversed: **act, then
verify.** An untouched tree scores zero; a wrong edit scores zero. Think in a few sentences, then call a
tool. **Every reply carries a tool call until you are done** — the moment your reasoning holds a corrected
line, your next call is `patch` with it; never write a fix into prose.

## Rules that end the run at 0 — never trigger them

- A reply with no tool call ends the run. A reply that thinks too long is cut off. Repeating a call (~5×)
  halts it — change something every call.
- **Two backstops end the run: ~600,000 tokens and 30 minutes of wall clock.** Every tool output is re-sent
  and re-paid on every later call, and slow commands burn the clock, so keep each output tiny and keep
  moving. `read_file` **always** with `offset` (from `grep -n`) and `limit` ≤ 60; never `cat` source; end
  commands that could overflow with `| head -40` / `| tail -40`; never run the whole suite.
- No network/installs; don't touch tests or config (test tree, `conftest.py`, `pytest.ini`, `tox.ini`,
  `setup.cfg`, pytest section of `pyproject.toml`, fixtures, golden files, output-regenerating flags); write
  only inside `/testbed` and `/tmp`, never list/read/run anything elsewhere (not even `ls` of `/`, `/ep`,
  `/runner`) — reaching outside zeroes the run. The fix itself uses no `pytest`/`_pytest`, `inspect`,
  `importlib`, `subprocess`, `exec`, `eval`.

## Machine facts — already checked

- Project at `/testbed` (no `/workspace`/`/repo`; one commit — `git` only for a final `git diff` /
  `git checkout -- <file>`). `/opt/sh-pristine` is the **same broken code** — useless to diff.
- The interpreter with deps + pytest is **`/opt/miniconda3/envs/testbed/bin/python`**, written in full; the
  `python` on PATH lacks deps.
- Use `terminal`, `read_file`, `write_file`, `search_files`, `patch` directly — no `bash`/`Read`/`Grep`/
  `Edit`, never `tool_call`/`tool_search`/`tool_describe`, no skills. A tool-loop/"not deferrable" warning →
  next call is plain `terminal`. A tool error → fix args once, then `terminal`. If `patch` can't write,
  once: `cp <f> /tmp/w.py && patch /tmp/w.py && cp /tmp/w.py <f>`; never `sudo`/`chmod`. Omit `terminal`'s
  `timeout` (seconds; a big value backgrounds the command); never `sleep`.

## The loop

1. **Locate (call 1):** `grep -rn "<name from issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
   One search per symbol; a miss → one `grep -rn` in `terminal`, never a second `search_files`. The issue is
   a symptom report, not a diagnosis: trust the runtime failure, then caller/callee data flow, then
   siblings; the prose last.
2. **Reproduce (calls 2–3):** `write_file` the issue's snippet or a minimal call into `/tmp/r.py` (never an
   `echo` heredoc), then `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -25`.
   The last `/testbed` frame — or the wrong return value — is the suspect. **The issue's shown output/value
   is the spec: make the code reproduce it character for character** (spaces, brackets, separators, quotes,
   case); a clean exit is not proof. **Cover every case the issue names, not just the snippet:** if it
   mentions variants (e.g. `many=True` and single, empty/`None`, both endianness), put each in the repro and
   make the fix satisfy all of them — the hidden tests check the variants too, so a fix that only passes the
   one case you tried scores zero on them. For an error/exception bug, match the exact exception **type and
   message** the issue shows, not just "it raises".
3. **Read the suspect once (call 4):** `read_file` at the `grep -n` offset, `limit` ≤ 60.
4. **Decide the bug's shape, then act on it:**
   - **A small mechanical edit** — scan each line against its name, docstring, neighbours, callers (the
     docstring may be edited too) for: a name used before assignment or a lone `pass` (deleted line — write
     it back); a vanished guard/loop/`try-except` (input once rejected now processed, a raw error where a
     fallback belonged, one item handled where all should be — restore it); a flipped operator/comparison, a
     `not` added/dropped, a broken comparison chain, an off-by-one, a wrong constant/unit/shift, a toggled
     default; swapped operands/arguments or reversed paired names; a `return`/`raise`/`break` making lines
     unreachable or control reordered so a value is used before it is set; an inverted `if`; a method/
     property/base that no longer exists (rebuild from siblings). **Patch the first mismatch in your very
     next call,** then rerun the repro.
   - A comment or name saying *simulate*, *without actually*, *placeholder*, *for now*, or *dummy* marks a
     faked body — rebuild what its name and callers require.
   - **A deleted block or a rewritten/`combine_*` function** (the body reads plausibly but is wrong, or a
     whole handling branch is gone) — this is the hard bug the strategy-less baseline fails, so it is where
     the credit is won: **do not guess-patch.** Spend the calls to understand the data model, the callers,
     and the sibling branches (what fields/attributes the objects expose, what the callers expect back),
     then reconstruct the smallest block that satisfies them. Investigating a hard bug for a dozen calls
     beats a premature wrong patch — but keep each output small so the clock survives.
   If the repro prints a wrong value and no line looks wrong, **instrument**: print intermediate values
   along the data path and patch where the value first diverges. One value still wrong after a fix is a
   second altered site — find its producer (getter/helper/sibling); one kept-test grep says if it is pinned.
5. **Patch clock:** repro ran twice with no edit on a mechanical bug → next call patches your best
   candidate. Two patches on one hunch both fail → wrong location: revert both, re-localize from the
   traceback.
6. **Sweep — always, even once the repro is green.** These bugs come several at a time, usually in the
   **same file** you patched, and the hidden tests fail on the site you did not touch while your repro passes.
   Before finishing, re-read the patched function to its end and its nearest siblings once (`limit` ≤ 60 each)
   and patch any of: a value computed but never used afterwards (its assignment/merge was deleted — e.g. a
   list built and then dropped); an `except`/guard/tuple narrower than its siblings or than the cases the
   issue names; a constant, operator or argument order that differs from the sibling doing the same job. For
   each symptom still wrong, also `grep -rn "<name>" <pkg dir> | head -20` across the package, audit, patch.
   One pass per symbol/file; the issue's symptom list is the whole work list.
7. **Check — a regression zeroes everything, so guard it:** make the **smallest** edit that fixes the
   issue. After patching, run the changed module's kept tests, then the repro:
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file> -q -x -p no:cacheprovider
   2>&1 | tail -12`. Confirm it **collected** tests ("no tests ran" proves nothing). If your edit touches a
   function imported by other modules, run that neighbouring test file too — a previously-passing test that
   now fails means your edit is wrong: narrow it or `git checkout -- <file>`. Green kept tests never license
   output differing from the issue's shown output (the graded tests are hidden), and never substitute a
   remembered/"upstream" format for the one shown.
8. **Finish:** run the repro once more vs the issue's expected output; read `git diff`, undo anything
   unintended, delete debug prints, stop with one line.

## sqlglot only — a clean reference is in the tree

`/testbed/docs/sqlglot/` holds generated pages printing each module's **pristine** source with line numbers,
untouched by the bug (`sqlglot/optimizer/simplify.py` ↔ `docs/sqlglot/optimizer/simplify.html`). After the
repro, strip the one relevant page to text in `/tmp`, print the suspect function (≤ 60 lines), and change
exactly the differing lines. Adapt, don't paste; if missing, use the normal loop.

## Repositories

| Project | Source | Tests | Watch |
|---|---|---|---|
| cantools | `src/cantools/` | `tests/` | CLI tests compare exact stdout; damage in bit/byte math (`database/utils.py`, `message.py`) and `formats/dbc.py` |
| python-docx / python-pptx | `src/docx/` · `src/pptx/` | `tests/` mirror source | warnings are errors; properties returning a stale object, swapped oxml-setter branches |
| astroid | `astroid/` | `tests/` | an xfail that passes is a failure; dropped inference guards, deleted brain/helper branches |
| sqlglot | `sqlglot/` | `tests/`, `tests/dialects/` | `tests/fixtures/` golden; `parser.py` locals used before set, flipped dialect checks, dialect tables off from base |
| sqlparse | `sqlparse/` | `tests/` flat | exact SQL strings; `sql.py` classes missing a base, reordered `engine/grouping.py` calls |
| oauthlib / marshmallow | `oauthlib/` · `src/marshmallow/` | `tests/` | exact strings/error codes; dropped validation guards |
| pygments | `pygments/` | `tests/` | snapshot tests; never regenerate |
| gpxpy | `gpxpy/` | `test.py` at root | one big file — select with `-k` |

## Order of preference

Every injected site fixed, nothing else broken → some sites fixed, nothing else broken → the tree exactly as
found. A regression is worth less than nothing changed.
