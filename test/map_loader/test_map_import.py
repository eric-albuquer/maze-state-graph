# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: testes da importação de mapas (.md/.txt) e do salvamento em maps/update/
import tempfile
import unittest
from pathlib import Path

from unittest.mock import patch

from src.map import map_loader
from src.map.map_loader import map_import, map_import_and_save, list_update_maps, map_load
from src.map.map_nodes import MapStart, MapEnd


def import_text(content: str, name: str = "mapa.md"):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_text(content, encoding="utf-8")
        return map_import(path)


class TestMapImport(unittest.TestCase):
    def test_raw_map(self):
        m = import_text("#####\n#S.G#\n#####\n")
        self.assertEqual((m.rows, m.cols), (3, 5))
        self.assertEqual(m.start, (1, 1))
        self.assertEqual(m.end, (3, 1))
        self.assertIsInstance(m.matrix[1][1], MapStart)
        self.assertIsInstance(m.matrix[1][3], MapEnd)

    def test_map_inside_code_fence(self):
        m = import_text("```\n#####\n#S.G#\n#####\n```\n")
        self.assertEqual((m.rows, m.cols), (3, 5))

    def test_blank_lines_and_fence_language_ignored(self):
        m = import_text("\n```text\n#####\n\n#S.G#\n#####\n```\n\n")
        self.assertEqual((m.rows, m.cols), (3, 5))

    def test_missing_start_or_end(self):
        with self.assertRaises(ValueError):
            import_text("#####\n#..G#\n#####\n")
        with self.assertRaises(ValueError):
            import_text("#####\n#S..#\n#####\n")

    def test_invalid_symbol(self):
        with self.assertRaises(ValueError):
            import_text("#####\n#S?G#\n#####\n")

    def test_uneven_rows(self):
        with self.assertRaises(ValueError):
            import_text("#####\n#S.G#\n####\n")

    def test_empty_file(self):
        with self.assertRaises(ValueError):
            import_text("  \n\n")


class TestMapImportSave(unittest.TestCase):
    def test_saved_in_update_folder_and_reloadable(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "meu_mapa.md"
            src.write_text("```\n#####\n#S.G#\n#####\n```\n", encoding="utf-8")
            maps_dir = Path(tmp) / "maps"
            maps_dir.mkdir()
            with patch.object(map_loader, "MAPS_FOLDER", maps_dir):
                m, saved = map_import_and_save(src)
                self.assertEqual(saved, "update/meu_mapa.txt")
                self.assertTrue((maps_dir / "update" / "meu_mapa.txt").is_file())
                self.assertEqual(list_update_maps(), ["update/meu_mapa.txt"])
                again = map_load(saved)
                self.assertEqual((again.rows, again.cols), (m.rows, m.cols))
                self.assertEqual(again.start, m.start)

    def test_does_not_overwrite_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "mapa.md"
            src.write_text("#####\n#S.G#\n#####\n", encoding="utf-8")
            maps_dir = Path(tmp) / "maps"
            maps_dir.mkdir()
            with patch.object(map_loader, "MAPS_FOLDER", maps_dir):
                _, first = map_import_and_save(src)
                _, second = map_import_and_save(src)
                self.assertEqual(first, "update/mapa.txt")
                self.assertEqual(second, "update/mapa_2.txt")


if __name__ == "__main__":
    unittest.main()
