from pyboy import PyBoy

pyboy = PyBoy("../../data/blue.gb", cgb=True)
pyboy.set_emulation_speed(1000)

with open("playback_state.state", "rb") as f:
    pyboy.load_state(f)

btns = [btn.strip().split(",")[1].replace("arrow_", "") for btn in open("inputs.csv").readlines()][1:]

for btn in btns:
    if btn != "":
        pyboy.button_press(btn)
        pyboy.tick(2)
        pyboy.button_release(btn)
        pyboy.tick(2)
        for x in range(500):
            pyboy.tick()
    else:
        for x in range(500):
            pyboy.tick()