# Restore the damaged Python project in /testbed

A bug injector damaged the source of a working Python project in `/testbed`. Undo it. The tests that caught the
damage were deleted; every test still in the tree passes now. You are paid per deleted test that passes again,
and nothing if a test that passes now fails afterwards. Nobody will answer questions.

## Read this before the generic notes below

They favour caution; here that loses. Every earlier output is re-sent with each call, so a run has about 30 calls.
Runs that end with no edit earn zero, and most had already seen the damaged lines. **Form a hypothesis fast, patch
it, then let a reproduction judge.**

Never end a run by accident:
1. Every reply makes a tool call until you are finished. A corrected line in your reasoning goes into `patch` next.
2. Think in at most ten short lines per reply. Never reconstruct "the upstream project" from memory.
3. A call that fails twice means change approach; repeating it halts the run.
4. The issue may name a test file or test function. It was deleted and exists nowhere: never look for it or run it.
   Put what it would check into `/tmp/r.py`.

## Tools and machine

- Call `terminal`, `patch`, `write_file` (and `search_files`) directly by those names. **Never call `read_file`:**
  without a `limit` it dumps a whole file — tens of thousands of characters re-sent on every later call, which
  sinks the run. Read code only as `cd /testbed && sed -n '120,160p' <file>` (40 lines at most), with the line
  numbers from `grep -n` first; copy `patch` text from that output exactly. Never `tool_call`,
  `tool_search` or a wrapper; never invent `bash`, `execute_command`, `read`. If a tool errors twice, use `terminal`.
- Work only in `/testbed` (fix) and `/tmp` (scratch). Never look at `/ep`, `/runner`, `/opt` or anywhere else, not
  even with `ls`: it can disqualify the run, and no clean copy of the project exists.
- Python: `/opt/miniconda3/envs/testbed/bin/python`, written in full. The PATH `python` lacks pytest and deps.
- No `timeout` argument, no `sleep`; commands over a minute are lost to the background. Select tests with `-k` or
  `file::test`. Git has one commit: use it only for `git diff` at the end.
- Keep outputs small — they are what the budget pays for: every `terminal` output piped to `| head -n 25` or
  `| tail -n 25` (a `sed -n` range is already bounded); never `cat` a source file, never the whole test suite.

## How the damage was made

- Subtle edits in one function, often two or three: flipped comparison or boolean, `and`/`or`, off-by-one, changed
  constant, default or string, swapped arguments or variables, wrong attribute or key.
- A body regenerated from its signature and docstring: reads cleanly, behaves differently. The docstring, signature,
  callers and siblings are original — they are the spec.
- A removed statement (assignment, `if` guard or `raise`, loop, `with`/`try`); `if`/`else` bodies exchanged;
  statements reordered; an operand dropped from `a + b + c`; a class method deleted (rebuild it like its siblings).
- **Damage in two or more functions of one file or package — about a quarter of tasks.** Each site earns its own tests.

## The loop

0. **First call — look for the injector's own notes.** It sometimes leaves a trailing comment on the line it
   damaged, saying what it did (`node=node,  # swapped self with node`, `return  # removed yielding ...`):
   `cd /testbed && grep -rnE --include=*.py '^[^#]*[^[:space:]#][^#]*#.*([Ss]wapp|[Ss]ubtle|[Bb]ug\b|[Ii]ncorrect|[Uu]nintended|[Ss]ilently|[Rr]emoved|[Cc]hanged?\b|[Ww]rong|[Ii]nstead of|[Uu]nnecessar|[Uu]nneeded)' . | grep -v -e /tests/ -e /test_ -e /docs/ | head -n 20`
   Usually it prints nothing. A hit in the code the issue is about is damage: restore what the comment says the
   original was, delete the comment, and look at the rest of that function too. Ignore hits elsewhere.
1. **Locate** (sqlglot bug: once you have the suspect function, run the `/tmp/doc.py` comparison from the sqlglot note below before reading any code): `grep -rn "<specific name>" /testbed --include=*.py | grep -v /tests/ | head -n 20`.
2. **Reproduce with asserts, not prints.** (If the issue's own snippet is broken — a wrong import, a typo — repair the snippet, never the library.) `write_file` `/tmp/r.py` that turns **every** expectation in the issue
   into an `assert` — exact values, types, strings, and every "should raise X" as
   `try: call()` / `except X: pass` / `else: raise AssertionError("expected X")`. Then run
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 15`. The first failing assert and
   the deepest `/testbed` frame point at the suspect. Never judge the output by eye: the script decides.
3. **Read the suspect once:** `grep -n "def <name>" <file>`, then `sed -n '<start>,<start+39>p' <file>`. Audit each
   statement against the list above.
3b. **Judge the shape of the damage before acting.** A small mechanical edit (a flipped operator, a swapped pair,
   a changed constant, a deleted line) is patched at once. A whole branch or block that is missing, or a body
   rewritten to read plausibly, is the hard case the bare model fails — there, do not guess: spend calls on the
   data the function receives and must return (its callers, the attributes of the objects, the sibling branches)
   and rebuild the smallest block that satisfies them. A variable the function sets but never reads
   (`previous_point = ...` with no use) marks where the deleted code used it — your rebuild must use it. Test
   absence with `is None`, never truthiness: `0`, `0.0` and `""` are real values. A rebuilt block must also keep
   the ordinary path working: add asserts to `/tmp/r.py` that plain input (nothing missing, no special case, two
   normal items in a row, an empty list) runs without error and gives the obvious result. This matters most when
   `pytest` finds no tests (gpxpy's whole `test.py` is deleted): the hidden suite then also contains every old test
   of that file, and a crash on the plain path fails all of them. If no line looks wrong, instrument: print the values along
   the data path from `/tmp/r.py` and patch where a value first goes wrong.
4. **Patch every suspect line in the next call — by call 8 at the latest.** If nothing looks wrong but behaviour is,
   rewrite the smallest body that does what docstring, signature and callers require. Rerun `/tmp/r.py`.
   If the reproduction has run twice with no edit, patch your best candidate now. If two patches on the same
   hunch both fail, revert them (`git checkout -- <file>`) and re-locate from the traceback instead of a third.
5. **Audit the whole damaged file — the issue shows only one symptom.** The tests still in the tree passed before
   you fixed anything, so a green suite says nothing about the deleted ones, and the hidden tests cover the whole
   file the injector touched, not just the function the issue names. Once the issue's symptom is fixed, read every
   other function and method of that file (40 lines at a time with `sed -n`). Anything that looks deliberately
   wrong is damage — fix it even though the issue never mentions it: a missing `raise` (an error built but not
   raised), a literal that makes no sense (`'invalid_token'`, a hard-coded `True`), a renamed key or attribute
   (`resource_owner_key_old`), arguments passed in the wrong order or by the wrong keyword, a condition with its
   sense flipped, a value initialised from itself. Deleted statements also show up against the function's
   counterpart (load vs dump, parse vs format, encode vs decode, getter vs setter). In each damaged function, check
   every parameter is actually used: a parameter the body ignores, or overwrites with `None` or a constant
   (`self.parent = None` while `parent` is a parameter), is damage — restore it (`self.parent = parent`) even if
   you "remember" the upstream line differently: your memory of the project is unreliable, this rule is not. Re-question every small literal there
   (`0`/`1`/`-1`, `None`, `True`, an index) against how siblings call the same thing; a function with one visible
   damaged line usually has two or three. Stay within the damaged file
   and its direct counterparts; never hunt through the whole repository. Before treating a value as damaged, one
   `grep` of the kept tests for its name: if a kept test pins the current value, leave it. Then:
5b. **Fixtures are a second spec.** The test tree's data files (`tests/files/`, `tests/fixtures/`, sample documents,
   golden outputs) are undamaged. For anything that dumps, serializes, formats or prints, run the function on a
   fixture of that format and diff its output against the fixture with a short script in `/tmp`: a line the fixture
   has and your output lacks is a deleted statement; a differing value is a changed one. Also `grep -n` the file for
   the expression you just corrected — copy-pasted siblings often carry the same damage.
6. **Regressions:** before your first patch, run the covering test file once (no `-x`) and note what already fails —
   afterwards only a new failure is yours. To undo one edit, apply the reverse `patch`; `git checkout -- <file>`
   would also discard your earlier good fixes in that file. for each changed file run its covering tests,
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <tests> -q -x -p no:cacheprovider 2>&1 | tail -n 8`;
   confirm tests ran. Any failure is yours: narrow or revert (`git checkout -- <file>`).
6c. **The finish gate.** Stop only when `/tmp/r.py` — covering every case the issue mentions — runs to the end with
   no AssertionError. A green test suite proves nothing here (those tests passed before your fix). If an assert still
   fails, you are not done: find what produces that value, however sure you feel.
7. **Finish:** `git diff | head -n 50`, drop debug prints and unintended changes, end with one line.

## Rules — breaking one scores zero

Edit source only: never tests, fixtures, golden or snapshot files, `conftest.py`, `pytest.ini`, `tox.ini`,
`setup.cfg`, `setup.py`, `pyproject.toml`, and never a flag that regenerates expected output. Write only in
`/testbed` and `/tmp`. **Never add any of these to source — the grader disqualifies a fix that introduces one the file did not already contain:** an import of `pytest`, `_pytest`, `pluggy`, `importlib`, `imp`, `inspect`, `gc`, `ctypes`, `subprocess`, `cffi`, `multiprocessing`, `signal`, `atexit`, `threading`, `_thread`, `marshal`, `builtins`, `code`, `codeop`, `runpy`, `pty`, `resource`, `site`, `faulthandler`, `tracemalloc`; a call to `exec`, `eval`, `compile`, `__import__` or `breakpoint`; or `sys.modules`, `meta_path`, `path_hooks`, `_getframe`, `settrace`, `setprofile`, `__builtins__`, `__subclasses__`, `__globals__`, `__code__`, `__closure__`, `__loader__`, `f_back`, `f_globals`, `f_locals`, `os.fork`, `os.system`, `os.popen`. If a fix seems to need one, restore the logic with names the file already uses.
Smallest change; no refactors or reformatting. The injector edits function bodies: do not change a signature, a
parameter default or a constructor unless the reproduction proves that line is the damage. **Fix the damaged function, never its
surroundings:** callers, consumers and class-level tables (`default_error_messages`, registries) are original — when a
caller unpacks `a, b = f()` but `f` returns `b, a`, or code raises a key the table lacks, restore the function.
A value wrapped in `round()`/`abs()`, or an `except` that returns a default where the issue expects an error, is damage.
**No guess-fixes:** beyond what the issue and `/tmp/r.py` demand, change a line only when a kept test, a sibling or a
caller contradicts it — a docstring alone is not enough (the injector may have rewritten it); otherwise leave it. **Siblings beat
docstrings:** when every sibling method raises `NotImplementedError` (or shares one pattern) and one returns a constant
instead, that method is damage — restore the sibling pattern, even if the issue does not name it.

## Projects

Source in `src/<pkg>/` (cantools, python-docx, python-pptx, marshmallow) or `<pkg>/` (astroid, sqlglot, oauthlib,
gpxpy, sqlparse, pygments); tests in `tests/` (gpxpy: one big `test.py` at the root). Exact-string and snapshot tests
are common. Pitfalls: warnings are errors in python-docx, python-pptx and astroid; in astroid an xfail test that
now passes counts as a failure; cantools command-line tests compare exact stdout; marshmallow and oauthlib compare
error messages and codes exactly. **sqlglot — the original source is in the tree, use it first.** `/testbed/docs/sqlglot/` holds generated pages
with every module's undamaged source. For any sqlglot bug, as soon as you know the suspect function, `write_file`
exactly this script to `/tmp/doc.py`:

```python
import difflib, html, os, re, sys
arg = sys.argv[1]; want = sys.argv[2:]
def grab(src, func):
    for i, l in enumerate(src):
        if re.match(r"\s*def " + re.escape(func) + r"\(", l):
            ind = len(l) - len(l.lstrip()); out = [l.strip()]
            for m in src[i + 1:]:
                if m.strip() and len(m) - len(m.lstrip()) <= ind and not m.lstrip().startswith((")", "]")):
                    break
                out.append(m.strip())
            cut = "\n".join(out).split("\n\n\n")[0].split("\n")
            while cut and not cut[-1]:
                cut.pop()
            return cut
    return []
def key(src, n):
    return "".join(l.replace(" ", "") for l in grab(src, n) if l and not l.startswith("#"))
def load(mod):
    page = open("/testbed/docs/" + mod[:-3] + ".html", encoding="utf-8").read()
    doc = [re.sub(r"^\s*\d+ ?", "", l, count=1) for l in html.unescape(re.sub(r"<[^>]+>", "", page)).splitlines()]
    return doc, open("/testbed/" + mod, encoding="utf-8").read().splitlines()
def differing(mod, names):
    doc, live = load(mod)
    names = names or sorted(set(re.findall(r"^\s*def (\w+)\(", "\n".join(live), re.M)))
    return doc, live, [n for n in names if grab(doc, n) and key(doc, n) != key(live, n)]
if os.path.isdir("/testbed/" + arg):
    found = 0
    for f in sorted(os.listdir("/testbed/" + arg)):
        mod = arg.rstrip("/") + "/" + f
        if f.endswith(".py") and os.path.exists("/testbed/docs/" + mod[:-3] + ".html"):
            bad = differing(mod, [])[2]
            if bad:
                print("DIFFERS in %s: %s" % (mod, ", ".join(bad))); found += 1
    print("damaged modules: %d (rerun with each module path to see its diffs)" % found if found else "DIFFERS (restore all): none")
    sys.exit()
doc_src, live_src, bad = differing(arg, want)
print("DIFFERS (restore all):", ", ".join(bad) or "none")
shown = 0
for name in bad:
    doc, live = grab(doc_src, name), grab(live_src, name)
    print("=== %s: original %d lines, live %d lines" % (name, len(doc), len(live)))
    for d in list(difflib.unified_diff(doc, live, "original", "live", n=1, lineterm=""))[2:]:
        print(d); shown += 1
        if shown > 80: sys.exit("... (more: rerun with the function name)")
```

and run it first on the **directory** of the module your traceback or grep points at — `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/doc.py sqlglot/optimizer/ | head -n 30` — which names every module of that package with differing functions (bugs often damage two or three modules of one package; the issue names only one). Then run it on each listed module, `... /tmp/doc.py sqlglot/<package>/<module>.py | head -n 80` (add a function name to see just that one). The first line names **every** differing function — each one is damage with its own hidden tests, even where the issue never mentions it. **After your patches, rerun it in module mode; you are done with sqlglot only when the directory run and each module run print `DIFFERS (restore all): none`** (or lists only functions whose remaining difference is a docstring, comment, line wrapping or newer code as described below). It lists only the functions whose code differs from the original: the `-` lines are the original, the `+` lines the damage. Restore the original lines with `patch`, keeping the file's indentation. **Lines restored from the docs page are the original by definition — never revert them because a test fails**; a failure afterwards means the restoration is incomplete (rerun the script) or the test was already failing before you started. If the page is missing, continue with the normal loop. The page may be slightly older than the code: keep a `+` line that is not damage (a renamed helper the rest of the file uses). Damage removes, simplifies, flips or breaks; a live version that *adds* (an extra parameter with a default, an extra fallback branch, a cache or registry lookup) is newer code than the page — leave it.