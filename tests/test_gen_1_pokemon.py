import unittest

from src.integration.gen_1_pokemon import Pokemon


class TestPokemonDisplay(unittest.TestCase):
    def setUp(self):
        self.pokemon = Pokemon.from_memory_buffer(
            "Cap'n",
            "Green",
            [
                0x5C,  # 0x00 	Index number of the Species 	1 byte
                0x00,
                0x01,  # 0x01 	Current HP 	2 bytes
                0x10,  # 0x03 	Level 	1 byte
                0x02,  # 0x04 	Status condition 	1 byte
                0x01,  # 0x06 	Type 2 	1 byte
                0x02,  # 0x06 	Type 2 	1 byte
                0x00,  # 0x07 	Catch rate/Held item 	1 byte
                0x08,  # 0x08 	Index number of move 1 	1 byte
                0x09,  # 0x09 	Index number of move 2 	1 byte
                0x0A,  # 0x0A 	Index number of move 3 	1 byte
                0x0B,  # 0x0B 	Index number of move 4 	1 byte
                0x0C,
                0x0D,  # 0x0C 	Original Trainer ID number 	2 bytes
                0x0E,
                0x0F,
                0x10,  # 0x0E 	Experience points 	3 bytes
                0x11,
                0x12,  # 0x11 	HP EV data 	2 bytes
                0x13,
                0x14,  # 0x13 	Attack EV data 	2 bytes
                0x15,
                0x16,  # 0x15 	Defense EV data 	2 bytes
                0x17,
                0x18,  # 0x17 	Speed EV data 	2 bytes
                0x19,
                0x1A,  # 0x19 	Special EV data 	2 bytes
                0x1B,
                0x1C,  # 0x1B 	IV data 	2 bytes
                0x1D,  # 0x1D 	Move 1's PP values 	1 byte
                0x1E,  # 0x1E 	Move 2's PP values 	1 byte
                0x1F,  # 0x1F 	Move 3's PP values 	1 byte
                0x20,  # 0x20 	Move 4's PP values 	1 byte
                0x21,  # 0x21 	Level 	1 byte
                0x01,
                0x02,  # 0x22 	Maximum HP 	2 bytes
                0x24,
                0x25,  # 0x24 	Attack 	2 bytes
                0x26,
                0x27,  # 0x26 	Defense 	2 bytes
                0x28,
                0x29,  # 0x28 	Speed 	2 bytes
                0x2A,
                0x2B,  # 0x2A 	Special 	2 bytes
            ],
        )

    def test_parse(self):
        self.assertEqual("Cap'n", self.pokemon.nickname)
        self.assertEqual("Green", self.pokemon.caught_by)
        self.assertEqual("Horsea", self.pokemon.species)
        self.assertEqual(1, self.pokemon.hp)
        self.assertEqual(256 + 2, self.pokemon.max_hp)
        self.assertEqual(33, self.pokemon.level)
        self.assertEqual("Healthy", self.pokemon.status)
        self.assertEqual("Fighting - Flying", self.pokemon.type)
        self.assertEqual("Ice Punch", self.pokemon.move1)
        self.assertEqual("Thunder Punch", self.pokemon.move2)
        self.assertEqual("Scratch", self.pokemon.move3)
        self.assertEqual("Vise Grip", self.pokemon.move4)

    def test_output(self):
        self.assertEqual(
            self.pokemon.as_markdown(),
            f"""
## Cap'n _(Horsea)_

Type: Fighting - Flying

HP: 1 / 258

Status: Healthy

Level: 33

Moves:
 - Ice Punch
 - Thunder Punch
 - Scratch
 - Vise Grip

Caught by: Green
""",
        )


if __name__ == "__main__":
    unittest.main()
