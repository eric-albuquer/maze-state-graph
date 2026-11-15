import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.map import map_loader


class TestIntegrationMapSave(unittest.TestCase):
 
    # Veifica se o mapa carregado é o mesmo salvo em um arquivo temporario
    def test_save_and_load_keeps_map(self):
        lines = [
            "###########",
            "#S.,~+*aA>#",
            "#v<^.....G#",
            "###########",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "original.txt").write_text("\n".join(lines))

            with patch.object(map_loader, "MAPS_FOLDER", Path(tmp)):
                original = map_loader.map_load("original.txt")
                map_loader.map_save(original, "salvo.txt")
                reloaded = map_loader.map_load("salvo.txt")


        self.assertEqual(reloaded.start, original.start)
        self.assertEqual(reloaded.end, original.end)
        self.assertEqual(
            ["".join(repr(cell) for cell in row) for row in reloaded.matrix],
            lines,
        )


if __name__ == "__main__":
    unittest.main()
