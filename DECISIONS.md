# Decisions

One line per design decision, with why.

- Folder layout: flat `lecoop/{watch,learn,plan,data}` package + `scripts/` entry points. Why: simplest to navigate for a solo project, no packaging boilerplate needed.
- Dependency management: pip + `requirements.txt`. Why: standard, zero extra tooling to learn.
