import os
from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App
from slack_event_handlers import handle_input

load_dotenv()
app = App(token=os.getenv('SLACK_TOKEN'))


def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_XAPP")).start()
    handler.start()


@app.event("reaction_added")
def call_reaction_handler(event, say, client):
    handle_input(event, say, client)
