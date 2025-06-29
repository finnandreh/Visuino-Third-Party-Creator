"""
Enhanced Visuino component‑editing canvas.

Changes compared with the first draft:
    • The window is now split down the middle: left side shows a *read‑only* preview
      of the selected .vcomp file, right side hosts a stub panel with check‑boxes.
    • Later we will wire those check‑boxes so that ticking one of them triggers
      a re‑parse of the file and a live update of the preview (or other widgets).
    • For now the check‑boxes simply log to the console so you can see that the
      events are coming through.

No other files need to change – *open_editor()* is still the entry point that
WorkdirWidget calls.
"""

from __future__ import annotations

from pathlib import Path

import PySimpleGUI as sg


# ── helpers ────────────────────────────────────────────────────────────

def _read_component_text(path: Path) -> str:
    """Return the raw text of the component file (UTF‑8)."""
    try:
        return path.read_text(encoding="utf‑8")
    except Exception as err:  # noqa: BLE001 (broad except ok for a UI tool)
        return f"⚠️  Could not read file: {err}"


# ── public API ─────────────────────────────────────────────────────────

def open_editor(comp_path: Path) -> None:  # noqa: D401 (imperative OK)
    """Modal window that lets the user preview & (later) tweak one component."""

    text = _read_component_text(comp_path)

    # ── LHS: file preview -------------------------------------------------
    lhs = sg.Column(
        [
            [sg.Text("Component file preview:")],
            [
                sg.Multiline(
                    text,
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

    # ── RHS: placeholder options -----------------------------------------
    rhs = sg.Column(
        [
            [sg.Text("Parse options (stub):")],
            [sg.Checkbox("Check A", key="-CHK_A-")],
            [sg.Checkbox("Check B", key="-CHK_B-")],
            [sg.Checkbox("Check C", key="-CHK_C-")],
            [sg.Stretch()],  # push content to the top
        ],
        expand_y=True,
        element_justification="left",
        pad=((10, 0), 0),  # a little breathing room after the separator
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

    # Main event‑loop ------------------------------------------------------
    while True:
        event, values = win.read()

        # ---- close window ------------------------------------------------
        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        # ---- Checkbox stubs ---------------------------------------------
        if event in ("-CHK_A-", "-CHK_B-", "-CHK_C-"):
            # For now just print which option was toggled and its state.
            print(f"{event} → {values[event]}")
            # TODO: hook up your parser and update widgets accordingly.

    win.close()
