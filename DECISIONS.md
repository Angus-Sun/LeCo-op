# Decisions

One line per design decision, with why.

This is just a log of every design decision I decided to make while building this out (so I actually think about my decisions before making them :D)

- Folder layout: flat `lecoop/{watch,learn,plan,data}` package + `scripts/` entry points. Why: simplest to navigate for a solo project, no packaging boilerplate needed.
- Dependency management: pip + `requirements.txt`. Why: standard, zero extra tooling to learn.
- Episode-end detection (`lecoop/watch/detect.py`) uses a brightness threshold on the center crop of the frame. Why: calibrated against real win/death/gameplay screenshots (overlay ~140 brightness vs. ~45 gameplay); simpler and more robust than digging for an undocumented state hook in the game's bundled JS. (Scoped only to forest temple subject to change in future)
- Watch's spawn logic will mix level-entrance spawns with spawn-near-mechanic spawns (toxic pool, switches, doors), instead of always spawning at the entrance. Why: the planner can only avoid a hazard if the world model learned its consequence from data which requires random play to actually encounter that hazard often enough
