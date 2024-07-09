import csv
import os

from bot.slack_bot import start_slack_bot


def main():
    set_up_files()
    start_slack_bot()


def set_up_files():
    if not os.path.exists("data/inputs.csv"):
        with open("data/inputs.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["order_id", "Input"])
        print("Inputs CSV file created.")


if __name__ == "__main__":
    main()
