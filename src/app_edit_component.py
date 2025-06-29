"""
Enhanced Visuino component‑editing canvas with **Pre Populate** support.

Usage flow (quick recap)
========================
1. WorkdirWidget still calls `open_editor(path)` when you press **Edit component**.
2. The editor window splits **left** (read‑only file preview) and **right** (options).
3. Fill in / tweak the fields on the right, tick *ArduinoLoopBegin* if wanted and
   click **Pre populate** ➜ the file gets overwritten with a template that pulls
   in your settings. The preview refreshes instantly so you can keep iterating.

The heavy lifting lives entirely inside this file – you don’t have to touch
`WorkdirWidget` again.
"""

from __future__ import annotations

import re
from pathlib import Path

import PySimpleGUI as sg

######################################################################
# helpers
######################################################################

def _read_component_text(path: Path) -> str:
    """Return the raw text of the component file (UTF‑8)."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as err:  # noqa: BLE001 – broad except is fine inside a UI tool
        return f"⚠️  Could not read file: {err}"


def _camel_to_title(s: str) -> str:
    """Convert *CamelCase* → "Camel Case" for nicer defaults."""
    return re.sub(r"(?<!^)(?=[A-Z])", " ", s).strip()

######################################################################
# main entry point
######################################################################

def open_editor(comp_path: Path) -> None:  # noqa: D401 – imperative name is OK
    """Open a modal editor for a single `.vcomp` file."""

    # ── infer nickname/short‑name from filename --------------------------------
    stem_parts = comp_path.stem.split(".", 1)
    if len(stem_parts) == 2:
        nickname, short = stem_parts
    else:  # file not prefixed – still allow editing
        nickname, short = "", stem_parts[0]

    namespace        = f"{nickname}Lib" if nickname else "MyLib"
    disp_name_def    = _camel_to_title(short)
    create_name_def  = re.sub(r"\s+", "", disp_name_def)
    header_def       = f"{create_name_def}.h"
    categories       = [
        "TArduinoBooleanFlipFlopsToolbarCategory",
        "TArduinoMathFunctionsToolbarCategory",
        "TArduinoSignalSourcesToolbarCategory",
    ]

    ##################################################################
    # UI layout
    ##################################################################

    # Left – file preview -------------------------------------------------------
    lhs = sg.Column(
        [
            [sg.Text("Component file preview:")],
            [
                sg.Multiline(
                    _read_component_text(comp_path),
                    size=(80, 28),
                    key="-TXT-",
                    disabled=True,
                    font=("Courier New", 9),
                    expand_x=True,
                    expand_y=True,
                    horizontal_scroll=True,
                )
            ],
        ],
        expand_x=True,
        expand_y=True,
    )

    # Right – options & actions -------------------------------------------------
    rhs = sg.Column(
        [
            [sg.Text("Display name:"), sg.InputText(disp_name_def, key="-NAME-", size=(25, 1))],
            [sg.Text("Header file (.h):"), sg.InputText(header_def, key="-HDR-", size=(25, 1))],
            [sg.Text("Category:"), sg.Combo(categories, default_value=categories[0], key="-CAT-", readonly=True, size=(35, 1))],
            [sg.Checkbox("ArduinoLoopBegin", key="-LOOP-")],
            [sg.Button("Pre populate", key="-PREPOP-", button_color=("white", "green"))],
            [sg.Stretch()],
        ],
        element_justification="left",
        pad=((10, 0), 0),
        expand_y=True,
    )

    layout = [
        [lhs, sg.VerticalSeparator(), rhs],
        [sg.Push(), sg.Button("Close", size=(10, 1))],
    ]

    win = sg.Window(
        f"Edit – {comp_path.name}",
        layout,
        modal=True,
        finalize=True,
        resizable=True,
    )

    ##################################################################
    # event‑loop
    ##################################################################

    while True:
        event, values = win.read()

        # ---- Close window -----------------------------------------------------
        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        # ---- Pre‑populate template -------------------------------------------
        if event == "-PREPOP-":
            # Gather user settings (fall back to defaults if fields left empty)
            disp_name = values["-NAME-"].strip() or disp_name_def
            create_name = re.sub(r"\s+", "", disp_name)
            header_file = values["-HDR-"].strip() or f"{create_name}.h"
            loop_flag   = values["-LOOP-"]
            category    = values["-CAT-"] or categories[0]

            # Build template ---------------------------------------------------
            tmpl_lines: list[str] = [
                f"{namespace} : Namespace\n",
                f"    [Name('{disp_name}')]\n",
                f"    [CreateName('{create_name}')]\n",
                f"    [ArduinoInclude( '{header_file}' )]\n",
            ]
            if loop_flag:
                tmpl_lines.append("    [ArduinoLoopBegin]\n")
            tmpl_lines.extend(
                [
                    f"    [ArduinoClass( '{namespace}::{create_name}' )]\n",
                    f"    [Category( {category} )]\n\n",
                    f"        +TArduino{create_name}: TArduinoComponent\n\n",
                    "            InputPin : TOWArduinoDigitalSinkPin\n",
                    "            OutputPin : TOWArduinoDigitalSourcePin\n\n",
                    "        ; // TArduinoComponent\n\n\n",
                    f"; // {namespace}\n",
                ]
            )
            new_text = "".join(tmpl_lines)

            # Write file + update preview -------------------------------------
            try:
                comp_path.write_text(new_text, encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                sg.popup_error(f"Could not write file:\n{exc}")
            else:
                win["-TXT-"].update(new_text)
                sg.popup_ok("File successfully pre‑populated!", title="✅ Success")

    win.close()
