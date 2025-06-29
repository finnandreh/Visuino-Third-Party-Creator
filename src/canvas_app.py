import PySimpleGUI as sg
from app_header   import header_section
from app_workdir  import WorkdirWidget


def run_app() -> None:
    wd = WorkdirWidget()

    layout = [
        header_section(),
        *wd.layout,
        [sg.Text("Canvas area / background",
                 size=(60, 15),
                 background_color="lightgrey",
                 key="-CANVAS-",
                 expand_x=True, expand_y=True)],
        [sg.Text("", key="-DEBUG-", size=(120, 2),
                 text_color="white", background_color="black",
                 font=("Consolas", 10, "bold"))],
        [sg.Button("Exit")],
    ]

    window = sg.Window("Visuino Component Creator",
                       layout,
                       size=(1200, 800),
                       resizable=True,
                       finalize=True)
    window.TKroot.minsize(1200, 800)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        # Forward all events to widget
        dbg = wd.handle_event(event, values, window)
        if dbg:
            window["-DEBUG-"].update(dbg)
            print(dbg)

    window.close()


if __name__ == "__main__":
    run_app()
