# 18: Verify your lab

## What you will build

Nothing new: this is where you prove everything from guides 02 to 17 actually works together.

## Why

A lab you have not checked end to end is a guess. This is the same discipline the security loop asks of you
later: measure, don't assume.

## Steps

```bash
cd lab
make verify
```

Each line is `PASS`, `FAIL` or `SKIP`. `SKIP` is normal for an optional part you did not build (Windows 11,
a Wi-Fi access point). Any `FAIL` is something to fix before you move on.

## Check it worked

The summary line reads `N passed, 0 failed, M skipped`.

## If it goes wrong

- Each check's message says what it expected and usually which guide to re-read. Run one check at a time
  with `./verify/verify.sh --only NAME` while you fix things.
- `20-weak-defaults` failing is actually useful information: it means something was hardened before the
  baseline measurement in the security weeks. If you did that on purpose, note it; if not, you may want to
  rebuild that guest.

You now have a complete, working "business in a box". The security loop (measure, harden, re-measure) starts
from here.
