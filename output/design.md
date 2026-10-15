# Dashboard Design — Problem 8

What I chose for the Campus Customs dashboard look, and why. Code lives in `frontend/src/`.

## Overall feel

Yale blue (`#00356b`) and a warm gold accent (`#f4c542`) over a soft off-white
gradient background, with a serif display face (Fraunces) for headings
against a clean sans (Inter) for everything else. The goal was a desk that
reads as *institutional and trustworthy* (it's handling real money) but not
sterile — the gold accent, the floating "CC" brand mark, and the animation
throughout are what keep it from feeling like a plain admin panel.

## Layout

Two columns: a fixed-width **Board** on the left (the 3 tickets, always
visible) and a wider **Stage** on the right (the team + live feed +
results). This mirrors how a real desk works — the inbox stays put while
you focus on one case at a time — and keeps the single most important rule
(pick exactly one ticket) spatially obvious: there's only one stage, so
only one ticket can be "on" it.

## How agents read differently

Each of the 5 agents gets its own color and glyph (BOSS ♛ navy, INVENTORY ▣
green, ACCOUNTING $ amber, FACILITIES ⌂ purple, CUSTOMER SERVICE ✉ rose) —
chosen so they're distinguishable at a glance without reading labels, the
way you'd recognize teammates by their jacket color. An agent's avatar
starts dimmed (55% opacity) and *lights up* the first time it speaks during
a run, then stays lit for the rest of that run — so at any moment you can
see who's been involved just from the avatar row, before reading a single
line of the feed. Whoever spoke most recently gets a scale-up, a colored
glow ring, a "breathing" pulse on its glyph, and an expanding ripple ring —
a quiet but readable "this one's talking right now" signal, since there's
no audio/video to carry that otherwise.

Below the avatars, a live feed streams in (polling `/events` every 1.2s
while a run is active) as colored bubbles — left border and small circular
avatar in that agent's color, the agent's name, which delegation hop it
came from, what it said, and chips for each MCP tool it called. New bubbles
slide in from the left rather than just appearing, so the feed reads as
something *happening* rather than a static log dump.

## How resolved tickets show up

Each ticket card gets an outcome badge once its run finishes: green
"Resolved", amber "Not Resolved" (with the `partial_fulfillment_note`
shown below the feed), or red "Needs Approval" if a payment is pending —
color alone tells you the state of all 3 tickets from the board at a
glance. The result panel underneath the stage pops in with a rise-and-fade
animation rather than snapping into place, so a finished run feels like it
*arrived* rather than that the page silently changed under you.

One deliberate, slightly unusual choice: if BOSS reports a ticket resolved
but the ticket's own status (re-fetched from `/tickets` after the run) is
still unresolved (`open` or `partial`; corrected in Problem 9, see below) — meaning no one actually marked it resolved — the
panel shows a visible mismatch warning instead of trusting the agent's
claim. This is the dashboard applying the same "never invent, always
verify" rule the agents are held to, back onto the agents themselves. It's
a small thing, but it's the kind of detail that makes the tool feel honest
rather than just decorative.

*Note added in Problem 9 (the text above is otherwise unchanged):* the result panel now also has a "What each agent did" list, with each agent's last statement and the tools it used in that run. That covers the "short summary of what each agent did" requirement directly, instead of leaving it to the live feed. Separately, `partial` tickets now count as open (`is_open: true`). Before, they showed as closed even though they were still unresolved.

## How cash shows up

The balance in the header counts up or down with an eased animation
instead of jumping to the new number, and the whole meter gets a warm gold
highlight for a moment while it's dropping — so an approved payment has a
visible, satisfying "the money just moved" beat instead of a silent number
change you might miss. The approval card itself (gold border, glowing
outline) is the most visually prominent element on the page when it
appears, on purpose: this is the one moment a human's input is legally and
narratively required, and the UI should make that impossible to scroll
past. Typing a name is required before the Approve button even becomes
clickable — a lightweight stand-in for a real signature, directly matching
Shop Rule 4.

## Why this should be enjoyable to actually use

The combination of color-coded "characters," the lit-up/pulsing avatars,
the sliding feed, and the count-up cash meter turns an otherwise invisible
process (a backend making tool calls) into something you can *watch* and
read at a glance without parsing text — closer to watching a scoreboard
than reading a log file. The honesty touches (the mismatch flag, the
explicit partial-fulfillment notes, the exact dollar amount and account on
every approval) are what should make someone trust sitting at this desk
for real, not just like how it looks.
