"""Did a strategy copy another author's earlier bundle? (the copy penalty, `sh.scoring.v2`)

Every crowned bundle is revealed at close, and every sealed bundle is kept with its round. A later submission can
paste one in whole or in part and score like the original without adding anything. This module measures, for each
strategy sealed this round, the share of its text that **another author** sealed **before this author first used it**:

  * text is compared as distinct 12-token runs (shingles, as the S1 check in `sh.validator.similarity`), so
    reflowing or reformatting a paste does not hide it;
  * each shingle belongs to whoever sealed it first: a run counts as copied only when another author sealed it in
    an earlier round than this author's own first use of it. An original author who later edits their bundle keeps
    the runs they wrote first, even after others copied them; two authors who first use a run in the same round
    are not counted against each other;
  * "another author" excludes the same hotkey and the same GitHub account (seals before r0052 carry no account;
    the hotkey still matches).

The share becomes the scoring inputs: at ≥ `NEAR_DUP` the bundle is a near-duplicate (score 0, never crowned);
from `COPY_FROM` it is `prior_copy` (the score is cut by `copy_penalty` × share); below that it is ordinary shared
phrasing (calibrated on r0058-r0064: originals share 1-11 %, the largest partial reuse 25 %).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sh.validator.similarity import _shingles

NEAR_DUP = 0.80  # this share of a bundle sealed first by other authors: a near-duplicate
COPY_FROM = 0.30  # from this share up, the share is the score's prior_copy
SAME_STRATEGY = 0.80  # a hotkey's bundle this close to its current one counts as the same strategy, first seen then


def bundle_text(d: Path) -> str:
    """A sealed bundle's text: every file but the attestation, in a fixed order."""
    parts = []
    for f in sorted(p for p in d.rglob("*") if p.is_file() and p.name != "attestation.json"):
        try:
            parts.append(f.read_text(errors="ignore"))
        except OSError:
            continue
    return "\n".join(parts)


@dataclass(frozen=True)
class Sealed:
    round_id: str
    hotkey: str
    github: str | None
    shingles: frozenset


def history(rounds: Path) -> list[Sealed]:
    """Every bundle any round sealed, oldest round first (rounds/<rid>/seal.json + rounds/<rid>/bundles/<hotkey>/)."""
    out = []
    for rd in sorted(p for p in rounds.glob("r*") if p.is_dir()):
        try:
            active = json.loads((rd / "seal.json").read_text()).get("active") or {}
        except (OSError, ValueError):
            continue
        for hotkey, info in active.items():
            d = rd / "bundles" / hotkey
            if d.is_dir():
                sh = _shingles(bundle_text(d))
                if sh:
                    out.append(Sealed(rd.name, hotkey, (info or {}).get("github"), frozenset(sh)))
    return out


def _share(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a) if a else 0.0


def assess(round_id: str, current: list[Sealed], past: list[Sealed]) -> dict[str, dict]:
    """{hotkey: {share, source, first_seen, near_dup, prior_copy}} for this round's sealed bundles. `first_seen` is the
    earliest round this hotkey sealed essentially this bundle (≥ SAME_STRATEGY), the crown's tie order."""
    everyone = sorted(past + current, key=lambda b: b.round_id)
    seen: dict[tuple, list[Sealed]] = {}  # shingle -> the bundles that carry it, first use per hotkey, oldest first
    for b in everyone:
        for sh in b.shingles:
            lst = seen.setdefault(sh, [])
            if not any(x.hotkey == b.hotkey for x in lst):
                lst.append(b)
    out = {}
    for c in current:
        mine = lambda b: b.hotkey == c.hotkey or (c.github and b.github and b.github == c.github)  # noqa: E731
        copied = 0
        by_source: dict[str, int] = {}
        for sh in c.shingles:
            users = seen.get(sh, ())
            own = min((b.round_id for b in users if mine(b)), default=round_id)
            other = next((b for b in users if not mine(b)), None)
            if other is not None and other.round_id < own:
                copied += 1
                key = f"{other.round_id}:{other.github or other.hotkey[:12]}"
                by_source[key] = by_source.get(key, 0) + 1
        share = copied / len(c.shingles) if c.shingles else 0.0
        own_past = [b for b in past if b.hotkey == c.hotkey]
        first = min((b.round_id for b in own_past if _share(c.shingles, b.shingles) >= SAME_STRATEGY), default=round_id)
        out[c.hotkey] = {
            "share": round(share, 4),
            "source": max(by_source.items(), key=lambda kv: kv[1])[0] if by_source else None,
            "first_seen": first,
            "near_dup": share >= NEAR_DUP,
            "prior_copy": round(share, 4) if COPY_FROM <= share < NEAR_DUP else 0.0,
        }
    return out


def assess_round(rounds: Path, round_dir: Path) -> dict[str, dict]:
    """`assess` for the round in `round_dir`, against every earlier round under `rounds`."""
    allb = history(rounds)
    rid = round_dir.name
    current = [s for s in allb if s.round_id == rid]
    if not current:  # the round's own seal may live outside `rounds` (tests, a round being closed by hand)
        current = [s for s in history(round_dir.parent) if s.round_id == rid]
    return assess(rid, current, [s for s in allb if s.round_id < rid])
