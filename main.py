import os

from dotenv import load_dotenv


def main():
    load_dotenv()

    print(os.getenv("SLACK_TOKEN"))


if __name__ == "__main__":
    main()
