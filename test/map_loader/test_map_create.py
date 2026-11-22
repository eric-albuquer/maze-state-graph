# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: testes do editor de mapas (lógica) e do salvamento do mapa criado em maps/update/
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.map import map_loader
from src.map.map_editor import MAX_COLS, MAX_ROWS, MIN_SIZE, erase, grid_to_lines, new_grid, paint, parse_size
from src.map.map_loader import map_create_and_save, map_load


VALID = ["#####", "#S.G#", "#####"]


class TestMapEditor(unittest.TestCase):
    def test_new_grid_has_border_start_and_end(self):
        lines = grid_to_lines(new_grid(5, 7))
        self.assertEqual(lines[0], "#######")
        self.assertEqual(lines[-1], "#######")
        self.assertEqual(lines[1][1], "S")
        self.assertEqual(lines[-2][-2], "G")

    def test_paint_and_erase(self):
        grid = new_grid(5, 7)
        self.assertTrue(paint(grid, 3, 2, ","))
        self.assertEqual(grid[2][3], ",")
        self.assertTrue(erase(grid, 3, 2))
        self.assertEqual(grid[2][3], ".")

    def test_border_cannot_be_changed(self):
        grid = new_grid(5, 7)
        self.assertFalse(paint(grid, 0, 0, "."))
        self.assertFalse(paint(grid, 6, 2, "."))
        self.assertFalse(paint(grid, 99, 99, "."))
        self.assertEqual(grid[0][0], "#")

    def test_start_and_end_are_unique(self):
        grid = new_grid(5, 7)
        paint(grid, 3, 2, "S")
        flat = "".join(grid_to_lines(grid))
        self.assertEqual(flat.count("S"), 1)
        self.assertEqual(grid[2][3], "S")
        self.assertEqual(grid[1][1], ".")

    def test_too_small_grid(self):
        with self.assertRaises(ValueError):
            new_grid(3, 3)

    def test_too_large_grid(self):
        with self.assertRaises(ValueError):
            new_grid(MAX_ROWS + 1, 7)
        with self.assertRaises(ValueError):
            new_grid(7, MAX_COLS + 1)


class TestParseSize(unittest.TestCase):
    def test_valid_sizes(self):
        self.assertEqual(parse_size("15", MIN_SIZE, MAX_ROWS, "linhas"), 15)
        self.assertEqual(parse_size(" 7 ", MIN_SIZE, MAX_ROWS, "linhas"), 7)
        self.assertEqual(parse_size(str(MIN_SIZE), MIN_SIZE, MAX_ROWS, "linhas"), MIN_SIZE)
        self.assertEqual(parse_size(str(MAX_COLS), MIN_SIZE, MAX_COLS, "colunas"), MAX_COLS)

    def test_empty_text(self):
        with self.assertRaises(ValueError):
            parse_size("  ", MIN_SIZE, MAX_ROWS, "linhas")

    def test_not_an_integer(self):
        for text in ("abc", "1.5", "-7", "7a"):
            with self.assertRaises(ValueError, msg=text):
                parse_size(text, MIN_SIZE, MAX_ROWS, "linhas")

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            parse_size(str(MIN_SIZE - 1), MIN_SIZE, MAX_ROWS, "linhas")
        with self.assertRaises(ValueError):
            parse_size(str(MAX_ROWS + 1), MIN_SIZE, MAX_ROWS, "linhas")


class TestMapCreateAndSave(unittest.TestCase):
    def create(self, lines, name):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(map_loader, "MAPS_FOLDER", Path(tmp)):
                result = map_create_and_save(lines, name)
                saved_file = Path(tmp) / result[1]
                return result, saved_file.read_text(), map_load(result[1])

    def test_saved_in_update_folder_and_reloadable(self):
        (m, saved), text, reloaded = self.create(VALID, "meu_mapa")
        self.assertEqual(saved, "update/meu_mapa.txt")
        self.assertEqual(text.splitlines(), VALID)
        self.assertEqual((reloaded.start, reloaded.end), (m.start, m.end))

    def test_does_not_overwrite_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(map_loader, "MAPS_FOLDER", Path(tmp)):
                _, first = map_create_and_save(VALID, "mapa")
                _, second = map_create_and_save(VALID, "mapa")
        self.assertEqual(first, "update/mapa.txt")
        self.assertEqual(second, "update/mapa_2.txt")

    def test_name_is_sanitized(self):
        (_, saved), _, _ = self.create(VALID, "meu mapa/novo!")
        self.assertEqual(saved, "update/meu_mapa_novo_.txt")

    def test_empty_name(self):
        with self.assertRaises(ValueError):
            self.create(VALID, "   ")

    def test_missing_start_or_end(self):
        with self.assertRaises(ValueError):
            self.create(["#####", "#..G#", "#####"], "x")
        with self.assertRaises(ValueError):
            self.create(["#####", "#S..#", "#####"], "x")

    def test_border_must_be_walls(self):
        with self.assertRaises(ValueError):
            self.create(["#####", ".S.G#", "#####"], "x")


if __name__ == "__main__":
    unittest.main()
