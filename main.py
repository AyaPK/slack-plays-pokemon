import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from dotenv import load_dotenv

load_dotenv()
app = App(token=os.getenv('SLACK_TOKEN'))


def main():
    start_slack_bot()


def start_slack_bot():
    SocketModeHandler(app,
                      os.getenv("SLACK_XAPP")
                      ).start()


@app.event("app_mention")
def hello_world(ack, body, say, client):
    say("I heard that!")


if __name__ == "__main__":
    main()
