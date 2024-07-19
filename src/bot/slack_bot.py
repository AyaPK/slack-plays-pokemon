import csv
import os
import time
import json
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from bot.slack_event_handlers import handle_input, calculate_reactions
from state.state_manager import state_manager
from slack_sdk import errors

load_dotenv()

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
SLACK_XAPP = os.getenv('SLACK_XAPP')
VALID_REACTIONS = os.getenv('VALID_REACTIONS')

if not SLACK_TOKEN or not SLACK_XAPP or not VALID_REACTIONS:
    raise ValueError("Missing necessary environment variables.")

app = App(token=SLACK_TOKEN)

TIMER_DURATION = 5
timer_active = False
reactions_dict = {}

def start_slack_bot():
    handler = SocketModeHandler(app, SLACK_XAPP)
    handler.start()


@app.event("reaction_added")
def handle_reaction_added(event, say, client):
    global timer_active
    global reactions_dict

    if state_manager.last_message and event["item"]["ts"] != state_manager.last_message["ts"]:
        return

    reaction = event.get("reaction")
    if reaction not in json.loads(VALID_REACTIONS):
        return

    user = event.get("user")
    if user not in reactions_dict.keys(): 
        reactions_dict[f"{user}-{len(reactions_dict)}"] = (event.get("event_ts"), reaction)

    if not timer_active:
        start_timer(client, say, event)


def start_timer(client, say, event):
    global timer_active
    global reactions_dict

    timer_active = True
    print(f"{TIMER_DURATION} second timer started...")
    time.sleep(TIMER_DURATION)
    print(f"{TIMER_DURATION} second timer complete!")


    if isAnarchyMode():
        try:
            handle_input(event,say,client,anarchy_inputs=convert_reactions_dict_to_input_list(reactions_dict))
        except errors.SlackApiError as e:
            print(e)
        post_anarchy_cycle_actions()

    else:
        button = calculate_reactions(client, say, event)
        try:
            handle_input(event, say, client, button)
        except errors.SlackApiError as e:
            print(e)

        post_cycle_actions(button)
    
    timer_active = False


def convert_reactions_dict_to_input_list(reactions: dict):
    sorted_values = sorted(reactions.values(), key=lambda x: x[0])

    return [t[1] for t in sorted_values]

def post_cycle_actions(button):
    write_inputs_to_file(button)

def post_anarchy_cycle_actions():
    global reactions_dict

    reactions_dict = {}


def write_inputs_to_file(button):
    if os.path.exists("data/inputs.csv"):
        with open("data/inputs.csv", 'r', newline='') as file:
            reader = csv.reader(file)
            row_count = sum(1 for row in reader) - 1

    with open("data/inputs.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([row_count, button])

def isAnarchyMode():
    return True
