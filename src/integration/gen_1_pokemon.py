from dataclasses import dataclass
from typing import List, Self

from integration.byte_mappings import (
    EXPERIENCE_TYPES,
    GEN_1_ITEMS,
    GEN_1_MOVES,
    GEN_1_SPECIES,
    STATUS_BIT_FIELD,
    TYPE_MAP,
)


@dataclass
class Pokemon:
    nickname: str
    caught_by: str
    species: str
    hp: int
    max_hp: int
    level: int
    status: str
    type: str
    move1: str
    move2: str
    move3: str
    move4: str
    xp: int
    experience_type: str

    @classmethod
    def from_memory_buffer(cls, nickname: str, caught_by: str, buffer) -> Self:
        return Pokemon(
            nickname=nickname,
            caught_by=caught_by,
            species=GEN_1_SPECIES[int(buffer[0x0])],
            hp=int.from_bytes(buffer[0x1 : 0x1 + 2]),
            max_hp=int.from_bytes(buffer[0x22 : 0x22 + 2]),
            level=int(buffer[0x21]),
            status=cls._status_from_bit_field(buffer[0x4]),
            type=cls._type_from_bytes(buffer[0x5], buffer[0x6]),
            move1=GEN_1_MOVES[buffer[0x8]],
            move2=GEN_1_MOVES[buffer[0x9]],
            move3=GEN_1_MOVES[buffer[0xA]],
            move4=GEN_1_MOVES[buffer[0xB]],
            xp=int.from_bytes(buffer[0x0e: 0x0e + 3]),
            experience_type=EXPERIENCE_TYPES[GEN_1_SPECIES[int(buffer[0x0])]]
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
        status = " - ".join(
            [ailment for bit, ailment in STATUS_BIT_FIELD.items() if bit & byte]
        )

        return status or "Healthy"

    def xp_to_next_level(self) -> int:
        total_required = _xp_required_for_level(self.experience_type, self.level + 1)
        return total_required - self.xp

    def as_markdown(self) -> str:
        return f"""
## {f"{self.nickname} _({self.species})_" if self.nickname else self.species}

Type: {self.type}

HP: {self.hp} / {self.max_hp}

Status: {self.status}

Level: {self.level} ({self.xp_to_next_level()} XP to next level)

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
    money: int
    items: List[str]
    party: List[Pokemon]

    @classmethod
    def from_pyboy(cls, pyboy) -> Self:
        num_pokemon_in_party = int(pyboy.memory[0xD163])
        num_items_in_inventory = int(pyboy.memory[0xD31D])

        return GameInformation(
            player_name=_bytes_as_gen1_string(pyboy.memory[0xD158 : 0xD158 + 0xB]),
            money=cls._binary_coded_decimal_to_int(pyboy.memory[0xD347 : 0xD347 + 0x3]),
            items=[
                f"{pyboy.memory[
                    0xD31E + 0x2 * i + 1
                ]} x {GEN_1_ITEMS[pyboy.memory[
                    0xD31E + 0x2 * i
                ]]}"
                for i in range(num_items_in_inventory)
            ],
            party=[
                Pokemon.from_memory_buffer(
                    nickname=_bytes_as_gen1_string(
                        pyboy.memory[0xD2B5 + 11 * i : 0xD2B5 + 11 * (i + 1)]
                    ),  # The website is wrong. It's not 10 bytes, it's 11
                    caught_by=_bytes_as_gen1_string(
                        pyboy.memory[0xD273 + 11 * i : 0xD273 + 11 * (i + 1)]
                    ),
                    buffer=pyboy.memory[0xD16B + 44 * i : 0xD16B + 44 * (i + 1)],
                )
                for i in range(num_pokemon_in_party)
            ],
        )

    @staticmethod
    def _binary_coded_decimal_to_int(bytes) -> int:
        tot = 0

        for byte in bytes:
            first_nibble = byte & 0b1111
            second_nibble = (byte >> 4) & 0b1111

            tot = (tot * 10) + second_nibble
            tot = (tot * 10) + first_nibble

        return tot

    def as_markdown(self) -> str:
        party_data = "\n\n".join([pokemon.as_markdown() for pokemon in self.party])
        item_data = "\n".join([f" - {item}\n" for item in self.items])

        return f"""
# Game Data

Name: {self.player_name}

Money: ₽ {self.money}

Inventory:

{item_data}

---

# Party:

{party_data}
"""


STRING_TERMINATOR = 80
ASCII_DELTA = 63


def _bytes_as_gen1_string(data) -> str:
    try:
        text = ""
        for byte in data:
            if byte == STRING_TERMINATOR:
                break
            text += chr(byte - ASCII_DELTA)
    except:
        text = "UNKNOWN"

    return text


# https://bulbapedia.bulbagarden.net/wiki/Experience
def _xp_required_for_level(experience_type: str, level: int) -> int:
    match experience_type:
        case "Fast":
            return int(0.8 * level ** 3)
        case "Medium Fast":
            return int(level ** 3)
        case "Medium Slow":
            return int(1.2 * level ** 3 - 15 * level ** 2 + 100 * level - 140)
        case "Slow":
            return int(1.25 * level ** 3)
