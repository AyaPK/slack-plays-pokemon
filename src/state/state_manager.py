import os
import pickle


class StateManager:
    def __init__(self):
        self.last_message = None
        self.canvas = None


def save_state(manager, filename='data/state_manager.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(manager, file)


def load_state(filename='data/state_manager.pkl'):
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
    else:
        manager = StateManager()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        save_state(manager, filename)
        return manager


state_manager = load_state()
