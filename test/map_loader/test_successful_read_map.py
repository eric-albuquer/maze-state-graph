import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.map import map_loader
from src.map.map_nodes import *


def load_from_text(content: str):
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "mapa.txt").write_text(content)
        with patch.object(map_loader, "MAPS_FOLDER", Path(tmp)):
            return map_loader.map_load("mapa.txt")



class TestSuccessfulReadMap(unittest.TestCase):

    # verifica se o quantidade de colulas e linhas batem com o arquivo lido.
    def test_start_end_and_size(self):
        map = load_from_text("\n".join([
            "#####",
            "#...#",
            "#####",
        ]))
        self.assertEqual(map.rows, 3)
        self.assertEqual(map.cols, 5)

    # verifica se todos os simploes foram reconhecidos corretamente
    def test_each_symbol_creates_right_tile(self):
        map = load_from_text("\n".join([
            "#########",
            "#S.,~+*G#",
            "#########",
        ]))

        row = map.matrix[1]
        self.assertIsInstance(map.matrix[0][0], MapWall)
        self.assertIsInstance(row[1], MapStart)
        self.assertIsInstance(row[2], MapDotFloor)
        self.assertIsInstance(row[3], MapMud)
        self.assertIsInstance(row[4], MapWater)
        self.assertIsInstance(row[5], MapBonus)
        self.assertIsInstance(row[6], MapSource)
        self.assertIsInstance(row[7], MapEnd)


    #Verificam se as chaves e portam são reconhecidas.
    def test_keys_and_ports(self):
        map = load_from_text("\n".join([
            "#######",
            "#SaAbBG#",
            "#######",
        ]))

        row = map.matrix[1]
        self.assertIsInstance(row[2], MapKey)
        self.assertEqual(row[2].letter, "a")
        self.assertIsInstance(row[3], MapPort)
        self.assertEqual(row[3].letter, "a")
        self.assertIsInstance(row[4], MapKey)
        self.assertEqual(row[4].letter, "b")
        self.assertIsInstance(row[5], MapPort)
        self.assertEqual(row[5].letter, "b")


    #verifica se as 4 esteiras viram a istancia correta de mapfloordirected com as possições de direção corretas.
    def test_directed_floors(self):
        map = load_from_text("\n".join([
            "########",
            "#S><v^G#",
            "########",
        ]))

        row = map.matrix[1]
        expected = {2: (1, 0), 3: (-1, 0), 4: (0, 1), 5: (0, -1)}
        for x, dir_vec in expected.items():
            self.assertIsInstance(row[x], MapFloorDirected)
            self.assertEqual(row[x].dir_vec, dir_vec)


if __name__ == "__main__":
    unittest.main()
