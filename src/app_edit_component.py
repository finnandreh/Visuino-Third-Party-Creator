"""
Enhanced Visuino component‑editing canvas with **Pre Populate** support.

Updates in this revision
========================
* When you click **Pre populate**, the code now also ensures that the referenced
  header file (e.g. `FinnPulse.h`) exists under your library’s `SRC/` folder.
  If it isn’t there, a template-based header stub with correct Visuino pattern
  and namespace is auto‑generated so the project compiles straight away.
"""

from __future__ import annotations

import re
from pathlib import Path

import PySimpleGUI as sg

######################################################################
# helpers
######################################################################

def _read_component_text(path: Path) -> str:
    """Return the raw text of the component file (UTF-8)."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as err:  # noqa: BLE001
        return f"⚠️  Could not read file: {err}"


def _camel_to_title(s: str) -> str:
    """Convert *CamelCase* → "Camel Case"."""
    return re.sub(r"(?<!^)(?=[A-Z])", " ", s).strip()

######################################################################
# main entry point
######################################################################

def open_editor(comp_path: Path) -> None:
    """Open a modal editor for a single `.vcomp` file."""

    # ── infer nickname/short-name from filename --------------------------------
    stem_parts = comp_path.stem.split(".", 1)
    if len(stem_parts) == 2:
        nickname, short = stem_parts
    else:
        nickname, short = "", stem_parts[0]

    namespace        = nickname or "MyNamespace"
    disp_name_def    = _camel_to_title(short)
    create_name_def  = re.sub(r"\s+", "", disp_name_def)
    header_def       = f"{create_name_def}.h"
    categories       = [
        "TArduinoBooleanFlipFlopsToolbarCategory",
        "TArduinoMathFunctionsToolbarCategory",
        "TArduinoSignalSourcesToolbarCategory",
    ]

    # ── UI layout -------------------------------------------------------------
    lhs = sg.Column(
        [
            [sg.Text("Component file preview:")],
            [sg.Multiline(_read_component_text(comp_path), size=(80, 28), key="-TXT-", disabled=True,
                          font=("Courier New", 9), expand_x=True, expand_y=True, horizontal_scroll=True)],
        ], expand_x=True, expand_y=True)

    rhs = sg.Column(
        [
            [sg.Text("Display name:"), sg.InputText(disp_name_def, key="-NAME-", size=(25, 1))],
            [sg.Text("Header file (.h):"), sg.InputText(header_def, key="-HDR-", size=(25, 1))],
            [sg.Text("Category:"), sg.Combo(categories, default_value=categories[0], key="-CAT-", readonly=True, size=(35, 1))],
            [sg.Checkbox("ArduinoLoopBegin", key="-LOOP-")],
            [sg.Button("Pre populate", key="-PREPOP-", button_color=("white", "green"))],
            [sg.Stretch()],
        ], pad=((10, 0), 0), expand_y=True)

    layout = [[lhs, sg.VerticalSeparator(), rhs], [sg.Push(), sg.Button("Close", size=(10, 1))]]

    win = sg.Window(f"Edit – {comp_path.name}", layout, modal=True, finalize=True, resizable=True)

    # ── event loop -----------------------------------------------------------
    while True:
        event, values = win.read()
        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        if event == "-PREPOP-":
            # gather user settings
            disp_name   = values["-NAME-"].strip() or disp_name_def
            create_name = re.sub(r"\s+", "", disp_name)
            header_file = values["-HDR-"].strip() or f"{create_name}.h"
            loop_flag   = values["-LOOP-"]
            category    = values["-CAT-"] or categories[0]

            # build .vcomp template
            tmpl_lines = [
                f"{namespace} : Namespace\n",
                f"    [Name('{disp_name}')]\n",
                f"    [CreateName('{create_name}')]\n",
                f"    [ArduinoInclude( '{header_file}' )]\n",
            ]
            if loop_flag:
                tmpl_lines.append("    [ArduinoLoopBegin]\n")
            tmpl_lines.extend([
                f"    [ArduinoClass( '{namespace}::{create_name}' )]\n",
                f"    [Category( {category} )]\n\n",
                f"        +TArduino{create_name}: TArduinoComponent\n\n",
                "            InputPin : TOWArduinoDigitalSinkPin\n",
                "            OutputPin : TOWArduinoDigitalSourcePin\n\n",
                "        ; // TArduinoComponent\n\n\n",
                f"; // {namespace}\n",
            ])
            new_text = "".join(tmpl_lines)

            # write .vcomp
            try:
                comp_path.write_text(new_text, encoding="utf-8")
            except Exception as exc:
                sg.popup_error(f"Could not write .vcomp file:\n{exc}")
                continue

            # ensure header file exists under SRC/ with class skeleton only
            lib_root  = comp_path.parent.parent
            src_dir   = lib_root / "SRC"
            src_dir.mkdir(parents=True, exist_ok=True)
            header_path = src_dir / header_file
            if not header_path.exists():
                content = f"""
#pragma once

#include <Mitov.h>

namespace {namespace}
{{
  template <typename T_OutputPin>
  class {create_name} : public T_OutputPin
  {{
    _V_PIN_( OutputPin )

    // Inputs and outputs will be added later via editor

    inline void InputPin_o_Receive(void* _Data)
    {{
      // placeholder
    }}
  }};
}}
"""
                try:
                    header_path.write_text(content.strip() + "\n", encoding="utf-8")
                except Exception as exc:
                    sg.popup_error(f"Failed to create header file:\n{exc}")

            win["-TXT-"].update(new_text)
            sg.popup_ok("Files successfully pre‑populated!", title="✅ Success")

    win.close()
