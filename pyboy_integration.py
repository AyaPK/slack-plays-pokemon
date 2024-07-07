from pyboy import PyBoy


def save_initial_state():
    with PyBoy("blue.gb", window="null", cgb=True) as pyboy, open("state_file.state", "wb") as f:
        pyboy.save_state(f)


def pyboy_tick(button=""):
    valid_buttons = ["a", "b", "up", "down", "left", "right", "start", "select"]

    pyboy = PyBoy("blue.gb", window="null", cgb=True)
    pyboy.set_emulation_speed(100)
    try:
        with open("state_file.state", "rb") as f:
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
    pyboy.screen.image.resize((480, 432), 0).save("image.png")
    with open("state_file.state", "wb") as f:
        pyboy.save_state(f)
    pyboy.stop()
