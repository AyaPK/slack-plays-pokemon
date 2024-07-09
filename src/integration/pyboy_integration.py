from dataclasses import dataclass
from typing import List, Self
from pyboy import PyBoy

from integration.byte_mappings import GEN_1_MOVES, STATUS_BIT_FIELD, TYPE_MAP


def save_initial_state():
    with PyBoy("data/blue.gb", window="null", cgb=True) as pyboy, open("data/state_file.state", "wb") as f:
        pyboy.save_state(f)


def pyboy_tick(button=""):
    valid_buttons = ["a", "b", "up", "down", "left", "right", "start", "select"]

    pyboy = PyBoy("data/blue.gb", window="null", cgb=True)
    pyboy.set_emulation_speed(100)
    try:
        with open("data/state_file.state", "rb") as f:
            pyboy.load_state(f)
    except FileNotFoundError:
        save_initial_state()

    button = button.lower()
    if button in valid_buttons:
        pyboy.button_press(button)
        pyboy.tick(2)
        pyboy.button_release(button)
        pyboy.tick(2)

    pyboy.tick(500)
    pyboy.screen.image.resize((480, 432), 0).save("data/image.png")
    with open("data/state_file.state", "wb") as f:
        pyboy.save_state(f)

    game_info = GameInformation.from_pyboy(pyboy)

    pyboy.stop()

    return game_info


@dataclass
class Pokemon:
    nickname: str
    caught_by: str
    hp: int
    max_hp: int
    level: int
    status: str
    type: str
    move1: str = ""
    move2: str = ""
    move3: str = ""
    move4: str = ""

    @classmethod
    def from_memory_buffer(cls, nickname: str, caught_by: str, buffer) -> Self:
        return Pokemon(
            nickname=nickname,
            caught_by=caught_by,
            hp=int.from_bytes(buffer[0x1:0x1 + 2]),
            max_hp=int.from_bytes(buffer[0x22:0x22 + 2]),
            level=int(buffer[0x21]),
            status=cls._status_from_bit_field(buffer[0x4]),
            type=cls._type_from_bytes(buffer[0x5], buffer[0x6]),
            move1=GEN_1_MOVES[buffer[0x8]],
            move2=GEN_1_MOVES[buffer[0x9]],
            move3=GEN_1_MOVES[buffer[0xA]],
            move4=GEN_1_MOVES[buffer[0xB]],
        )
    
    @staticmethod
    def _type_from_bytes(type1_byte, type2_byte) -> str:
        type1 = TYPE_MAP[type1_byte]
        type2 = TYPE_MAP[type2_byte]

        if type1 == type2:
            return type1

        return f"{type1} - {type2}"
    
    @staticmethod
    def _status_from_bit_field(byte) -> str:
        status = " - ".join([
            ailment
            for bit, ailment in STATUS_BIT_FIELD.items()
            if bit & byte
        ])

        return status or "Healthy"
    
    def as_markdown(self) -> str:
        return f"""
## {self.nickname}

Type: {self.type}

HP: {self.hp} / {self.max_hp}

Status: {self.status}

Level: {self.level}

Moves:
{f" - {self.move1}" if self.move1 else ""}
{f" - {self.move2}" if self.move2 else ""}
{f" - {self.move3}" if self.move3 else ""}
{f" - {self.move4}" if self.move4 else ""}

Caught by: {self.caught_by}
"""


@dataclass
class GameInformation:
    player_name: str
    party: List[Pokemon]

    @classmethod
    def from_pyboy(cls, pyboy) -> Self:
        num_pokemon_in_party = int(pyboy.memory[0xD163])

        return GameInformation(
            player_name=_bytes_as_gen1_string(pyboy.memory[0xD158:0xD158 + 0xB]),
            party=[
                Pokemon.from_memory_buffer(
                    nickname=_bytes_as_gen1_string(pyboy.memory[0xD2B5 + 10 * i:0xD2B5 + 10 * (i + 1)]),
                    caught_by=_bytes_as_gen1_string(pyboy.memory[0xD273 + 10 * i:0xD273 + 10 * (i + 1)]),
                    buffer=pyboy.memory[0xD16B + 44 * i:0xD16B + 44 * (i + 1)]
                )
                for i in range(num_pokemon_in_party)
            ]

        )

    def as_markdown(self) -> str:
        party_data = "\n\n".join([pokemon.as_markdown() for pokemon in self.party])

        return f"""
# Game Data

Name: {self.player_name}

---

# Party:

{party_data}
"""


STRING_TERMINATOR = 80
ASCII_DELTA = 63


def _bytes_as_gen1_string(data) -> str:
    try:
        text = "".join([chr(byte - ASCII_DELTA) for byte in data if byte != STRING_TERMINATOR])
    except:
        text = "UNKNOWN"

    return text
