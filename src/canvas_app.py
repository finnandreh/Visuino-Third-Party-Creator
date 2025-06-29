import PySimpleGUI as sg
from app_header import header_section
from app_workdir import workdir_section          #  ← NEW IMPORT


def run_app() -> None:
    layout = [
        header_section(),                        # top banner
        *workdir_section(),                      # new row
        [sg.Text("Canvas area / background",
                 size=(60, 20),
                 background_color="lightgrey",
                 key="-CANVAS-",
                 expand_x=True,
                 expand_y=True)],
        [sg.Button("Exit")]
    ]

    window = sg.Window(
        "Visuino Component Creator",
        layout,
        resizable=True,
        finalize=True,
    )

    # ── main event loop ────────────────────────────────
    workdir = None
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        # Capture directory changes (you can expand this later)
        if values.get("-WORKDIR-") != workdir:
            workdir = values["-WORKDIR-"]
            print(f"📂  Working directory set to: {workdir}")

    window.close()
