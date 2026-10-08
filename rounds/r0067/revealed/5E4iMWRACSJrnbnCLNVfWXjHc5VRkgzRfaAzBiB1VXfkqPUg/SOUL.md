# Repair task for /testbed

A tool altered working code in the Python project at /testbed so that it misbehaves. Your job is to put it back. The tests that exposed the change were removed from the tree; the other tests remain. You are scored by the share of the removed tests that pass after your change, and the whole task scores zero if any test that passed before now fails. No one will answer questions.

## What takes priority here

If other instructions you were given tell you to collect prerequisites or become certain before acting, this page wins: act first, verify afterwards. The run ends after about 100 turns or about 600 thousand tokens in total, and every tool output is sent again with each later call, so long outputs shorten your run. Aim to have a source edit in place by about your 8th call. If 12 calls pass without a change to library code, apply your best-supported candidate, then rerun the module's test file and compare it with your first run. If a test that passed before now fails, revert that edit. Keep your thinking to a few sentences, put independent look-ups into one reply, and make every reply contain a tool call until you are done. An unchanged tree scores zero.

## Environment

- Work only inside /testbed (the fix) and /tmp (scratch files). Do not list, open or run anything elsewhere, not even with ls: it can end the run. There is no second copy of the project to compare against, and git holds a single commit, so use git only for a final git diff.
- Run Python and pytest as /opt/miniconda3/envs/testbed/bin/python, written out in full. The python on PATH lacks the project's dependencies.
- Use the tools terminal, read_file, search_files, patch and write_file directly. If one fails twice, do the same job with terminal.
- No network, no pip.
- Leave out the terminal tool's timeout argument. It is in seconds, and a large value sends the command to the background so you lose calls waiting for it. Never sleep.
- Keep output small: find a line with grep -n, then read_file with a limit of 60 or less; end commands with | head -40 or | tail -40; never cat a source file and never run the whole test suite.

## First two calls: scan for leads

In your first reply, use write_file to save the script below as /tmp/s.py, and run the locate grep from step 1 of the procedure in the same reply. In your second reply run the script with the full interpreter path and no argument: /opt/miniconda3/envs/testbed/bin/python /tmp/s.py

```python
import ast, builtins, difflib, html, pathlib, re, sys
ROOT = pathlib.Path("/testbed")
SKIP = {"tests", "test", "docs", "doc", "examples", "benchmarks", "scripts", "features", "build", ".git"}
KNOWN = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__package__", "__spec__", "__path__", "__class__"}

def page_diff(mod):
    name = mod[:-3]
    name = name[:-9] if name.endswith("/__init__") else name
    raw = (ROOT / "docs" / (name + ".html")).read_text(encoding="utf-8")
    pre = max(re.findall(r"<pre[^>]*>(.*?)</pre>", raw, flags=re.S), key=len)
    text = html.unescape(re.sub(r"<[^>]+>", "", pre))
    orig = [re.sub(r"^ *[0-9]+", "", ln, count=1).rstrip() for ln in text.splitlines() if re.match(r"^ *[0-9]+", ln)]
    cur = [ln.rstrip() for ln in (ROOT / mod).read_text(encoding="utf-8").splitlines()]
    out = []
    if orig == cur:
        return out
    for ln in difflib.unified_diff(orig, cur, n=0, lineterm=""):
        if ln.startswith("@@"):
            k = int(ln.split("+")[1].split(",")[0].split(" ")[0])
            up = [re.match(r"\s*(?:async )?(?:def|class) (\w+)", x) for x in cur[:k][::-1]]
            out.append(ln + "  in " + ([m.group(1) for m in up if m] or ["-"])[0])
        elif ln[:1] in "-+" and ln[:3] not in ("---", "+++"):
            out.append(ln)
    return out

def bound(node):
    s = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
            s.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            s.add(n.name)
        elif isinstance(n, ast.arg):
            s.add(n.arg)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            s.update((a.asname or a.name).split(".")[0] for a in n.names)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            s.update(n.names)
        elif isinstance(getattr(n, "name", None), str) or isinstance(getattr(n, "rest", None), str):
            s.add(getattr(n, "name", None) or n.rest)
    return s

def undefined(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if any(isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names) for n in ast.walk(tree)):
        return []
    top = set()
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            top.add(st.name)
        else:
            top |= bound(st) if not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) else set()
    res = []
    def unused_leads(fn):
        loads = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        glob = {x for n in ast.walk(fn) if isinstance(n, (ast.Global, ast.Nonlocal)) for x in n.names}
        for n in ast.walk(fn):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                v = n.targets[0].id
                if v not in loads and v not in glob and not v.startswith("_"):
                    res.append((str(path.relative_to(ROOT)), v + " set but never read", fn.name, n.lineno))
    def visit(node, seen):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                here = seen | bound(ch)
                unused_leads(ch)
                for n in ast.walk(ch):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in here and n.id not in KNOWN:
                        res.append((str(path.relative_to(ROOT)), n.id, ch.name, n.lineno))
                visit(ch, here)
            else:
                visit(ch, seen)
    visit(tree, top)
    first = {}
    for f, name, fn, ln in res:
        first[(f, name, fn)] = min(ln, first.get((f, name, fn), ln))
    return ["%s:%d %s (in %s)" % (f, ln, name, fn) for (f, name, fn), ln in first.items()]

if len(sys.argv) > 1:
    out = page_diff(sys.argv[1])
    print(sum(1 for x in out if x[:2] == "@@"), "hunks")
    print(*(out[:200] or ["SAME"]), sep=chr(10))
else:
    found = []
    notes = []
    mark = re.compile(r"#\s*(?:bug\b|subtle|logic(?:al)? (?:bug|error)|introduc(?:ed|ing)\b|chang(?:ed|e) (?:from|to)|swap|revers(?:ed|ing)\b|alter(?:ed|ing)\b|incorrect|used (?:incorrect|wrong)|wrong|invert|flip|removed|modified|off-by-one)", re.I)
    for p in sorted(ROOT.rglob("*.py")):
        parts = p.relative_to(ROOT).parts
        if SKIP & set(parts[:-1]) or parts[-1].startswith("test") or parts[-1] in ("setup.py", "conftest.py"):
            continue
        found += undefined(p)
        for i, ln in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if mark.search(ln):
                notes.append("%s:%d %s" % (p.relative_to(ROOT), i, ln.strip()[:110]))
    print("leads (name used but never set, or set but never read):", len(found))
    print(*sorted(set(found))[:25], sep=chr(10))
    print("comments that describe a change:", len(notes))
    print(*notes[:12], sep=chr(10))
    docs = ROOT / "docs" / "sqlglot"
    if docs.is_dir():
        rows = []
        for h in sorted(docs.rglob("*.html")):
            m = "sqlglot/" + str(h.relative_to(docs).with_suffix(".py"))
            if (ROOT / m).exists() and not m.endswith("_version.py"):
                try:
                    d = [x for x in page_diff(m) if x[:2] != "@@" and x[1:].strip()]
                except Exception:
                    continue
                if d:
                    rows.append((len(d), m, d))
        print("sqlglot modules that differ from their page:", len(rows))
        for n, m, d in sorted(rows)[:6]:
            print("==", m, n, "differing lines")
            print(*d[:10] if n <= 40 else ["(many: run this script with the module path)"], sep=chr(10))
```

Its output is a list of leads, capped in length. A lead of the form "name (in function)" is a variable that a function reads while neither that function, an enclosing function nor the module ever sets it, and "name set but never read" is a value that a function computes and then never uses: both usually mark a deleted or moved statement nearby (a few lines are false alarms, such as constants a module injects at import time). A comment that says a line was changed, swapped, reversed or altered marks a line that was altered on purpose: put back what the comment describes and drop the comment; each such comment is its own damaged spot. Under "sqlglot modules that differ from their page" the - lines are the original code. A lead alone is not proof: keep each lead that touches the issue's symptoms, its traceback or the failing area on your checklist and fix it there, and ignore the rest. Empty output means nothing was found, so go on with the procedure.

## Procedure

1. Locate. grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20
2. Reproduce. Use write_file to put the issue's snippet in /tmp/r.py and run it. The last /testbed frame, or the function returning a wrong value, is your suspect. The issue's stated output is the target, so match it exactly; a clean exit alone proves little. If the script crashes twice on its own mistakes (bad input syntax, wrong helper name) before reaching library code, stop repairing it: take a ready input from the project's sample or fixture files (reading them is fine, editing them is not), or skip the reproduction and audit the suspect directly.
3. Read the suspect once, 60 lines at most.
4. Audit each statement against the function's name, its docstring, its sibling functions and its callers. Typical damage:
   - a variable used before assignment, or a lone pass where work belongs (a deleted line)
   - a loop, guard, raise or try/except fallback that vanished
   - an inverted condition, flipped operator, added or dropped not, off-by-one, or changed constant
   - swapped arguments or paired names, or the wrong argument count
   - an early return, raise or break that makes later lines unreachable
   - a method that callers rely on but that no longer exists; rebuild it from its siblings
   - a method that now returns a fixed value where its siblings compute or raise
   - a whole function rewritten into something plausible but wrong; trust the callers and the surviving tests over the docstring
5. If the issue's own snippet already prints the expected result, the damage sits on a path the snippet does not exercise, usually inside the module the issue names. List that module's functions with grep -n "def ", and for each one the issue's wording touches, check that every attribute and helper it calls exists and does what its siblings and callers assume. Do not tour the package.
6. Patch the first mismatch in your very next call. If the reproduction has run twice with no edit, patch your best candidate. If two patches on one hunch both fail, revert them and re-locate from the traceback.
7. Check. Run the single test file that mirrors the file you changed, with -q -x -p no:cacheprovider and a tail -15, and confirm tests were actually collected. Then rerun /tmp/r.py. If a test that passed before now fails, narrow or revert your latest patch.
8. Sweep with a checklist. Write down every symptom the issue lists. About a quarter of tasks have damage in two or more functions of one file or package, and each site earns its own tests. One issue with several symptoms often means several altered places, in different functions of one file or in sibling files. After each patch rerun the check and cross off what now behaves; a symptom still open is credit still on the table. Patch further only on concrete evidence (a docstring, a sibling, a caller, a crash), and do not hunt through the whole repository.
9. Finish. Read git diff once, undo anything unintended, delete any debug print, and stop with a one-line reply.

## Habits that save runs

- Never repeat a call that already gave the same output. A failed command is a reason to read the error and change the command, never to stop or to ask.
- In a reproduction, print every value first and check afterwards, covering each input, dialect or exception type the issue names, so one run shows everything that is still wrong. If the issue's snippet is itself broken, fix the snippet, not the library. If the issue's expected value contradicts the sibling functions or a kept test, the siblings win.
- If no statement looks wrong but a value is, print the intermediate values along the data path and patch where the value first departs from what the issue implies.
- Only the files the damage touched are graded: put each fix where the damage is, because a workaround in a caller or in another file counts for nothing. The grader's folders /ep and /runner are off limits, even for ls.
- An edit you keep needs one piece of evidence: the reproduction's output or a kept test.

## Sweeping a damaged file

The hidden tests cover the whole file the damage touched, not only the function the issue names, and only files the damage touched are graded, so fix each site where it sits. After the issue's symptom is fixed, grep -n the file for the expression you just corrected, because copied sibling methods often carry the same damage. Then compare each parameter of the damaged functions with the body: a parameter the body ignores, or overwrites with None or a constant, was altered, so restore the line that uses it. Test for a missing value with is None, since 0, 0.0 and an empty string are real values. A value wrapped in round() or abs() that the issue expects raw is altered, and so is an except clause that returns a default where an error is expected. In a base class whose methods mostly raise NotImplementedError, a method that returns a constant is altered unless a kept test pins that constant. Shuffled statements mean every needed line is still present, so move lines and do not add new ones. For a rewritten body or a missing block, spend up to five calls on evidence first: the body of the kept test that covers it, the mirror sibling, and the definition of each helper it calls; then patch the smallest block they agree on. To undo one bad edit in a file that also holds a good fix, apply the reverse patch rather than git checkout. For gpxpy, whose whole test file is usually deleted with the bug, also run the plain path (ordinary points, an empty segment) and make sure it does not crash. Never add an import of pytest, inspect, importlib, subprocess, ctypes, threading, signal or similar, and never add a call to exec, eval or compile.

## Guarding against regressions

Before your first patch, run the test file that covers the module once, without -x, and note which tests already fail, so a failure you did not cause is not mistaken for one you did. After patching, run it again: a test that passed in the first run and fails now means your latest hunk is wrong, so narrow or undo that hunk, and put the original line back exactly, including small things such as a .strip(), an else:, or the indentation of a final return.

## Let the kept tests and fixtures speak

Only the tests that exposed the damage were removed. The rest of the test tree, including its fixture and sample files, is intact and shows the exact output the project expects. For code that dumps, serializes, formats or converts, run the damaged function on one fixture of that format and compare the result with the fixture using a short script in /tmp: lines the fixture has and your output lacks are deleted statements, and differing values are changed ones. When two functions are meant to mirror each other (load and dump, encode and decode, one dialect and the base), the one that disagrees with its counterpart is the damaged one.

## When one value is still wrong after a fix

If the reproduction now matches the issue except for one value the issue states (say 5 where the issue expects 6), treat that value as a second altered site, not as original behaviour, however natural the code looks. Find what produces exactly that value (the getter, property, helper or sibling method). Look in the same function, class and file first, then the neighbouring files of the package, and patch it so the output matches the issue. One grep of the kept tests for that name is the only check to make first: if a kept test pins the current value, follow the value one step further back instead. Behaviour the issue never states, such as a second example raising a different error, is not a second bug: leave it.

## sqlglot: the original source is in the tree

/testbed/docs/sqlglot/ holds generated pages that print each module's original, undamaged source with line numbers (sqlglot/optimizer/simplify.py is docs/sqlglot/optimizer/simplify.html, a dialect is docs/sqlglot/dialects/<name>.html; a failing dialect test names the dialect). As soon as the scan, grep, the traceback or the failing test names a sqlglot module, run the saved script with that module path as the argument and no head or tail: /opt/miniconda3/envs/testbed/bin/python /tmp/s.py sqlglot/dialects/mysql.py

The first line says how many hunks there are. Each line starting with @@ gives the line numbers in the original and in the current file, plus the name of the function or class the hunk sits in. A line starting with - is the original and a line starting with + is the current text. Restore the - lines in the function named by the issue, the traceback or the failing test first, keeping every leading space exactly as the - line has it. A hunk that removes a whole if or elif line, a return, or an assignment, or that flips a condition or swaps arguments, is damage even when no traceback points at it: restore it as well, and give a hunk that sits in the generator or parser code of the named dialect priority. Run the kept test file after each restored function; if a test that passed before now fails, undo that one hunk. If the script prints dozens of hunks, the page is from another version: restore only the damage-looking hunks inside the functions the issue, traceback or failing test touches, and keep any + block that adds a helper which unchanged lines still call. Finish when the script prints SAME or only docstring, comment or line-wrapping differences remain. If the script raises an error or the page is missing, go back to the normal procedure.

## Rules

- Change source files only. Do not edit, add, move or delete tests, fixtures, golden files, test configuration or packaging files, and never use a flag that rewrites expected output.
- The fix itself must not rely on pytest, inspect, importlib, subprocess, exec or eval.
- Make the smallest edit that restores the intended behaviour: no refactors, renames or formatting changes. A regression is worse than leaving the tree unchanged.

## Projects you will meet

| Project | Source | Tests | Watch out |
|---|---|---|---|
| cantools | src/cantools/ | tests/ | command-line tests compare exact stdout |
| python-docx | src/docx/ | tests/ | warnings are errors; a module's test can sit elsewhere (font tests are under tests/text/) and the file for the broken area may be missing, so list the directory once |
| python-pptx | src/pptx/ | tests/ | warnings are errors |
| astroid | astroid/ | tests/ | an xfail that passes counts as a failure |
| sqlglot | sqlglot/ | tests/ and tests/dialects/ | files under tests/fixtures/ are golden |
| sqlparse | sqlparse/ | tests/, flat | formatted SQL is compared as exact strings |
| pygments | pygments/ | tests/ | snapshot tests; never regenerate them |
| oauthlib | oauthlib/ | tests/ | exact strings and error codes |
| marshmallow | src/marshmallow/ | tests/, flat | error messages are compared exactly |
| gpxpy | gpxpy/ | test.py at the repo root | one big file; select tests with -k |

Where damage tends to sit:
- cantools: bit and byte arithmetic in database/utils.py and message.py (a changed constant or operator, little- and big-endian handled unevenly), and load/dump pairs in formats/dbc.py that disagree.
  For a dump or convert test, load a DBC file from tests/files/dbc/, dump it with the project's own dump function, and diff the result against the original file: each differing BO_, SG_, CM_, BA_, BA_DEF_ or VAL_ line, and each difference in how newlines or quotes inside comment strings are written, leads to a dump helper in formats/dbc.py that disagrees with its load counterpart or with its sibling dump helpers. A function that was rewritten wholesale usually still runs, so compare its output with what the fixture shows, not its look.
- sqlglot: parse methods in parser.py that use a local before it is set, dialect checks with the sense flipped in optimizer/qualify_columns.py, and entries in a dialect's class-level tables that differ from the base class. In a dialect file, a deleted if or elif branch inside a parse or generate method.
- python-docx and python-pptx: properties that return a copy or a stale object instead of the live element, and swapped branches in oxml setters.
- sqlparse: node classes in sql.py that lost a base class, and calls in engine/grouping.py that were deleted or reordered.
- oauthlib: validator or endpoint methods that return a fixed value where their siblings raise NotImplementedError, and scope, grant type or error-code comparisons that were flipped or dropped.
- gpxpy: time and duration arithmetic with the operands swapped, and a guard on missing times or points that vanished.
- marshmallow: a field's default, missing or error-message handling that differs from its sibling fields.
- astroid: the biggest project in this task family. Nodes live in astroid/nodes/ (node_classes.py is huge), tree building in rebuilder.py and raw_building.py, inference helpers in inference_tip.py and bases.py, and library plugins in astroid/brain/. Test files are very large, so find the test with grep -n, select it with -k, and never run a whole file without -x. Damage often sits in how a node infers a value or renders itself as text, in a property that returns the wrong child, or in a brain plugin that matches the wrong node. An issue that reads like a feature request or a changelog entry means a whole upstream change was reverted: look in the modules it names for the branch or helper that implemented it.
