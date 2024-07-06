# Slack Plays Pokemon

### A dumb idea spawned during a totally unrelated hackathon

## System Requirements

SlackPlaysPokémon uses poetry for Python to create an isolated environment and manage package dependencies.
Before continuing, ensure you have installed Python version 3.12 or above.

### Poetry installation (Bash)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Poetry installation (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

You can check poetry is installed by running `poetry --version` from a terminal.

## Dependencies

The project uses a virtual environment to isolate package dependencies. To create the virtual environment and install required packages, run the following from your preferred shell:

```bash
$ poetry install
```

## Slack App
SlackPlaysPokémon is a Python Bolt app.
Create a Slack app with the appropriate read/write permissions, then add the `xoxb` and `xapp` tokens to the appropriate environment variables in the `.env` file.

## Emulation
This project emulates Pokémon Blue (and possibly supports Pokémon Red unofficially). You will need your own legally dumped cartridge as a `.gb` file in the root of the project to run it.

## Acknowledgements
- [PyBoy](https://github.com/Baekalfen/PyBoy) - Used to emulate a headless Gameboy and store the game state
- [bolt-python](https://github.com/slackapi/bolt-python) - A Python framework used to easily build Slack apps
