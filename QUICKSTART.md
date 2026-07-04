# Quickstart

A five-minute version for anyone who just wants Claude to help build their own tools — no coding background needed. (The full [README](README.md) has the details when you want them.)

## What this is

A small starter pack you drop into a project folder so Claude **remembers how you like to work** and **stays careful with your files and your code**. You set it up once, then you mostly just talk to Claude normally.

## Get started in 3 steps

1. **Add the kit to your project.** Brand-new or empty project? Copy this folder's contents into it. Already has files (and maybe its own README)? Don't copy over them — instead just tell Claude where this kit is and point it at your project (or run `python install.py`), and it adds its files *without* overwriting your README.
2. **Open the project in Claude Code and say:** `run /setup`
3. **Answer a few short questions.** Claude figures out whether your project is brand new or already has code, then sets itself up to match. Done.

That's it. From here you just describe what you want to build.

## Talk naturally — Claude has helpers for the moments that matter

You don't need to memorize commands. Just say what you're doing, and the right helper kicks in:

- **Starting something new?** Say *"let's plan this"* or *"interview me about this."* Claude asks you one sharp question at a time and turns your idea into a clear, step-by-step plan before any code is written.
- **Wrote something and want it checked?** Say *"review my changes."*
- **Something's broken?** Say *"help me figure out this bug."*
- **Done for the day?** Say *"wrap up"* — Claude tidies up, saves your progress, and notes where to pick up next time.
- **Want an extra safety net on your code history?** Say *"block the dangerous git commands."* Claude will set it up and tell you exactly what changed.
- **Want a written record of a chat?** Say *"save this conversation."*

## About safety

This kit sets Claude up in a **sensible middle ground**, so you get help without either extreme. Out of the box it's more relaxed than Claude's cautious default — the everyday, harmless stuff (reading your files, running tests, building the project) just happens, so you're not stuck clicking "approve" every few seconds for basic things. But it's deliberately *not* the reckless "skip every safety check" mode either: anything risky — deleting files, rewriting your saved history, reaching outside your project folder, or sending code somewhere shared — still stops and asks you first, and a short list of truly dangerous commands is blocked outright. So Claude gets real room to work, but can't quietly delete or damage files elsewhere on your PC.

You approve or decline each prompt as it comes up. And if you ever want an extra hard lock on risky git commands, just ask (see above) — Claude will set it up and tell you exactly what changed and how to undo it.

## When you're curious for more

The [README](README.md) explains every skill, the permission settings, and how Claude learns your project. You never *need* it to get going — it's there for when you want to look under the hood.
