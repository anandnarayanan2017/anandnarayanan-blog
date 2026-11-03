# A Prompt Is Not a Specification

<!--
DRAFT, not published. To publish: move this file to docs/blog/posts/, add a
"2" date and a "2" excerpt to docs/blog/series.json, and add a hero image as
docs/blog/images/02-a-prompt-is-not-a-specification-1.png.
Suggested excerpt: "A prompt describes what to build. A specification also
says what must never happen. Turning “Build a booking API” into four testable
invariants, and why the fourth sentence mattered most."
-->

In Part 1, I typed “Build a booking API” and called it a wish.

A few readers asked the fair follow-up question: then what should I have typed?

Not a longer prompt. A longer prompt is still a wish, only with better manners.

## What the prompt left out

Here is everything “Build a booking API” says about double bookings:

Nothing.

I never wrote that two people can’t have the same room at the same time. I didn’t need to. Every human who has fought over a meeting room knows it. That is exactly the problem: the rules everyone knows are the rules nobody writes down.

When I listed what I actually meant, the list looked like this:

- Two confirmed bookings for the same room must never overlap.
- A cancelled booking frees the slot.
- The same hour in a different room is not a conflict.
- Back-to-back bookings, one ending at 10:00 and the next starting at 10:00, are fine.
- When twenty people press “Book” at the same moment, exactly one wins.

None of these are features. They are **invariants**: statements that must stay true after every request, in any order, under any load, whoever wrote the code.

That distinction matters more with an agent than with a colleague. Agents are very good at building features. A prompt says what to build. It rarely says what must never happen, and an agent cannot reliably guess the rules you only carry in your head.

Ambiguity in a prompt isn’t harmless. It’s a decision you delegated without noticing.

## Three questions per invariant

For each rule, I now ask three questions before an agent writes a line of code.

**1. What must always be true?** One sentence, no “should”, no “ideally”.

> No two confirmed bookings for the same room may overlap in time.

**2. Who enforces it?** The application, the database, or both?

> The database.

**3. What evidence would prove it?** A check that fails if the rule is broken.

> Twenty simultaneous requests for one slot produce exactly one HTTP 201 and nineteen HTTP 409s, and the database holds exactly one confirmed booking.

The second question is the one people skip. It turned out to be the one that mattered.

## The sentence that did the work

The first attempt at concurrency safety looked careful. Open a transaction. Check whether the slot is taken. If it is free, insert the booking. Commit.

Read it in a code review and it looks right. An AI reviewer read it and scored it 9 out of 10.

It isn’t right. In PostgreSQL’s default isolation level, Read Committed, one transaction can’t see another’s booking until that booking is committed. Twenty requests arrive together, all twenty check, all twenty find the slot free, and then they all insert. The transaction makes each request consistent with itself, not with the other nineteen.

The twenty-request test caught it: ten bookings for the same room and the same hour. The failure went back to the agent, and the second attempt passed.

What it changed is the point of this part. The fix wasn’t smarter application code. It was moving the rule to where the invariant said it belonged, into the database:

```sql
ALTER TABLE bookings
  ADD CONSTRAINT bookings_no_overlap
  EXCLUDE USING gist (room_id WITH =, tstzrange(start_at, end_at) WITH &&)
  WHERE (status = 'confirmed');
```

Read it as English: for the same room, no two confirmed time ranges may overlap. The database now refuses the second booking, however many requests arrive and whoever writes the next version of the API. The application turns that refusal into an HTTP 409.

“The database enforces the rule” looked like a detail in the specification. It was the most important clause in it.

## The specification is the tests

I didn’t keep these invariants in a document. Each one is a test that runs on every change:

| Invariant | Test |
|---|---|
| Exactly one of twenty simultaneous requests wins | `exactly one of 20 simultaneous requests for the same slot wins` |
| The database itself rejects overlaps, and back-to-back is fine | `the database itself rejects overlapping confirmed bookings (SQLSTATE 23P01)` |
| A cancelled booking frees the slot | `cancelled bookings do not block the slot, even at the database level` |
| The same slot in another room is not a conflict | `the same slot in different rooms is not a conflict` |

Notice the second test. It skips the API and inserts an overlapping row directly with SQL. If someone adds a batch import next year, or an agent writes a new endpoint that forgets the check, the database still says no. The test proves the rule lives where I said it lives, not only that today’s code happens to respect it.

A document can say “bookings must not overlap”. Only a test can fail when they do.

## What I hand an agent now

Not a forty-page document. This isn’t a return to waterfall. It is a few sentences that would hurt if they were wrong:

```text
Intent:      Users book meeting rooms by the hour.
Invariants:  No two confirmed bookings for a room overlap (enforced by the database).
             Cancelled bookings free the slot. Back-to-back bookings are allowed.
Failure:     A clash returns HTTP 409 and changes nothing.
Evidence:    20 simultaneous requests for one slot: one 201, nineteen 409s,
             one row in the database. Tests run in CI on every change.
```

Writing that took me less time than reviewing the first attempt. And it changes what the agent is doing: instead of guessing what “correct” means, it is working towards a check that will tell it.

## Where this stops working

Invariants are not free, and they don’t cover everything.

- **They only cover the rules you thought of.** A specification with four invariants protects four things. It says nothing about the fifth.
- **Some rules don’t fit in a database constraint.** “A user may hold at most three bookings a week” needs a different design, and that is a design decision, not a prompt tweak.
- **A test can encode the wrong rule.** If I had written “at least one request succeeds”, the broken version would have passed. Specifications need review too.

That last point leads to the next part. A specification tells the agent what “correct” means. Something still has to give the agent the context, the tools and the feedback loop to get there, and decide what happens when a check fails. That is the harness.

**Next: Part 3, The Harness Around the Agent.**

What is one rule in your system that everyone knows and nobody has written down? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **The code:** [examples/double-booking](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc/examples/double-booking): the four tests, the check-then-insert first attempt, the exclusion constraint, and the run log behind “ten times”. It runs in CI on every change.
- **Why the transaction didn’t help:** PostgreSQL documentation, [Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html), on what Read Committed does and doesn’t protect against.
- **The constraint:** PostgreSQL documentation, [Exclusion constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION).
- **Write skew, with meeting rooms:** Martin Kleppmann, *Designing Data-Intensive Applications* (O’Reilly), chapter on transactions.
- **Invariants and contracts:** Bertrand Meyer, *Object-Oriented Software Construction*, 2nd edition (Prentice Hall, 1997), on design by contract.
