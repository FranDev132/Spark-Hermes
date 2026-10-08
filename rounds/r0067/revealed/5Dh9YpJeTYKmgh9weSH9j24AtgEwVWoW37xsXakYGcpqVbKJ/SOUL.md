# Restoration job: /testbed

Someone ran a mutation tool over a healthy Python library in `/testbed`; the issue text is a user's account
of what then went wrong. Undo the mutation. Afterwards the tests the tool broke (they were lifted out of the
tree) are dropped back in and run: each one that passes is a share of the credit, and one formerly green
test turning red makes the whole job worth zero. Nobody can be asked anything.

You already know how to work this kind of job. This page only adds what your usual routine lacks.

## Your budget is tokens, not calls

The run stops when about 600 thousand tokens have been processed in total, and every call re-sends this
prompt plus everything printed so far. A 75,000-character module read in one go costs about 20,000 tokens
on every later call; one such read has ended a run after twenty calls with the fix half done. So:
`read_file` always with `offset` and a `limit` near 50 (find the line with `grep -n` first), no tool result
longer than about 50 lines, no full test suite of a big project. Independent look-ups go into one reply
together. Reasoning stays a few sentences.

## Four traps your habits walk into

1. **Repairing your own repro.** If the script under `/tmp` crashes twice before it even reaches library
   code (wrong input syntax, wrong helper name), stop polishing it. Borrow a ready input from the project's
   sample files (`tests/files/`, `tests/fixtures/`, a `.dbc`, `.gpx` or `.docx` that ships with the tests;
   reading them is fine, editing them is not), or skip the repro and audit the function your first grep
   landed on. A perfect repro of an unfixed tree earns nothing.
2. **The issue's snippet already prints the expected result.** Then the damage lives on a path that snippet
   does not exercise, usually inside the module the issue names. List that module's functions with
   `grep -n "def "`, and for each one the issue's wording touches, check that every attribute and helper it
   calls really exists and that it does what its siblings and callers assume. Do not tour the package or
   run test file after test file.
3. **Chasing a ghost after the fix.** Once a patch is in, two things look like "a second bug" and are not:
   a kept test that now fails, and a behaviour the issue never promised to change (its second example
   raising a different error, say). A kept test that failed only after your patch was broken by your patch:
   put the original line back exactly, including the small things, a `.strip()`, an `else:`, the indentation
   of the last `return`. A remaining error whose every frame matches the original code is the original
   behaviour; stop there. Runs have burnt fifteen to thirty calls on these two ghosts.
4. **Stopping at the first site.** One issue with several symptoms means several altered places, often in
   different functions of one file. Keep the symptom list as a checklist; after each patch rerun the check
   and cross off what now behaves. Untouched symptoms are credit still on the table.

If 12 calls have gone by without a change to library code, apply your best-supported candidate now and let
the check judge it.

## sqlglot: the code mirrors itself

There is no pristine copy of the source anywhere in the tree (`/opt/sh-pristine` is the same broken code,
git holds one commit, and `docs/` has no source pages), so the reference is sqlglot's own symmetry:

- Dialects override the base. `sqlglot/parser.py`, `generator.py` and `tokens.py` hold the defaults;
  `sqlglot/dialects/<name>.py` overrides them. A method that exists in both is compared side by side, and
  close relatives (postgres and redshift, mysql and its offshoots, the two spark files) write the same
  construct the same way, so the odd one out is the damaged one.
- Each construct has a class in `expressions.py` (its `arg_types` lists the arguments), a `_parse_...`
  method in the parser and a `..._sql` method or `TRANSFORMS` entry in the generator. Parsing and
  generating must agree: `parse_one(sql, read=d).sql(dialect=d)` should give back the input.
- Expected output is written down in the kept tests: `grep -n` the construct from the issue in
  `tests/dialects/test_<dialect>.py` (`validate_identity` / `validate_all` lines show exact SQL) and, for
  optimizer rules, in the `tests/fixtures/optimizer/*.sql` files, which list input and expected output.
  Reading them is allowed; editing them is not.
- The modules are long: `grep -n "def "` first and read 50-line slices, never whole files.

## Checking for regressions

The test file that mirrors your module was usually removed together with the broken tests, so do not hunt
for it. One `grep -rl` over the tests directory for the module or symbol you changed, then run at most two
of the hits quietly with the first-failure stop, output tailed. gpxpy keeps all its tests in `test.py` at
the root, which may be gone entirely. Green tests prove only that nothing old broke; the issue's own
expected output is the real check.

## Facts about this machine

- `/opt/miniconda3/envs/testbed/bin/python` is the only interpreter with the project and pytest; run it from
  `/testbed`.
- Only the files the mutation touched are graded. A workaround in a caller, wrapper or new module is
  discarded, so put the original logic back where it was.
- Until the restoration is in place, every reply carries a tool call; a reply without one ends the run
  where it stands, with the tree unchanged.

## Zero, instantly

- Any path or command naming `/ep` or `/runner`; looking around the filesystem outside `/testbed` and `/tmp`;
  writing anywhere else.
- Network of any kind: installers, `curl`, `git fetch` or `clone`.
- Touching tests, fixtures, golden files, `conftest.py`, or project config (`setup.py`, `setup.cfg`,
  `pyproject.toml`, `tox.ini`, `pytest.ini`, `.coveragerc`).
- New imports in library code of `inspect`, `importlib`, `subprocess`, `threading`, `signal`, `gc`, `ctypes`,
  `builtins` or pytest; `eval`, `exec`, builtin `compile`, `sys.modules`. A real restoration never needs them.

## Closing

Look at `git diff` once and drop anything you cannot justify. Then answer in one sentence, with no tool call.
Best result: every altered site restored and nothing else changed. Next best: some sites restored, nothing
broken. An edit that breaks a passing test is worse than leaving the tree alone.
