#!/usr/bin/env python3
"""Worst Fix Ever: Funniest Commit Message - make.fun entry.

Writes one commit-message line (at most 100 characters) to
/output/entry.txt. The judge compares entries two at a time by its
published brief, in this priority order:

  1. Reads as a one-line commit message for a bug fix that made
     everything worse (pass/fail gate, applied before scoring).
  2. Makes a reader laugh out loud: a real joke, not a complaint.
  3. Captures the specific irony of a repair that broke more than
     it mended.
  4. Sounds like a real commit subject line: short, plain, the kind
     a tired engineer would actually type at the end of a bad day.
  5. Finds a fresh angle instead of the obvious ones about
     reverting, testing in production or breaking everything.

The program scores a small set of candidate lines against criteria
2-5 (weights follow the judge's priority order) and writes the
winner. Deterministic: no network, no input, no randomness, no
clock. The gate (criterion 1 plus the sealed scorer's 1-100
character, UTF-8, non-blank rule) is enforced before writing.
"""

import os
import sys

# Criterion weights, in the judge's priority order (criterion 1 is a
# pass/fail gate applied before scoring; 2 matters most, then 3, 4, 5).
WEIGHTS = {"funny": 4, "irony": 3, "voice": 2, "fresh": 1}

CANDIDATES = [
    {
        "text": "fix: users couldn't log in; now everyone is an admin",
        "scores": {"funny": 5, "irony": 5, "voice": 5, "fresh": 4},
        "why": "The original bug (nobody can log in) and the backfire "
               "(everybody is an admin) are both named in one plain "
               "clause each, so the irony needs no explanation: the fix "
               "did not restore access control, it abolished it. The "
               "punchline is a concrete catastrophe, not a complaint, "
               "and the semicolon reads exactly like a tired engineer "
               "confessing in a subject line.",
    },
    {
        "text": "fix: off-by-one error now off by two",
        "scores": {"funny": 4, "irony": 5, "voice": 5, "fresh": 5},
        "why": "The purest form of the brief: the repair made the very "
               "same error measurably worse, by exactly one. Elegant and "
               "fresh, but the laugh is a clever nod rather than a "
               "laugh-out-loud, so it trails the winner on criterion 2.",
    },
    {
        "text": "fix: flaky test fixed, it now fails reliably",
        "scores": {"funny": 4, "irony": 5, "voice": 5, "fresh": 4},
        "why": "'Fails reliably' is a beautiful oxymoron and the line "
               "sounds exactly like a real commit. But the backfire is "
               "a test outcome, not a user-facing disaster, so the joke "
               "lands a notch softer than the winner's.",
    },
    {
        "text": "fix: daily crash fixed, server now crashes hourly",
        "scores": {"funny": 4, "irony": 4, "voice": 5, "fresh": 4},
        "why": "A measurable worsening (daily to hourly) in deadpan "
               "voice. Strong, but 'crashes more often' is a thinner "
               "irony than a fix that inverts its own purpose.",
    },
    {
        "text": "fix: modal that wouldn't close now never opens",
        "scores": {"funny": 4, "irony": 4, "voice": 4, "fresh": 4},
        "why": "Clean overcorrection joke: the unclosable thing is now "
               "unopenable. Real voice, but the stakes are a UI modal, "
               "so the laugh is smaller.",
    },
    {
        "text": "fix: duplicate emails fixed, users now get triplicates",
        "scores": {"funny": 4, "irony": 4, "voice": 4, "fresh": 3},
        "why": "Numerical escalation is a real joke and the voice is "
               "plain. Slightly wordy, and 'more of the same bug' is a "
               "less specific irony than the winner's inversion.",
    },
    {
        "text": "fix: Tuesday-only bug now happens every day",
        "scores": {"funny": 3, "irony": 4, "voice": 5, "fresh": 4},
        "why": "A wonderfully specific bug (Tuesdays only) that the fix "
               "spread to every day. Great voice, but the laugh depends "
               "on the reader picturing a Tuesday bug at all.",
    },
    {
        "text": "fix: 404 page fixed, every page is now 404",
        "scores": {"funny": 3, "irony": 4, "voice": 4, "fresh": 3},
        "why": "The error page swallowed the whole site: specific and "
               "visual. It leans closest to the banned 'broke "
               "everything' angle, which costs it on freshness.",
    },
]


def total(candidate):
    """Weighted score under the judge's priority order."""
    return sum(
        WEIGHTS[criterion] * score
        for criterion, score in candidate["scores"].items()
    )


def gate(text):
    """The sealed scorer's rule plus criterion 1: 1-100 characters of
    UTF-8 text, not only white space, reading as a one-line commit
    message about a fix that backfired."""
    if not isinstance(text, str):
        return False
    if not text.strip():
        return False
    if len(text) > 100:
        return False
    if "\n" in text or "\r" in text:
        return False
    text.encode("utf-8")  # raises on non-UTF-8-encodable text
    return text.startswith("fix: ")


def main():
    # Score twice from scratch and require the same winner: the
    # grader runs this program twice and compares the action logs,
    # so any nondeterminism must fail loudly here, never silently.
    first = sorted(CANDIDATES, key=total, reverse=True)
    second = sorted(
        [dict(c, scores=dict(c["scores"])) for c in CANDIDATES],
        key=total,
        reverse=True,
    )
    if [c["text"] for c in first] != [c["text"] for c in second]:
        print("nondeterministic ranking", file=sys.stderr)
        return 1
    ranked = first
    for candidate in ranked:
        candidate["total"] = total(candidate)
    winner = ranked[0]
    if not gate(winner["text"]):
        print("winner fails the gate: %r" % winner["text"], file=sys.stderr)
        return 1
    for candidate in ranked:
        print("%2d  %s" % (candidate["total"], candidate["text"]))
    out_dir = os.environ.get("MAKEFUN_OUTPUT", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(winner["text"])
    os.chmod(out_path, 0o644)
    print("wrote %d chars to %s" % (len(winner["text"]), out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
