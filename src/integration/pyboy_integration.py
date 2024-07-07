from dataclasses import dataclass
from typing import Self
from pyboy import PyBoy


def save_initial_state():
    with PyBoy("data/blue.gb", window="null", cgb=True) as pyboy, open("data/state_file.state", "wb") as f:
        pyboy.save_state(f)


def pyboy_tick(button=""):
    valid_buttons = ["a", "b", "up", "down", "left", "right", "start", "select"]

    pyboy = PyBoy("data/blue.gb", window="null", cgb=True)
    pyboy.set_emulation_speed(100)
    try:
        with open("data/state_file.state", "rb") as f:
            pyboy.load_state(f)
    except FileNotFoundError:
        save_initial_state()

    button = button.lower()
    if button in valid_buttons:
        pyboy.button_press(button)
        pyboy.tick(2)
        pyboy.button_release(button)
        pyboy.tick(2)

    pyboy.tick(500)
    pyboy.screen.image.resize((480, 432), 0).save("data/image.png")
    with open("data/state_file.state", "wb") as f:
        pyboy.save_state(f)

    game_info = GameInformation.from_pyboy(pyboy)

    pyboy.stop()

    return game_info


@dataclass
class GameInformation:
    player_name: str

    @classmethod
    def from_pyboy(cls, pyboy) -> Self:
        return GameInformation(
            player_name=pyboy.memory[0x2598:0x2598 + 0xB],
        )

    def as_markdown(self) -> str:
        return f"""
# Game Data

Name: {self.player_name}
"""
