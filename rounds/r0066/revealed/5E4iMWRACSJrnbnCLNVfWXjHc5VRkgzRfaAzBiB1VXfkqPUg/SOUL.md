# Repair task for /testbed

A tool altered working code in the Python project at /testbed so that it misbehaves. Your job is to put it back. The tests that exposed the change were removed from the tree; the other tests remain. You are scored by the share of the removed tests that pass after your change, and the whole task scores zero if any test that passed before now fails. No one will answer questions.

## What takes priority here

If other instructions you were given tell you to collect prerequisites or become certain before acting, this page wins: act first, verify afterwards. The run ends after about 100 turns or about 600 thousand tokens in total, and every tool output is sent again with each later call, so long outputs shorten your run. Aim to have a source edit in place by about your 8th call. If 12 calls pass without a change to library code, apply your best-supported candidate and let the check judge it. Keep your thinking to a few sentences, put independent look-ups into one reply, and make every reply contain a tool call until you are done. An unchanged tree scores zero.

## Environment

- Work only inside /testbed (the fix) and /tmp (scratch files). Do not list, open or run anything elsewhere, not even with ls: it can end the run. There is no second copy of the project to compare against, and git holds a single commit, so use git only for a final git diff.
- Run Python and pytest as /opt/miniconda3/envs/testbed/bin/python, written out in full. The python on PATH lacks the project's dependencies.
- Use the tools terminal, read_file, search_files, patch and write_file directly. If one fails twice, do the same job with terminal.
- No network, no pip.
- Leave out the terminal tool's timeout argument. It is in seconds, and a large value sends the command to the background so you lose calls waiting for it. Never sleep.
- Keep output small: find a line with grep -n, then read_file with a limit of 60 or less; end commands with | head -40 or | tail -40; never cat a source file and never run the whole test suite.

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
8. Sweep with a checklist. Write down every symptom the issue lists. One issue with several symptoms often means several altered places, in different functions of one file or in sibling files. After each patch rerun the check and cross off what now behaves; a symptom still open is credit still on the table. Patch further only on concrete evidence (a docstring, a sibling, a caller, a crash), and do not hunt through the whole repository.
9. Finish. Read git diff once, undo anything unintended, delete any debug print, and stop with a one-line reply.

## Guarding against regressions

Before your first patch, run the test file that covers the module once, without -x, and note which tests already fail, so a failure you did not cause is not mistaken for one you did. After patching, run it again: a test that passed in the first run and fails now means your latest hunk is wrong, so narrow or undo that hunk, and put the original line back exactly, including small things such as a .strip(), an else:, or the indentation of a final return.

## Let the kept tests and fixtures speak

Only the tests that exposed the damage were removed. The rest of the test tree, including its fixture and sample files, is intact and shows the exact output the project expects. For code that dumps, serializes, formats or converts, run the damaged function on one fixture of that format and compare the result with the fixture using a short script in /tmp: lines the fixture has and your output lacks are deleted statements, and differing values are changed ones. When two functions are meant to mirror each other (load and dump, encode and decode, one dialect and the base), the one that disagrees with its counterpart is the damaged one.

## When one value is still wrong after a fix

If the reproduction now matches the issue except for one value the issue states (say 5 where the issue expects 6), treat that value as a second altered site, not as original behaviour, however natural the code looks. Find what produces exactly that value (the getter, property, helper or sibling method). Look in the same function, class and file first, then the neighbouring files of the package, and patch it so the output matches the issue. One grep of the kept tests for that name is the only check to make first: if a kept test pins the current value, follow the value one step further back instead. Behaviour the issue never states, such as a second example raising a different error, is not a second bug: leave it.

## sqlglot: the original source is in the tree

/testbed/docs/sqlglot/ holds generated pages that print each module's original, undamaged source with line numbers (sqlglot/optimizer/simplify.py is docs/sqlglot/optimizer/simplify.html, a dialect is docs/sqlglot/dialects/<name>.html). As soon as grep or the traceback names a sqlglot module, use write_file to save the script below as /tmp/d.py, then run it with the full interpreter path and the module path as the argument, for example: /opt/miniconda3/envs/testbed/bin/python /tmp/d.py sqlglot/optimizer/simplify.py | head -n 80

```python
import difflib, html, re, sys
mod = sys.argv[1]
name = mod[:-3]
if name.endswith("/__init__"):
    name = name[:-9]
raw = open("/testbed/docs/" + name + ".html", encoding="utf-8").read()
pre = max(re.findall(r"<pre[^>]*>(.*?)</pre>", raw, flags=re.S), key=len)
text = html.unescape(re.sub(r"<[^>]+>", "", pre))
orig = [re.sub(r"^ *[0-9]+", "", ln, count=1).rstrip() for ln in text.splitlines() if re.match(r"^ *[0-9]+", ln)]
cur = [ln.rstrip() for ln in open("/testbed/" + mod, encoding="utf-8").read().splitlines()]
diff = [ln for ln in difflib.unified_diff(orig, cur, n=0, lineterm="") if ln[:1] in "-+@" and ln[:3] not in ("---", "+++")]
print(*(diff[:120] or ["SAME"]), sep=chr(10))
```

Each line starting with @@ gives line numbers, a line starting with - is the original, and a line starting with + is the current text. Restore the - lines of the function named by the issue or the traceback first, keeping every leading space exactly as the - line has it. Then look at every other hunk: one that looks like damage (a deleted assignment, a flipped condition, a swapped argument) is its own hidden test, so restore it as well. Run the kept test file after each restored function; if a test that passed before now fails, undo that one hunk. If the diff shows many hunks far from the issue, the page is from another version: restore only the hunks that look like damage, and keep any + block that adds a helper which unchanged lines still call. Finish when the script prints SAME or only docstring, comment or line-wrapping differences remain. If the script raises an error or the page is missing, go back to the normal procedure.

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
- sqlglot: parse methods in parser.py that use a local before it is set, dialect checks with the sense flipped in optimizer/qualify_columns.py, and entries in a dialect's class-level tables that differ from the base class.
- python-docx and python-pptx: properties that return a copy or a stale object instead of the live element, and swapped branches in oxml setters.
- sqlparse: node classes in sql.py that lost a base class, and calls in engine/grouping.py that were deleted or reordered.
- oauthlib: validator or endpoint methods that return a fixed value where their siblings raise NotImplementedError, and scope, grant type or error-code comparisons that were flipped or dropped.
- gpxpy: time and duration arithmetic with the operands swapped, and a guard on missing times or points that vanished.
- marshmallow: a field's default, missing or error-message handling that differs from its sibling fields.
