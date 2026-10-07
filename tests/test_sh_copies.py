"""The copy penalty's measurement: whose text a bundle carries, and who sealed it first."""

from __future__ import annotations

import json

from sh.validator.copies import NEAR_DUP, Sealed, _shingles, assess, assess_round

ORIGINAL = " ".join(f"step{i} read the failing test then patch the source carefully and verify" for i in range(40))
OTHER = " ".join(f"item{i} grep the repository for the symbol and reproduce the issue first" for i in range(40))


def _b(round_id, hotkey, text, github=None):
    return Sealed(round_id, hotkey, github, frozenset(_shingles(text)))


def test_a_later_copy_by_another_author_is_a_near_duplicate_and_the_original_is_not():
    past = [_b("r0010", "A", ORIGINAL, "alice")]
    cur = [_b("r0012", "A", ORIGINAL, "alice"), _b("r0012", "B", ORIGINAL, "bob"), _b("r0012", "C", OTHER, "carol")]
    a = assess("r0012", cur, past)
    assert a["B"]["near_dup"] and a["B"]["share"] >= NEAR_DUP and a["B"]["source"] == "r0010:alice"
    assert a["A"]["share"] == 0.0 and not a["A"]["near_dup"] and a["A"]["first_seen"] == "r0010"
    assert a["C"]["share"] == 0.0 and a["C"]["first_seen"] == "r0012"


def test_a_partial_copy_sets_prior_copy_and_ordinary_overlap_does_not():
    half = ORIGINAL[: len(ORIGINAL) // 2] + " " + OTHER[: len(OTHER) // 2]
    a = assess("r0012", [_b("r0012", "B", half, "bob")], [_b("r0010", "A", ORIGINAL, "alice")])
    assert 0.3 <= a["B"]["share"] < NEAR_DUP and a["B"]["prior_copy"] == a["B"]["share"] and not a["B"]["near_dup"]
    tiny = OTHER + " " + " ".join(ORIGINAL.split()[:20])
    a = assess("r0012", [_b("r0012", "B", tiny, "bob")], [_b("r0010", "A", ORIGINAL, "alice")])
    assert a["B"]["prior_copy"] == 0.0


def test_an_original_author_is_never_flagged_for_text_others_copied_from_it():
    """A wrote first, B copied it, A later rewrote part of its bundle: the runs A wrote first are still A's."""
    edited = ORIGINAL[: len(ORIGINAL) * 2 // 3] + " " + OTHER[: len(OTHER) // 3]
    past = [_b("r0010", "A", ORIGINAL, "alice"), _b("r0011", "B", ORIGINAL, "bob")]
    a = assess("r0014", [_b("r0014", "A", edited, "alice")], past)
    assert a["A"]["share"] == 0.0


def test_same_hotkey_or_same_account_is_never_a_copy_and_same_round_is_not_compared():
    past = [_b("r0010", "A", ORIGINAL, None), _b("r0011", "A2", OTHER, "alice")]
    a = assess("r0012", [_b("r0012", "A", ORIGINAL, "alice"), _b("r0012", "A3", OTHER, "alice")], past)
    assert a["A"]["share"] == 0.0 and a["A3"]["share"] == 0.0  # old seal without an account: the hotkey matches
    a = assess("r0012", [_b("r0012", "X", ORIGINAL, "x"), _b("r0012", "Y", ORIGINAL, "y")], [])
    assert a["X"]["share"] == 0.0 and a["Y"]["share"] == 0.0


def test_assess_round_reads_seals_and_bundles(tmp_path):
    for rid, active in (("r0010", {"A": "alice"}), ("r0012", {"A": "alice", "B": "bob"})):
        rd = tmp_path / rid
        (rd / "bundles").mkdir(parents=True)
        (rd / "seal.json").write_text(json.dumps({"active": {h: {"github": g} for h, g in active.items()}}))
        for h in active:
            (rd / "bundles" / h).mkdir()
            (rd / "bundles" / h / "SOUL.md").write_text(ORIGINAL)
            (rd / "bundles" / h / "attestation.json").write_text("{}")
    a = assess_round(tmp_path, tmp_path / "r0012")
    assert a["B"]["near_dup"] and not a["A"]["near_dup"] and a["A"]["first_seen"] == "r0010"
