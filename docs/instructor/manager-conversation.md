# Instructor guide: the manager conversation

Twice in the course, the student explains their findings to "the business" (you), in a short, plain-language
conversation. No technical terms. The point is not to re-test their technical skill — that is what the
reports already show — it is to test whether a non-technical decision-maker could act on what they heard.

## When it happens

1. **After the baseline attack** (the first time they run `sslab attack` and `sslab audit` with
   `--label default`): what did you find, and why does it matter?
2. **After the second attack**, once hardened: what changed, what is still open, and what would you (as the
   business) decide to do about it?

## How to run it

Ten minutes is usually enough. Play a time-pressed small-business owner: you care about money, customers,
downtime and legal duties, not protocols or CVEs. If the student uses a technical term, stop them and ask
"what does that mean for me?"

Ask from their own impact table (`python -m sslab impact ...`), not from the raw findings: it forces them to
have already translated the finding before the conversation starts.

## Scenario cards (pick one per class, or assign by student)

1. **The reception computer.** "A customer says someone emailed them pretending to be us. Is that something
   that came from here?"
2. **The slow afternoon.** "Our file share was unreachable for twenty minutes yesterday. What happened, and
   could it happen again?"
3. **The competitor.** "A rival business seems to know things about our clients they shouldn't. Could that
   have come from us?"
4. **The insurance form.** "Our insurer is asking what security controls we have. What do I tell them?"

## Questions you might ask

- "In one sentence, what's the worst thing that could happen because of this?"
- "What would it cost us if it did?"
- "What do you want me to approve, and what does it cost?"
- (Second conversation) "You closed some of these. What's still open, and why haven't you closed it?"

## What a good answer sounds like

"Right now, anyone on our network could read the SSH sign-in logs or get into unlocked parts of the file
share without a password. If that got out, a customer could lose trust in us, and we could be in breach of
our contract with [client]. Locking it down costs a bit of extra setup time and means staff need to log in
properly in future — I think that's worth it."

A technical answer that never says what the business loses, or an answer that cannot explain why a control
was skipped, has not done this task.

## Related

- [Measure, harden, re-measure design](../design/lab-build-design.md#the-security-report-and-the-manager-conversation)
- `portfolio/templates/manager-briefing.md` (the student's one-page note, written before the conversation)
- `python -m sslab impact` (the blank impact table the student fills in first)
