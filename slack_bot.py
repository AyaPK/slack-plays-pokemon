import json
import os
import time
from slack_sdk import errors
from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App
from slack_event_handlers import handle_input, calculate_reactions

load_dotenv()
app = App(token=os.getenv('SLACK_TOKEN'))


def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_XAPP")).start()
    handler.start()


timer = False


@app.event("reaction_added")
def call_reaction_handler(event, say, client):
    if event["reaction"] not in json.loads(os.getenv("VALID_REACTIONS")):
        return

    global timer

    if not timer:
        try:
            client.reactions_add(
                channel=event["item"]["channel"],
                name="30-sec-timer",
                timestamp=event["item"]["ts"]
            )
        except errors.SlackApiError:
            pass

        timer = True
        print("Timer started....")
        for x in range(0, 10, 5):
            print(f"Slept for {x} seconds")
            time.sleep(5)

        button = calculate_reactions(client, say, event)

        handle_input(event, say, client, button)
        timer = False
