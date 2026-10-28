# QuantBank

A local PyQt6 desktop application for organizing quantitative interview practice.

## Features

- Add and edit questions, tags, sources, notes, and Python/C++ solution text.
- Practice by category, save questions, and track attempts and correct answers.
- Play a timed block-rearrangement game and review session scores.

`main.py` connects the pages in `ui/`. `logic/data_manager.py` stores questions and progress in local JSON files.

## Run from source

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install PyQt6
python main.py
```

On Windows, activate with `.venv\Scripts\activate`. These are source-derived setup steps; the GUI was not launched as part of this documentation review.

## Data and limitations

`quant_problems.json` contains questions and per-question practice state. `game_stats.json` stores game history. Editing or practicing can modify these files; use a local copy for personal progress.

This is a single-user local app. No learning-outcome benchmark is claimed. The tracked question collection needs a source and redistribution-rights review. The repository also contains generated Windows packaging artifacts; source review does not validate those binaries.
