# DELEGATION.md

Decision per action: **alone** (the agent acts and reports afterwards) or **approval** (the agent asks first and acts only after a yes).

## Classification

| # | Action | Decision | Justification |
|---|--------|----------|---------------|
| 1 | Read the appointments of a day | alone | Read-only, no side effects, and nearly every task needs it first. In cards A and B, asking would only have slowed things down. |
| 2 | Look up the weather | alone | Read-only, harmless, nothing to undo. Card D needed no question. |
| 3 | Search train connections | alone | Read-only and free. Searching is not committing: the choice and the booking come afterwards. |
| 4 | Read notes | alone | Read-only on my own data, needed to give good answers (card F: the stand-up note and the badge pickup time were useful). Reading changes nothing. |
| 5 | Create a personal block in the calendar (e.g. travel time, no other attendees) | approval | It writes to my calendar. Even though it only affects me, it changes my data and the agent may choose the wrong time or title. Asking first is cheap, and I decide by the type of action: only reading is done alone. |
| 6 | Reschedule an appointment with other attendees | approval | Changes other people's calendars and plans. The agent cannot know the reasons behind the appointment or what the others would accept. |
| 7 | Book a train ticket | approval | Spends my money and may cost a cancellation fee. In card C the agent booked directly because only one connection fit, and the person said that was wrong for a real situation. |
| 8 | Send a message to third parties | approval | Cannot be taken back and speaks in my name. The agent should show the draft (text and recipient) first, as in card E. |
| 9 | Create a note | approval | It writes to my notes. It is harmless and additive, but the agent would add content to my own data that I have not seen. Every writing action gets the same rule, so I do not have to judge the risk case by case. |
| 10 | Delete a note | approval | Irreversible loss of my own information. The agent cannot judge what is still valuable to me (card F). |

## My rule in one sentence

The agent acts alone only when an action just reads; it asks first for every action that writes, whether it changes my data, spends my money or involves other people.

## Observations from the role play

1. **Message sent without a draft (cards B/C, then E).** The agent sent the stand-up message right away with its own wording and an inferred recipient (the channel, read from a note). The person wanted to check it first, rewrote the text, and the first message could not be withdrawn, so a duplicate stayed in the channel. When replayed with a draft first (card E), the cost was one extra turn and the person kept control. This is why action 8 is approval.
2. **Inconsistent behaviour on bookings (cards B vs. C).** On the way there, the agent asked before booking. On the way back, it booked directly because only one connection fit. The person noted that in a real situation it should have asked both times, since booking spends money. Whether the agent asks must not depend on how obvious the choice seems, so it is a fixed rule (action 7).
3. **The agent needed context it did not have.** It had to infer who "the others" in the stand-up are from a note. It also did not know the travel time from the station to Werk 2, and with a 15-minute badge pickup (workshop note) the 29-minute buffer for the ICE 598 was tighter than it looked.
4. **Reading before asking found problems.** Reading notes and calendar revealed that the stand-up note says Wednesday while the day is a Thursday and the calendar lists it. These are cheap read-only steps that make later questions better, which is why actions 1 to 4 are alone.
5. **Vague or destructive requests need a question (card F).** "Tidy up my notes" is ambiguous, and its destructive part (deleting) cannot be undone, so the agent asked instead of acting. The person also wanted the raw note contents, not a summary, before deciding, because the notes are their own data.
