import json
import os
import time
from typing import Callable

from slack_sdk import WebClient
from integration.pyboy_integration import pyboy_tick, run_anarchy_inputs
from state.state_manager import state_manager, save_state


def handle_input(event, say, client: WebClient, post_delete_actions_callback: Callable[[None],None], isAnarchyMode: bool , button="", anarchy_inputs=[]):
    last_message = state_manager.last_message
    if not last_message:
        state_manager.last_message = event["item"]
        last_message = event["item"]

    if isAnarchyMode:
        parsed_anarchy_inputs = [btn.lower().replace("arrow_", "") for btn in anarchy_inputs]
        new_game_info = run_anarchy_inputs(parsed_anarchy_inputs)
        local_image_path = "data/results.gif"
        inputs_to_save = anarchy_inputs
    else: 
        button = button.replace("arrow_", "")
        new_game_info = pyboy_tick(button)
        local_image_path = "data/image.png"
        inputs_to_save = [button]
    
    upload_response = upload_image(client, local_image_path, event["item"]["channel"], isAnarchyMode, button, parsed_anarchy_inputs)

    if upload_response["ok"]:
        delete_last_message(client, last_message)

        post_delete_actions_callback(inputs_to_save)

        time.sleep(3)
        last_message = say("Vote for the next input:")
        state_manager.last_message = last_message

        save_state(state_manager)

        if new_game_info != state_manager.game_info:
            state_manager.game_info = new_game_info
            ensure_canvas_exists(client, last_message["channel"])
            update_canvas_with_game_info(client, state_manager.game_info)

        if "ts" in last_message:
            add_reactions(client, last_message["ts"], event["item"]["channel"])


def upload_image(client, local_image_path, channel, isAnarchyMode: bool, button="", anarchy_inputs=[]):
    message = f"Inputs provided: {anarchy_inputs}" if isAnarchyMode else f"Winning input: {button if button else 'None'}"
        
    return client.files_upload_v2(
    file=local_image_path,
    title=message,
    channel=channel
    )


def delete_last_message(client, last_message):
    try:
        client.chat_delete(channel=last_message["channel"], ts=last_message["ts"])
    except:
        print("Error deleting")


def add_reactions(client, timestamp, channel):
    reacts = json.loads(os.getenv("VALID_REACTIONS"))
    for emoji in reacts:
        client.reactions_add(
            channel=channel,
            name=emoji,
            timestamp=timestamp
        )


def calculate_reactions(client, say, event):
    last_message = state_manager.last_message
    if not last_message:
        state_manager.last_message = event["item"]
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


def ensure_canvas_exists(client: WebClient, channel_id):
    if state_manager.canvas is not None:
        return state_manager.canvas

    response = client.conversations_info(channel=channel_id).validate()

    try:
        canvas_id = response["channel"]["properties"]["canvas"]["file_id"]
    except:
        # Canvas doesn't exist. Create it
        create_canvas_response = client.conversations_canvases_create(channel_id=channel_id).validate()
        canvas_id = create_canvas_response["canvas_id"]

    state_manager.canvas = canvas_id


def update_canvas_with_game_info(client: WebClient, game_info):
    client.canvases_edit(
        canvas_id=state_manager.canvas,
        changes=[{
            "operation": "replace",
            "document_content": {
                "type": "markdown",
                "markdown": game_info.as_markdown()
            }
        }]
    )
