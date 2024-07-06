import os
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

    local_image_path = "image.png"
    client.files_upload_v2(
        file=local_image_path,
        title="pokemon_screenshot",
        initial_comment="Here is the next image",
        channels=event["channel"]
    )


def pyboy_tick():
    with PyBoy("blue.gb", window="null") as pyboy:
        pyboy.set_emulation_speed(100)
        with open("state_file.state", "rb") as f:
            pyboy.load_state(f)
        pyboy.tick(500)
        pyboy.screen.image.save("image.png")
        with open("state_file.state", "wb") as f:
            pyboy.save_state(f)


if __name__ == "__main__":
    main()
