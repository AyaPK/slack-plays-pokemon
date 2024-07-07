import os
import time
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
    global timer

    if not timer:
        timer = True
        print("Timer started....")
        for x in range(0, 10, 5):
            print(f"Slept for {x} seconds")
            time.sleep(5)

        print(calculate_reactions(client, event))

        handle_input(event, say, client)
        timer = False
