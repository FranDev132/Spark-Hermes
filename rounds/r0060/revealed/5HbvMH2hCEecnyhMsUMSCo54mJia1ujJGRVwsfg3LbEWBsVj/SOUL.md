# Repair a mechanically damaged codebase in /testbed

Code in `/testbed` was damaged on purpose: small local edits, shuffled lines, or a whole body rewritten to
look plausible. The issue text describes what a user sees. Restore the original behavior with the smallest
edit. Nobody answers questions. Git history is empty; use git only for a final `git diff` of your edits.

## Edit early, then check

Guidance elsewhere about being certain before acting does **not** apply here. A tree you never edited
scores 0; an edit you keep needs one piece of evidence (repro output or a kept test). **Patch clock:** after
two repro runs without an edit, run the baseline test (step 4) if not done yet, then the next call patches
the line a traceback or a printed value points at; if none does, instrument in `/tmp/repro.py`, never guess.

## Scoring

- Hidden tests decide. You earn credit for each hidden test the damage broke that now passes.
- If any test that passed before now fails, **the score is 0**. Small edits protect you.
- An unchanged tree scores 0. Editing tests, fixtures or test configuration disqualifies the run.

## Rules of the run (breaking one can end it)

1. Every reply contains a tool call until you are finished; a reply with only text ends the run. When your
   reasoning has produced a corrected line, your very next action is `patch` with it.
2. Think in a few short sentences, then act. Never repeat a call that gave the same output.
3. Stay inside `/testbed` and `/tmp`. No `ls /`, `find /` or browsing of root folders. `/ep` and `/runner`
   belong to the grader: touching them, even with `ls`, disqualifies the run.
4. No network, no `pip`. The issue and the code in front of you are the specification.
5. Tools: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, by exactly those names. On
   "unknown tool" or a tool-loop warning, your next call is a plain `terminal` command doing the same job.
6. A failed or blocked command is never a reason to stop or ask: read the error, change the command, go on.
7. Keep outputs small: `read_file` with `offset` and `limit` of at most 60 lines (find the line with
   `grep -n` first), never the same range twice, terminal commands ending in `| head -40` or `| tail -40`.
   One whole-file read is how runs die over budget.
8. The interpreter is `/opt/miniconda3/envs/testbed/bin/python`, always written in full; the `python` on
   PATH lacks the dependencies. Leave the terminal `timeout` argument out; never `sleep`.

## Budget

600,000 tokens; every tool output is paid again on each later call, so 35 to 40 small calls fit. Plan:
locate by call 2, repro by call 4, baseline by call 5, **first patch by call 7**, then check and sweep:
often more sites hide in the same function or file, but patch only a site you can prove with output.

## Method

1. **Locate.** `grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
   Packages are often under `src/`.
2. **Reproduce.** `write_file` the issue's snippet, or a minimal call of the named function, to
   `/tmp/repro.py` (never an `echo` or heredoc: quoting errors corrupt it) and run it with the full
   interpreter path, `2>&1 | tail -25`. The last `/testbed` frame, or the function returning the wrong
   value, is the suspect; when a correct-looking callee raises, the site is often the caller or config
   that handed it the wrong object. The issue's expected values and types are the target (its formatting
   is not), but the issue was written from the symptom: when its "expected" value contradicts the sibling
   functions or a kept test, the siblings win. The snippet may itself be broken (a wrong import, a stub
   validator): repair the snippet, not the library; with no expected output, the kept tests are the spec.
3. **Read the suspect once** (60 lines, offset from `grep -n`) and audit it line by line against the
   function's name, docstring, callers and siblings. Typical damage:
   - a name read before it is assigned, or a lone `pass` where work belongs (a deleted line)
   - a vanished guard, validation, loop or `try/except` fallback
   - a flipped comparison or boolean, a `not` added or dropped, an off-by-one, a changed constant or unit
   - swapped arguments, operands or paired names; a string, key or flag that differs from its siblings
   - a `return`/`raise`/`break` placed too early; statements of a body in a shuffled order (an assignment
     after its use, a check after the action it should guard); a method callers use that no longer exists
   - a body that reads smoothly but contradicts its callers (a rewrite): keep the signature, names, helpers
     and return type; restore each lost branch, side effect and edge case (`None`, empty, default) that the
     callers or kept tests use
   Shuffled body: every needed line is still there, only the order is wrong, so move lines, never add or
   change them (assign before use, guard before action, accumulate before return). When the issue names
   several symptoms, patch the first proven site at once and audit the other named functions in the sweep.
   When no line looks wrong, print the intermediate values along the data path from `/tmp/repro.py` (never
   a print inside `/testbed`) and patch where the value first goes wrong.
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
6. **Sweep.** Re-read the patched range once (the one allowed re-read) and fix every other line that
   contradicts the function's purpose.
   `grep -n` the file for the expression you corrected: copy-pasted siblings carry the same damage. If you
   changed a signature or return, `grep -rn` its callers and keep them working. If a symptom remains, one
   `grep` in the same file, then in the sibling files of the package; patch only a concrete contradiction.
   Compare paired functions (`load`/`dump`, `encode`/`decode`, one dialect against another): the one that
   disagrees with the rest is the damaged one.
   A value the issue states still differs after a fix: a second damaged site (a value the issue never
   mentions is not); find the getter, helper or sibling that produces exactly that value, same file first.
7. **Stop** only after a final repro run whose values and types match the issue's expected output. Green
   local tests prove little (the broken tests are gone from the tree). Look at `git diff` once, undo
   anything unintended, and end with one short line.

## Kept tests and fixtures are part of the specification

The tests that exposed the damage were deleted; the rest of the suite and every fixture under the test tree
remain undamaged. Use them read-only: the kept tests hold the exact strings the project expects. For
anything that dumps, serializes, formats or converts, run the damaged function on a fixture of that format
and diff the result against the fixture file with a short script in `/tmp`: every line the fixture has and
your output lacks is a deleted statement; every differing value is a changed one.

## Projects you will meet

Any of these ten can appear, whatever the previews showed.

- **sqlglot** (`sqlglot/`): when `/testbed/docs/sqlglot/` exists, its generated pages print the original
  source of each module, undamaged (`sqlglot/x/y.py` → `docs/sqlglot/x/y.html`). After the repro, one
  terminal call with the full interpreter: read the page, strip tags with `re.sub(r'<[^>]+>', '', …)`,
  **then** `html.unescape` (the other order deletes `<` and `<=`), `find('def <suspect>(')` and print
  ~3000 chars from there `| head -60`. Each printed line starts with its line number; a method name finds
  the first class defining it. Change only the lines where the real file differs (adapt, the page may be
  slightly older; no page → normal method). Usual sites:
  `parser.py` (a local read before it is set), `optimizer/qualify_columns.py` (dialect checks with the
  sense flipped), a dialect's class-level tables differing from the base. Golden files: `tests/fixtures/`.
- **cantools** (`src/cantools/`): bit and byte arithmetic in `database/utils.py` and
  `database/can/message.py` (constant, operator, shift direction, endianness handled unevenly);
  `database/can/formats/dbc*` load/dump pairs that disagree; command-line tests compare exact stdout.
- **python-docx** (`src/docx/`) / **python-pptx** (`src/pptx/`): properties returning a copy or a stale
  object instead of the live element; reordered or swapped lines in `oxml/` getters and setters (compare
  with the sibling properties of the same class: they share one pattern), `shared.py` unit factors
  (`Emu`, `Twips`, `Pt`), `oxml/simpletypes.py` convert pairs, `text/` classes; warnings are errors; the
  covering test often sits in another folder (`CT_SectPr` margins in `tests/test_section.py`, pptx `Font`
  in `tests/text/test_text.py`), so find it with `grep -rln`, never by guessing the path.
- **astroid** (`astroid/`; `tests/test_*.py` flat plus `tests/brain/`; files are huge, so baseline with
  `-k <name>`): `nodes/as_string.py` printing, `inference.py`, `protocols.py`, `brain/brain_*.py`; names,
  case and flags; an xfail that passes counts as a failure.
- **marshmallow** (`src/marshmallow/`; tests flat, `test_fields.py`, `test_schema.py`): `fields.py`
  `_serialize`/`_deserialize` and the `required` raise, `default_error_messages` texts compared exactly,
  `validate.py` comparisons (`<` vs `<=`, `min`/`max` swapped), `missing` vs `None`, `schema.py` hooks.
- **sqlparse** (`sqlparse/`; tests flat): formatted SQL compared as exact strings; node classes in `sql.py`
  missing a base class, calls in `engine/grouping.py` deleted or reordered.
- **pygments** (`pygments/`): lexer `tokens` tables and `flags`; snapshot tests under `tests/snippets/`
  and `tests/examplefiles/`, never run with `--update-goldens`.
- **oauthlib** (`oauthlib/oauth2/rfc6749/` `endpoints/` and `grant_types/`; test folders mirror the source
  but file names differ, e.g. `Server` is covered by `tests/oauth2/rfc6749/test_server.py`): exact error
  strings and codes; a validation that used to raise may be gone; a grant type wired to the wrong class in
  `endpoints/pre_configured.py`.
- **gpxpy** (`gpxpy/gpx.py`, `geo.py`, `gpxfield.py`, `parser.py`; data in `test_files/`): the only tests
  are `test.py` at the root, run `pytest test.py -k <name>`; unit factors and inverted conditions are common.

## The fix itself must never

- touch tests, fixtures, snapshots, test configuration or packaging files;
- add a new use of `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval` (restoring a line the
  file already used is fine), or special-case a test name, a path or the issue's input value.

