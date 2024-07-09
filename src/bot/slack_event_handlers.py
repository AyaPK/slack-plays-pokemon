import json
import os
import time
from integration.pyboy_integration import pyboy_tick
from state.state_manager import state_manager, save_state


def handle_input(event, say, client, button):
    last_message = state_manager.get_last_message()
    if not last_message:
        state_manager.set_last_message(event["item"])
        last_message = event["item"]

    button = button.replace("arrow_", "")
    pyboy_tick(button)
    local_image_path = "data/image.png"
    upload_response = upload_image(client, local_image_path, button, event["item"]["channel"])

    if upload_response["ok"]:
        delete_last_message(client, last_message)
        time.sleep(3)
        new_message = say("Vote for the next input:")
        state_manager.set_last_message(new_message)
        last_message = state_manager.get_last_message()

        if "ts" in last_message:
            add_reactions(client, last_message["ts"], event["item"]["channel"])

        save_state(state_manager)


def upload_image(client, local_image_path, button, channel):
    return client.files_upload_v2(
        file=local_image_path,
        title=f"Winning input: {button if button else 'None'}",
        channel=channel
    )


def delete_last_message(client, last_message):
    client.chat_delete(channel=last_message["channel"], ts=last_message["ts"])


def add_reactions(client, timestamp, channel):
    reacts = json.loads(os.getenv("VALID_REACTIONS"))
    for emoji in reacts:
        client.reactions_add(
            channel=channel,
            name=emoji,
            timestamp=timestamp
        )


def calculate_reactions(client, say, event):
    last_message = state_manager.get_last_message()
    if not last_message:
        state_manager.set_last_message(event["item"])
        last_message = event["item"]

    response = client.reactions_get(channel=last_message["channel"], timestamp=last_message["ts"])

    reactions = response["message"]["reactions"]
    reaction_counts = {}

    for reaction in reactions:
        emoji = reaction["name"]
        count = reaction["count"]
        if count > 1 and emoji in json.loads(os.getenv('VALID_REACTIONS')):
            reaction_counts[emoji] = count - 1

    try:
        winning_input = max(reaction_counts, key=lambda k: (reaction_counts[k], -get_priority(k)))
    except ValueError:
        return ""

    return winning_input


def get_priority(key):
    priority_order = ['b', 'a', 'arrow_down', 'arrow_up', 'arrow_left', 'arrow_right', 'start', 'select']
    try:
        return priority_order.index(key)
    except ValueError:
        return ""
