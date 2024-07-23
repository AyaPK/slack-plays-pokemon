import csv
import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import errors

from bot.slack_event_handlers import calculate_reactions, handle_input
from state.state_manager import state_manager

load_dotenv()

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_XAPP = os.getenv("SLACK_XAPP")
VALID_REACTIONS = os.getenv("VALID_REACTIONS")

if not SLACK_TOKEN or not SLACK_XAPP or not VALID_REACTIONS:
    raise ValueError("Missing necessary environment variables.")

app = App(token=SLACK_TOKEN)

TIMER_DURATION = 15
timer_active = False
reactions_dict = {}
inputs_to_save = []


def start_slack_bot():
    handler = SocketModeHandler(app, SLACK_XAPP)
    handler.start()


@app.event("reaction_added")
def handle_reaction_added(event, say, client):
    global timer_active
    global reactions_dict

    if (
        state_manager.last_message
        and event["item"]["ts"] != state_manager.last_message["ts"]
    ):
        return

    reaction = event.get("reaction")
    if reaction not in json.loads(VALID_REACTIONS):
        return

    user = event.get("user")
    if user not in reactions_dict.keys():
        reactions_dict[f"{user}-{len(reactions_dict)}"] = (
            event.get("event_ts"),
            reaction,
        )

    if not timer_active:
        start_timer(client, say, event, isAnarchyMode())


def start_timer(client, say, event, anarchy_mode_active):
    global reactions_dict
    global timer_active
    global inputs_to_save

    timer_active = True

    print(f"{TIMER_DURATION} second timer started...")
    time.sleep(TIMER_DURATION)
    print(f"{TIMER_DURATION} second timer complete!")

    if anarchy_mode_active:
        try:
            print("Anarchy mode is active")
            handle_input(
                event,
                say,
                client,
                post_delete_actions_callback,
                True,
                anarchy_inputs=convert_reactions_dict_to_input_list(reactions_dict),
            )
        except errors.SlackApiError as e:
            print(e)

    else:
        button = calculate_reactions(client, say, event)
        try:
            handle_input(
                event, say, client, post_delete_actions_callback, False, button
            )
        except errors.SlackApiError as e:
            print(e)

    post_cycle_actions(inputs_to_save, anarchy_mode_active)


def post_delete_actions_callback(reactions_to_save: list[str]):
    global timer_active
    global reactions_dict
    global inputs_to_save

    timer_active = False
    inputs_to_save = reactions_to_save
    reactions_dict = {}


def convert_reactions_dict_to_input_list(reactions: dict):
    sorted_values = sorted(reactions.values(), key=lambda x: x[0])

    return [t[1] for t in sorted_values]


def post_cycle_actions(inputs_to_save: list[str], anarchy_mode_active: bool):
    write_inputs_to_file(inputs_to_save, anarchy_mode_active)


def write_inputs_to_file(inputs_to_save: list[str], anarchy_mode_active: bool):
    if os.path.exists("data/inputs.csv"):
        with open("data/inputs.csv", "r", newline="") as file:
            reader = csv.reader(file)
            row_count = sum(1 for row in reader) - 1

    with open("data/inputs.csv", "a", newline="") as file:
        writer = csv.writer(file)
        for index, button in enumerate(inputs_to_save):
            writer.writerow(
                [row_count + index, button, 200 if anarchy_mode_active else 500]
            )


def isAnarchyMode():
    utc_dt = datetime.now()
    local_dt = utc_dt.astimezone()
    return (
        local_dt.weekday() == 4 and local_dt.hour >= 13 and local_dt.hour <= 18
    )  # anarchy mode is Friday between 1pm and 6pm
