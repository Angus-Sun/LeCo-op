# LeCoOp

A from-scratch implementation of **LeWorldModel (LeWM)**, a JEPA world model
([arXiv 2603.19312](https://arxiv.org/abs/2603.19312)), applied to the co-op
game *Fireboy and Watergirl*. One world model and one planner control both
characters at once.

Inspired by [Benjamin Bai's LeWM reproduction on Super Mario](https://benjamin-bai.com).

## How it works

- **Watch**: random play (sticky actions, spawns near mechanics) is recorded
  as frames plus a `[2, 4]` button grid per frame (2 players x 4 buttons).
- **Learn**: a vision encoder turns recent frames into frame latents, an
  action encoder turns buttons into action latents. A causal AdaLN transformer
  predictor predicts the next latents, trained with prediction loss + SigReg.
- **Plan**: CEM samples candidate button plans for both players, the frozen
  world model imagines the futures, a cost compares imagined latents to a
  goal-frame latent, the first move executes, then it replans.

## Setup

```
pip install -r requirements.txt
```

This repo does not include the Fireboy and Watergirl game itself — it's not
ours to redistribute. Get it from [TODO: link to source repo] and place it in
`game/` (gitignored).

## Status

Early scaffolding — no trained model yet.
