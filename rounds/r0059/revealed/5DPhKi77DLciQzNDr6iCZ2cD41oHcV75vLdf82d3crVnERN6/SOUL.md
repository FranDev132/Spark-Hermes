# Fix the injected bug in /testbed

Working code in `/testbed` was mechanically edited to break it. Find the damaged code and put it back by
editing the source with `patch`. Hidden tests grade the result; no one will answer questions.

## Rules that end a run at 0

- A reply without a tool call ends the run. Until the fix is applied, every reply calls a tool; never
  write the fix only in a message.
- Never list, read or run anything under `/ep`, `/runner` or elsewhere outside `/testbed` and `/tmp`.
- Never edit, add or delete tests or test config. If a test that passed before now fails, the score is 0.
- Call `terminal`, `read_file`, `write_file`, `patch`, `search_files` directly — never `tool_call`,
  `tool_search` or `tool_describe`.

## Working habits

- Python is `/opt/miniconda3/envs/testbed/bin/python` (the default `python` lacks pytest and the deps).
- Keep every output small: `read_file` with `offset` and `limit` ≤ 60; end commands with `| head -n 40` or
  `| tail -n 40`; never `cat` a source file or run the whole test suite.
- There is no git history and no other copy of the project — except in sqlglot (below).

## sqlglot: an undamaged copy of the source is in the tree

`/testbed/docs/sqlglot/<same path>.html` (e.g. `sqlglot/optimizer/simplify.py` →
`docs/sqlglot/optimizer/simplify.html`) prints the original source. Once you know the suspect function,
print it from the copy in one call and patch every line where `/testbed` differs (adapt, do not paste
whole functions; the copy may be a slightly different version):
`/opt/miniconda3/envs/testbed/bin/python -c "import html,re;t=html.unescape(re.sub(r'<[^>]+>','',open('/testbed/docs/sqlglot/optimizer/simplify.html').read()));i=t.find('def simplify_not(');print(t[i:i+3000] if i>=0 else 'not found')" | head -n 60`

Stop with one line once your reproduction behaves as the issue says it should.
