# Repair the damaged code in /testbed

Someone deliberately broke working code in the Python project at `/testbed`; the issue describes the visible symptoms. The tests that catch the damage were deleted, the other tests are still there. You earn credit for every hidden test your fix makes pass — a partial repair still pays — but if a test that passes now starts failing, the task scores zero. No one will answer questions.

## How to work here (this replaces the generic advice that follows)

Act, then check — not the other way round. You have roughly 25 calls before the token budget stops the run, and a run that ends with the tree untouched earns nothing. Keep reasoning short, and every reply until the end carries a tool call.

Facts already established, so do not spend calls on them: the repository has a single commit (history, `git log`, `git show` tell you nothing); `/opt/sh-pristine` is a copy of the same damaged tree; there is no network and no other copy of the original code anywhere; the interpreter with all dependencies is `/opt/miniconda3/envs/testbed/bin/python` (plain `python` lacks them). Stay inside `/testbed` and `/tmp`.

Every tool result is sent again with every later call. Read code only in slices: find the line with `grep -n … | head -n 20`, then `read_file` with `offset` and `limit` of at most 60 — never a whole file, at most two slices per file. Any command that could print a lot ends in `| head -n 40` or `| tail -n 40`.

## Call 1 — the damage scan (copy it verbatim)

`cd /testbed && B=/opt/miniconda3/envs/testbed/bin; { if [ -x $B/ruff ]; then $B/ruff check --no-cache --quiet --output-format concise --select F821,F841,F811,F823 --exclude tests,test,docs,doc,examples,benchmarks,scripts .; else $B/python -c "import ast,pathlib
for f in sorted(pathlib.Path('.').rglob('*.py')):
 if any(p in f.parts for p in ('tests','test','docs','doc','examples','benchmarks','build','.git')): continue
 try: t=ast.parse(f.read_text())
 except Exception: continue
 for fn in [n for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and not any(isinstance(c,ast.Call) and getattr(c.func,'id','') in ('locals','vars') for c in ast.walk(n))]:
  s={};l=set();skip=set()
  for n in ast.walk(fn):
   if isinstance(n,(ast.For,ast.comprehension)): skip|={x.id for x in ast.walk(n.target) if isinstance(x,ast.Name)}
   if isinstance(n,(ast.Assign,ast.AnnAssign)):
    for tg in (n.targets if isinstance(n,ast.Assign) else [n.target]):
     if isinstance(tg,(ast.Tuple,ast.List)): skip|={x.id for x in ast.walk(tg) if isinstance(x,ast.Name)}
   if isinstance(n,ast.Name):(s.setdefault(n.id,n.lineno) if isinstance(n.ctx,ast.Store) else l.add(n.id))
  [print(f'{f}:{k}: {v} assigned but never used') for v,k in s.items() if v not in l and v not in skip and v[0]!='_']"; fi; grep -rnEi "#\s*(Bug|Subtle|Logical bug|Introduc\w*|Chang\w*|Swap\w*|Revers\w*|Alter(ed|ing)|Incorrect|Incorrectly|Used incorrect|Used wrong|Wrong|Invert\w*|Flip\w*|Removed|Modified|Off-by-one|Exclud\w*)\b" --include=*.py . | grep -vE "^\./(tests?|docs?)/"; } 2>&1 | head -n 150`

It prints almost nothing on healthy code, so every line is a lead: `F821 undefined name` / `F841` / `assigned but never used` mean a statement near that line was deleted, moved or reordered; a comment like `# Changed …`, `# Swapped …`, `# Incorrect …` sits on a line that was altered on purpose — undo exactly what it says and delete the comment (each one is a separate site; they mark only some of the damage).

## Calls 2–3 — reproduce

With `write_file`, put the issue's example into `/tmp/check.py` so it prints `GOT …` next to `EXPECTED …` for every symptom the issue lists; run it with `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/check.py 2>&1 | tail -n 30`. The issue's expected output is the specification. If the example itself fails on the API (an unknown keyword or attribute the issue just used), it was written for another version: reproduce the same symptom with the current API instead of repairing the example.

## Find and fix

The deepest `/testbed` frame of the traceback, or the function that returns the wrong value, is where to look. Read it once and compare each line with its name, its docstring, its callers and its sibling functions. Typical damage:
- a deleted statement (a name used before it is set, an empty branch, a lost `return`), a removed guard or `try/except` fallback;
- an inverted condition, an added or dropped `not`, `<` vs `<=`, an off-by-one in a slice or range, a changed constant, separator or line ending;
- arguments or paired names swapped; a dictionary or attribute name changed;
- a method that callers still use but that no longer exists — write it back modelled on the same-named method of a sibling class;
- a missing key or default means the code that asks for it was changed — fix that code, never add the entry;
- a whole function rewritten into something plausible but wrong — rebuild it from what its callers and the surviving tests expect, not from its (possibly rewritten) docstring.
If the issue describes the current code in a way you cannot find, it is describing the original: put that behaviour back.

**Patch deadline:** the moment you can point at a suspicious line, your next call patches it — a wrong first patch costs one call, no patch costs the task. If `/tmp/check.py` has run twice without an edit in between, your next call is a patch of your best candidate. If nothing looks wrong, add prints of the intermediate values along the path to `/tmp/check.py` and patch where the value first departs from what the issue implies. Two patches at one spot that do not help: undo them and locate again from the traceback.

## Several sites

Damage usually sits in several places — the same function, its siblings, sometimes another module of the package. The issue's list of symptoms is your work list: after each fix, every symptom still wrong in `/tmp/check.py` is another site — `grep -rn` the names it mentions across the package, fix it there. Once the first fix holds, read the rest of the touched function and its neighbours in 60-line slices for further altered lines before you stop.

## After every patch

Run the kept tests of the module you changed — `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <that test file> -q -x -p no:cacheprovider 2>&1 | tail -n 15` — and `/tmp/check.py`. A kept test that now fails means your change is wrong: narrow it or revert it. Passing kept tests prove nothing about the bug itself (its tests are gone); only `/tmp/check.py` matching the issue does.

## Finish

Stop when `/tmp/check.py` prints exactly what the issue expects for every symptom and the scan no longer flags the files you touched. Look at `git diff` once, revert anything unintended, and end with a one-line reply. Never edit tests, fixtures or config, never install anything.

## Project notes

- sqlglot: `tests/fixtures/` holds expected outputs (`identity.sql`, `pretty.sql`, `optimizer/*.sql`) — a quick way to get EXPECTED values; dialect parsers and generators mirror the base `parser.py` / `generator.py`, so a missing branch usually has a twin there.
- cantools: `tests/files/` holds sample databases; a dump of a sample must reproduce its file exactly, line endings included (`repr()` the first differing line).
- astroid: inference bugs show as a wrong or `Uninferable` result — print `next(node.infer())` at each step; brain modules register transforms that must still be registered.
- python-docx: `src/docx/`, the oxml layer maps XML to properties; check the getter and setter as a pair.
- sqlparse: grouping and formatting compare exact strings — print `repr()` of the output.
