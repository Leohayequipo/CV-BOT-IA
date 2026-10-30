---
id: example-project          # kebab-case, unique; reuse the profile.yaml id when the project has one
title: Example project
related: [utn]               # ids from profile.yaml (experience or projects) this case study belongs to
period: "2026"               # "YYYY", or "YYYY-MM/YYYY-MM" for a range
role: Lead developer         # Leonardo's role in this project
stack: [Python, FastAPI, LangGraph]
lang: en
---

<!--
How to write a case study

- Everything in this file is public and the assistant can quote any sentence of it. Write only what
  can be shared: no client names the profile doesn't already name, no internal data, no code under NDA.
- Write about Leonardo in the third person ("Leonardo designed...").
- Facts only. If something wasn't measured, describe the outcome without inventing a number.
- Each section becomes one retrievable chunk, so every section must make sense on its own:
  name the project again instead of writing "it" or "this system".
- Required sections: Summary, Context and problem, Leonardo's role, Architecture,
  Key decisions and trade-offs, Results. The content validation test checks them.
- Delete this comment in a real case study.
-->

# Example project

## Summary

Two or three sentences: what it is, who it is for and the main result.

## Context and problem

Who needed it and why. What made it hard or important.

## Leonardo's role

What he owned, decided and built. Team size and who he worked with, if relevant.

## Architecture

How it works, as a short walkthrough from input to output. A text diagram is welcome.

## Key decisions and trade-offs

Two to four decisions: what was chosen, over what, and why. What was given up in exchange.

## Challenges

The hardest problems and how they were solved.

## Results

Measured outcomes first (numbers, users, time saved), then qualitative ones.

## Lessons learned

What he would do differently next time.
