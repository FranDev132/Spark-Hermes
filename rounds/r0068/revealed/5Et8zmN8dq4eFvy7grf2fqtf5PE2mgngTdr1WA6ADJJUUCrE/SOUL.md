# /testbed

A mutator altered a few statements of the Python library in `/testbed`. Put the original code back, then
reply in one sentence without a tool call. Work in your normal way; what follows is only what you cannot
see from inside the sandbox.

Grading: the deleted tests that exposed the change return and each passing one earns its share, but a
single previously passing test that fails makes the task zero. Many symptoms in the issue mean many changed
places; restore all of them, in the same files, since edits to other files are ignored.

Tokens are the limit (about 600k summed over every call, with all earlier output re-sent each time), so
read files in slices of about 50 lines from a `grep -n` hit, never whole, and keep each print short. Patch
once you have a solid candidate. A repro that will not run twice is not worth a third try: use a sample
file from the test tree as input, or audit the function the grep found.

After a patch, two things look like a second bug and are not: a kept test that fails only now was broken
by your patch (restore the original line exactly, with its `.strip()`, its `else:`, its indentation), and
an error the issue never promised to remove is the original behaviour. Stop there instead of searching on.

sqlglot only: no pristine copy of the source exists, so use its symmetry. A dialect file overrides the
base parser or generator, and sibling dialects write the same construct the same way: the one that
disagrees is damaged. The kept tests (`tests/dialects/test_<dialect>.py`) and the optimizer fixture files
under `tests/fixtures/optimizer/` spell out the exact expected SQL; grep them for the construct.

Never, or the score is zero: a path or command with `/ep` or `/runner`, anything outside `/testbed` and
`/tmp`, network or installs, any change to tests, fixtures, `conftest.py` or project configuration, and new
uses of `inspect`, `importlib`, `subprocess`, `threading`, `signal`, `gc`, `ctypes`, `builtins`, pytest,
`eval`, `exec`, `compile` or `sys.modules` in library code. Interpreter:
`/opt/miniconda3/envs/testbed/bin/python`.
