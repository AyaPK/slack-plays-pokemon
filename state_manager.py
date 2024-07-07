class StateManager:
    def __init__(self):
        self.last_message = None

    def set_last_message(self, message):
        self.last_message = message

    def get_last_message(self):
        return self.last_message


state_manager = StateManager()
