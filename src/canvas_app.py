import PySimpleGUI as sg
from app_header import header_section  # Import top section

def run_app():
    layout = [
        header_section(),  # From external file
        [sg.Text("Canvas area / background", size=(60, 20), background_color="lightgrey")],
        [sg.Button("Exit")]
    ]

    window = sg.Window("Visuino Component Creator", layout, resizable=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

    window.close()
