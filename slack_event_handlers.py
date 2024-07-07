import time
from pyboy_integration import pyboy_tick
from state_manager import state_manager


def handle_input(event, say, client):
    last_message = state_manager.get_last_message()

    if not last_message:
        state_manager.set_last_message(event["item"])
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
        state_manager.set_last_message(say("Select the next input:"))
        last_message = state_manager.get_last_message()

        if "ts" in last_message:
            reacts = ["arrow_up", "arrow_down", "arrow_left", "arrow_right", "a", "b"]
            timestamp = last_message["ts"]
            for emoji in reacts:
                client.reactions_add(
                    channel=event["item"]["channel"],
                    name=emoji,
                    timestamp=timestamp
                )
