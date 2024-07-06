import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from pyboy import PyBoy

load_dotenv()
app = App(token=os.getenv('SLACK_TOKEN'))


def main():
    save_initial_state()
    start_slack_bot()


def save_initial_state():
    with PyBoy("blue.gb") as pyboy, open("state_file.state", "wb") as f:
        pyboy.save_state(f)


def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_XAPP")).start()
    handler.start()


@app.event("app_mention")
def respond_to_mention(event, say, client):
    pyboy_tick()
    button = re.sub(r'<@\w+>', '', event["text"]).strip()
    pyboy_tick(button)

    local_image_path = "image.png"
    client.files_upload_v2(
        file=local_image_path,
        title="pokemon_screenshot",
        initial_comment="Here is the next image",
        channel=event["channel"]
    )


def pyboy_tick(button=""):
    valid_buttons = ["a", "b", "up", "down", "left", "right", "start", "select"]

    pyboy = PyBoy("blue.gb", window="null")
    pyboy.set_emulation_speed(100)
    with open("state_file.state", "rb") as f:
        pyboy.load_state(f)

    button = button.lower()
    if button in valid_buttons:
        pyboy.button_press(button)
        pyboy.tick(2)
        pyboy.button_release(button)
        pyboy.tick(2)

    pyboy.tick(500)
    pyboy.screen.image.save("image.png")
    with open("state_file.state", "wb") as f:
        pyboy.save_state(f)
    pyboy.stop()


if __name__ == "__main__":
    main()
