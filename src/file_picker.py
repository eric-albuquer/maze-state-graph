# [IA] Claude Code (Claude Sonnet 5.5) – arquivo inteiro: abre o explorador de arquivos do sistema para escolher o mapa a importar
"""Abre o explorador de arquivos do sistema para escolher um mapa (.md/.txt).

O diálogo roda em outro processo: misturar tkinter/Cocoa com a janela do pygame
no mesmo processo trava ou derruba o app em alguns sistemas (principalmente macOS).
"""
import subprocess
import sys
from pathlib import Path

PROMPT = "Escolha um arquivo de mapa (.md)"

_TK_SCRIPT = """
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)
path = filedialog.askopenfilename(
    title={prompt!r},
    filetypes=[("Mapas (.md, .txt)", "*.md *.txt"), ("Todos os arquivos", "*.*")],
)
print(path)
"""


class FilePickerError(Exception):
    """O explorador de arquivos não pôde ser aberto (diferente de o usuário cancelar)."""


def pick_map_file() -> Path | None:
    """Retorna o arquivo escolhido, ou None se o usuário cancelar.

    Levanta FilePickerError se o explorador de arquivos não puder ser aberto."""
    if sys.platform == "darwin":
        cmd = [
            "osascript", "-e",
            f'POSIX path of (choose file with prompt "{PROMPT}" of type {{"md", "markdown", "txt"}})',
        ]
    else:
        cmd = [sys.executable, "-c", _TK_SCRIPT.format(prompt=PROMPT)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as e:
        raise FilePickerError(f"Não foi possível abrir o explorador de arquivos ({e}).")
    if result.returncode != 0:
        # osascript devolve erro -128 quando o usuário cancela
        if "-128" in result.stderr:
            return None
        raise FilePickerError(
            "Não foi possível abrir o explorador de arquivos. "
            "Verifique se o tkinter está instalado."
        )
    path = result.stdout.strip()
    return Path(path) if path else None  # vazio = usuário cancelou
