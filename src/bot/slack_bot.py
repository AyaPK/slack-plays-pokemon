import csv
import json
import os
import time

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


def start_slack_bot():
    handler = SocketModeHandler(app, SLACK_XAPP)
    handler.start()


@app.event("reaction_added")
def handle_reaction_added(event, say, client):
    global timer_active

    if (
        state_manager.last_message
        and event["item"]["ts"] != state_manager.last_message["ts"]
    ):
        return

    reaction = event.get("reaction")
    if reaction not in json.loads(VALID_REACTIONS):
        return

    if not timer_active:
        start_timer(client, say, event)


def start_timer(client, say, event):
    global timer_active

    timer_active = True
    print(f"{TIMER_DURATION} second timer started...")
    time.sleep(TIMER_DURATION)
    print(f"{TIMER_DURATION} second timer complete!")

    timer_active = False

    button = calculate_reactions(client, say, event)
    try:
        handle_input(event, say, client, button)
    except errors.SlackApiError as e:
        print(e)
    post_cycle_actions(button)


def post_cycle_actions(button):
    write_inputs_to_file(button)


def write_inputs_to_file(button):
    if os.path.exists("data/inputs.csv"):
        with open("data/inputs.csv", "r", newline="") as file:
            reader = csv.reader(file)
            row_count = sum(1 for row in reader) - 1

    with open("data/inputs.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([row_count, button])
