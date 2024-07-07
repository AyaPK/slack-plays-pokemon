import os
import re
import time

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from pyboy import PyBoy

load_dotenv()
app = App(token=os.getenv('SLACK_TOKEN'))
last_message = None


def main():
    save_initial_state()
    start_slack_bot()


def save_initial_state():
    with PyBoy("blue.gb") as pyboy, open("state_file.state", "wb") as f:
        pyboy.save_state(f)


def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_XAPP")).start()
    handler.start()


@app.event("reaction_added")
def handle_input(event, say, client):
    global last_message

    if not last_message:
        last_message = event["item"]

    button = event["reaction"].replace("arrow_", "")
    pyboy_tick(button)

    local_image_path = "image.png"
    response = client.files_upload_v2(
        file=local_image_path,
        title="pokemon_screenshot",
        channel=event["item"]["channel"]
    )

    if response["ok"]:
        client.chat_delete(channel=last_message["channel"], ts=last_message["ts"])
        time.sleep(3)
        last_message = say("Select the next input:")

        if "ts" in last_message:
            reacts = ["arrow_up", "arrow_down", "arrow_left", "arrow_right", "a", "b"]
            timestamp = last_message["ts"]
            for emoji in reacts:
                client.reactions_add(
                    channel=event["item"]["channel"],
                    name=emoji,
                    timestamp=timestamp
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
    pyboy.screen.image.resize((480, 432), 0).save("image.png")
    with open("state_file.state", "wb") as f:
        pyboy.save_state(f)
    pyboy.stop()


if __name__ == "__main__":
    main()
