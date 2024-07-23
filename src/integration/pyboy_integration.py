import os

import imageio
from pyboy import PyBoy

from integration.gen_1_pokemon import GameInformation


def is_battle_happening(pyboy: PyBoy):
    return pyboy.memory[0xD057] != 0


def save_initial_state():
    with PyBoy("data/blue.gb", window="null", cgb=True) as pyboy, open(
        "data/state_file.state", "wb"
    ) as f:
        pyboy.save_state(f)


def pyboy_tick(button=""):
    valid_buttons = ["a", "b", "up", "down", "left", "right", "start", "select"]

    pyboy = PyBoy("data/blue.gb", window="null", cgb=True)

    print(is_battle_happening(pyboy))

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


def run_anarchy_inputs(inputs: list[str]):
    valid_buttons = ["a", "b", "up", "down", "left", "right", "start", "select"]

    pyboy = PyBoy("data/blue.gb", window="null", cgb=True)
    pyboy.set_emulation_speed(100)

    try:
        with open("data/state_file.state", "rb") as f:
            pyboy.load_state(f)
    except FileNotFoundError:
        save_initial_state()

    for i, button in enumerate(inputs):
        if button in valid_buttons:
            pyboy.button_press(button)
            pyboy.tick(2)
            pyboy.button_release(button)
            pyboy.tick(2)
        pyboy.tick(200)
        pyboy.screen.image.resize((480, 432), 0).save(
            f"data/gif/image-{str(i).zfill(3)}.png"
        )

    gif_image_filenames = [
        os.path.join(dirpath, f)
        for (dirpath, dirnames, filenames) in os.walk("data/gif")
        for f in filenames
    ]
    print(gif_image_filenames)
    images = []
    for filename in gif_image_filenames:
        images.append(imageio.imread(filename))
        os.remove(filename)

    imageio.mimsave("data/results.gif", images, fps=2)

    with open("data/state_file.state", "wb") as f:
        pyboy.save_state(f)

    game_info = GameInformation.from_pyboy(pyboy)

    pyboy.stop()

    return game_info
