# Repair a mechanically damaged codebase in /testbed

Working code in `/testbed` was damaged on purpose: one or more small local edits, sometimes a whole function
body rewritten to look plausible. The issue text describes what a user sees. Find the damaged lines and
restore the original behavior with the smallest possible edit. Nobody answers questions. Git holds a single
commit, so history reveals nothing; use git only for a final `git diff` of your own edits.

## For this task, act first and confirm afterwards

Guidance elsewhere about gathering prerequisites or being certain before changing something does **not**
apply here: edit early, then check. A tree you never edited scores 0; an edit you keep needs one piece of
evidence (repro output or a kept test). **Patch clock:** once the repro has run twice with no edit, your
next call patches the line a traceback or a printed value points at; if none does, instrument, never guess.

## Scoring

- Hidden tests decide. You earn credit for each hidden test the damage broke that now passes.
- If any test that passed before now fails, **the score is 0**. Small edits protect you.
- An unchanged tree scores 0. Editing tests, fixtures or test configuration disqualifies the run.

## Rules of the run (breaking one can end it)

1. Every reply contains a tool call until you are finished. A reply with only text ends the run. When your
   reasoning has produced a corrected line, your very next action is `patch` with it.
2. Think in a few short sentences, then act. A long reasoning turn gets cut off.
3. Never repeat a call: two identical outputs in a row means change the command.
4. Stay inside `/testbed` and `/tmp`. No `ls /`, `find /` or browsing of root folders. `/ep` and `/runner`
   belong to the grader: touching them, even with `ls`, disqualifies the run. `/opt/sh-pristine` is a copy
   of the same damaged tree, so comparing against it finds nothing.
5. No network, no `pip`. The issue and the code in front of you are the specification.
6. Tools: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, by exactly those names. On
   "unknown tool" or a tool-loop warning, your next call is a plain `terminal` command doing the same job.
7. A failed or blocked command is never a reason to stop or ask: read the error, change the command, go on.
8. Keep outputs small: `read_file` with `offset` and `limit` of at most 60 lines (find the line with
   `grep -n` first), never the same range twice, terminal commands ending in `| head -40` or `| tail -40`.
   One whole-file read is how runs die over budget.
9. The interpreter is `/opt/miniconda3/envs/testbed/bin/python`, always written in full; the `python` on
   PATH lacks the dependencies. Leave the terminal `timeout` argument out, never `sleep`, never start a
   process that does not exit on its own.

## Budget

600,000 tokens; every tool output is paid again on each later call, so 35 to 40 small calls fit. Plan:
locate by call 2, repro by call 4, **first patch by call 7**, then check and sweep. The first fix is rarely
the whole job: these bugs usually have two or three sites in the same function or file, so spend the
remaining calls on the sweep, not on a report.

## Method

1. **Locate.** `grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
   Packages are often under `src/`. One search per symbol; if it misses, widen the pattern once.
2. **Reproduce.** `write_file` the issue's snippet, or a minimal call of the named function, to
   `/tmp/repro.py` (never an `echo` or heredoc: quoting errors corrupt it) and run it with the full
   interpreter path, `2>&1 | tail -25`. The last `/testbed` frame, or the function returning the wrong
   value, is the suspect; when a correct-looking callee raises, the site is often the caller or config
   that handed it the wrong object. The issue's expected values and types are the target (its formatting
   is not); a clean exit proves nothing. The issue's snippet may itself be broken (a wrong import, a stub
   validator): repair the snippet, not the library, and when the issue gives no expected output, the kept
   tests are the specification. A missing module is not your problem: import the package from `/testbed`.
3. **Read the suspect once** (60 lines, offset from `grep -n`) and audit it line by line against the
   function's name, docstring, callers and siblings. Typical damage:
   - a name read before it is assigned, or a lone `pass` where work belongs (a deleted line)
   - a vanished guard, validation, loop or `try/except` fallback
   - a flipped comparison or boolean, a `not` added or dropped, an off-by-one, a changed constant or unit
   - swapped arguments, operands or paired names; a string, key or flag that differs from its siblings
   - a `return`/`raise`/`break` placed too early; a method callers use that no longer exists
   - a body that reads smoothly but contradicts its callers: rewrite the smallest body they need
   When the issue names several symptoms, patch the first proven site at once and audit the other named
   functions in the sweep: the damage is spread over the file. When no line looks wrong, instrument: print
   the intermediate values along the data path from `/tmp/repro.py` and patch where the value first goes
   wrong.
4. **Baseline, then patch.** Before the first patch, run the kept test file covering the module once,
   without `-x`, and note which tests already fail:
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file> -q -p no:cacheprovider 2>&1 | tail -15`
   (find it with `grep -rln "<class or function>" tests/ | head`). Then patch the first mismatch, as small
   as possible: no refactor, no rename, same return types and helpers. If `patch` cannot write under
   `/testbed`, copy the file to `/tmp`, patch the copy, copy it back; never `sudo` or `chmod`. Two failed
   patches on one suspicion: undo only those two with a reverse `patch` (never `git checkout` a file that
   holds an earlier good fix) and locate again from the traceback.
5. **Check.** Rerun the repro, then the same test command. Confirm tests were collected. Any failure that
   was not in the baseline: narrow or revert the last patch, keep earlier ones that held. Never run the
   whole suite.
6. **Sweep.** Re-read the patched function once and fix every other line that contradicts its purpose.
   `grep -n` the file for the expression you corrected: copy-pasted siblings carry the same damage. If you
   changed a signature or return, `grep -rn` its callers and keep them working. If a symptom remains, one
   `grep` in the same file, then in the sibling files of the package; patch only a concrete contradiction.
   Compare paired functions (`load`/`dump`, `encode`/`decode`, one dialect against another): the one that
   disagrees with the rest is the damaged one.
7. **Stop** only after a final repro run whose output you compared with the issue's expected output line by
   line. Green local tests prove little (the broken tests are gone from the tree). Look at `git diff` once,
   undo anything unintended, remove debug prints, and end with one short line.

## When the repro is almost right

A value the issue states still differs: that is a second damaged site, not original behavior (a value the
issue never mentions is not). Find the one getter, helper or sibling that produces exactly that value, in the
same function, class and file first, then the neighbouring files, and fix it. One `grep` of the kept tests
for that name is the only check: if a kept test pins the current value, the damage is one step further back.

## Kept tests and fixtures are part of the specification

The tests that exposed the damage were deleted; the rest of the suite and every fixture under the test tree
(`tests/files/`, `tests/fixtures/`, sample documents, golden outputs) remain undamaged. Use them read-only:
the kept tests hold the exact strings the project expects. For anything that dumps, serializes, formats or
converts, load a fixture of that format, run the damaged function on it, and diff the result against the
fixture file with a short script in `/tmp`: every line the fixture has and your output lacks is a deleted
statement; every differing value is a changed one. For a command-line tool, compare the command's output on
a fixture with the command-line test's expected text.

## Projects you will meet

- **sqlglot** (`sqlglot/`): when `/testbed/docs/sqlglot/` exists, its generated pages print the original
  source of each module, undamaged. After the repro, turn the one relevant page into plain text in `/tmp`
  (unescape HTML, strip tags), print only the suspect function, compare with the real file and change only
  the differing lines; the page may be slightly older, so adapt rather than paste; no page for that module
  means the normal method. Usual sites: `parser.py` (a local read before it is set),
  `optimizer/qualify_columns.py` (dialect checks with the sense flipped), a dialect's class-level tables
  differing from the base. Golden files live under `tests/fixtures/`.
- **cantools** (`src/cantools/`): bit and byte arithmetic in `database/utils.py` and
  `database/can/message.py` (constant, operator, shift direction, endianness handled unevenly);
  `database/can/formats/dbc*` load/dump pairs that disagree; command-line tests compare exact stdout.
- **astroid** (`astroid/`; `tests/test_*.py` flat plus `tests/brain/`, big files: select with `-k`): names,
  case and flags in inference and printing; an xfail that passes counts as a failure.
- **oauthlib** (`oauthlib/oauth2/rfc6749/` `endpoints/` and `grant_types/`; test folders mirror the source
  but file names differ, e.g. `Server` is covered by `tests/oauth2/rfc6749/test_server.py`): exact error
  strings and codes; a validation that used to raise may be gone; a grant type wired to the wrong class in
  `endpoints/pre_configured.py`.
- **gpxpy** (`gpxpy/gpx.py`, `geo.py`, `gpxfield.py`, `parser.py`; data in `test_files/`): the only tests
  are `test.py` at the root, run `pytest test.py -k <name>`; unit factors and inverted conditions are common.

## The fix itself must never

- touch tests, fixtures, snapshots, test configuration or packaging files (`pyproject.toml`, `setup.cfg`,
  `tox.ini`, `.coveragerc`);
- add a new use of `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval` (restoring a line the
  file already used is fine), or special-case a test name, a path or the issue's input value;
- fill the disk or run endless loops.

Revision v11 (e1).
