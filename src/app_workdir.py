import PySimpleGUI as sg
from pathlib import Path


def _default_arduino_lib_dir() -> Path:
    """
    Heuristic for the default Arduino ›libraries‹ folder.

    • Windows  →  ~/Documents/Arduino/libraries
    • macOS    →  ~/Documents/Arduino/libraries
    • Linux    →  ~/Arduino/libraries
    """
    home = Path.home()
    if home.joinpath("Documents").exists():          # covers Windows & macOS
        return home / "Documents" / "Arduino" / "libraries"
    return home / "Arduino" / "libraries"


def workdir_section() -> list[list[sg.Element]]:
    """Return a single-row layout for dropping into the main window."""
    default_path = _default_arduino_lib_dir()
    return [[
        sg.Text("Working directory:", size=(16, 1)),
        sg.InputText(str(default_path), key="-WORKDIR-", expand_x=True),
        sg.FolderBrowse(target="-WORKDIR-")
    ]]
