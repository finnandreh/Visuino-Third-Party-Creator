import PySimpleGUI as sg
from pathlib import Path
from glob import glob


# ── helpers ──────────────────────────────────────────────────────────────
def _default_arduino_lib_dir() -> Path:
    home = Path.home()
    return (home / "Documents" / "Arduino" / "libraries"
            if (home / "Documents").exists()           # Windows / macOS
            else home / "Arduino" / "libraries")       # Linux


_TEMPLATE_PROPERTIES = """\
name=YourComponentLibrary
version=1.0.0
author=Your Name <your@email.com>
maintainer=Your Name <your@email.com>
sentence=Library for custom Visuino components.
paragraph=This library was generated using the Visuino Third Party Creator tool.
category=Uncategorized
url=https://example.com/your-library
architectures=*
"""


class WorkdirWidget:
    # element keys
    VERIFY, CREATE, STRUCT = "-VERIFY-", "-CREATE-", "-STRUCT-"
    TOGGLE, SAVE           = "-TOGGLELIB-", "-SAVELIB-"
    LISTBTN                = "-LISTCOMP-"
    WORKDIR, NICK          = "-WORKDIR-", "-NICKNAME-"
    LIBTXT, LIBCOL         = "-LIBTXT-", "-LIBCOL-"
    LISTCOL, COMPLIST      = "-LISTCOL-", "-COMPLIST-"

    def __init__(self) -> None:
        default = _default_arduino_lib_dir()

        # ── top controls ───────────────────────────────────────────────
        self.layout: list[list[sg.Element]] = [
            [
                sg.Text("Working directory:", size=(16, 1)),
                sg.InputText(str(default), key=self.WORKDIR, expand_x=True),
                sg.FolderBrowse(target=self.WORKDIR),
            ],
            [
                sg.Text("Author nickname:", size=(16, 1)),
                sg.InputText("", key=self.NICK, expand_x=True),
            ],
            [
                sg.Button("Verify", key=self.VERIFY, button_color=("white", "blue")),
                sg.Button("Create", key=self.CREATE, disabled=True),
                sg.Button("Create structure", key=self.STRUCT, disabled=True),
                sg.Button("Show structure info", key=self.TOGGLE, disabled=True),
                sg.Button("Show components", key=self.LISTBTN, disabled=True),
            ],
        ]

        # ── shared space (one slot, two over-laid panels) ──────────────
        shared_space = sg.Column(
            [[
                sg.Column(  # library.properties editor
                    [
                        [sg.Text("library.properties content:")],
                        [sg.Multiline("", size=(80, 12), key=self.LIBTXT)],
                        [sg.Button("Save properties", key=self.SAVE)],
                    ],
                    key=self.LIBCOL,
                    visible=False,
                    expand_x=True,
                ),
                sg.Column(  # component list
                    [
                        [sg.Text("Components in library:")],
                        [sg.Listbox(values=[], size=(80, 12), key=self.COMPLIST)],
                    ],
                    key=self.LISTCOL,
                    visible=False,
                    expand_x=True,
                ),
            ]],
            expand_x=True,
        )

        self.layout += [[shared_space]]

    # ── helpers ────────────────────────────────────────────────────────
    def _effective_path(self, vals) -> Path:
        base = Path(vals[self.WORKDIR]).expanduser()
        nick = vals[self.NICK].strip()
        return base / nick if nick else base

    def _structure_ok(self, root: Path) -> bool:
        return all([
            (root / "SRC").is_dir(),
            (root / "Visuino" / "images").is_dir(),
            (root / "library.properties").is_file(),
            (root / "visuino.library").is_file(),
        ])

    def _build_structure(self, root: Path) -> None:
        (root / "SRC").mkdir(parents=True, exist_ok=True)
        (root / "Visuino" / "images").mkdir(parents=True, exist_ok=True)
        lp = root / "library.properties"
        if not lp.exists():
            lp.write_text(_TEMPLATE_PROPERTIES, encoding="utf-8")
        (root / "visuino.library").touch(exist_ok=True)

    def _load_lib_text(self, root: Path) -> str:
        lp = root / "library.properties"
        return lp.read_text(encoding="utf-8") if lp.is_file() else _TEMPLATE_PROPERTIES

    def _scan_components(self, root: Path) -> list[str]:
        vcomps  = glob(str(root / "Visuino" / "*.vcomp"))
        headers = glob(str(root / "SRC" / "*.h"))
        cpps    = glob(str(root / "SRC" / "*.cpp"))
        return [Path(p).name for p in (vcomps + headers + cpps)]

    # ── dispatcher ─────────────────────────────────────────────────────
    def handle_event(self, event: str, vals: dict, win: sg.Window) -> str | None:
        root = self._effective_path(vals)

        # ---------- VERIFY ----------
        if event == self.VERIFY:
            if root.exists():
                if self._structure_ok(root):
                    win[self.CREATE].update(disabled=True)
                    win[self.STRUCT].update(disabled=True)
                    win[self.TOGGLE].update(disabled=False, text="Show structure info")
                    win[self.LISTBTN].update(disabled=False, text="Show components")
                    return f"✅ Directory & structure OK: {root}"
                else:
                    win[self.CREATE].update(disabled=True)
                    win[self.STRUCT].update(disabled=False)
                    win[self.TOGGLE].update(disabled=True)
                    win[self.LISTBTN].update(disabled=True)
                    return "✅ Directory exists but structure incomplete."
            else:
                win[self.CREATE].update(disabled=False)
                win[self.STRUCT].update(disabled=True)
                win[self.TOGGLE].update(disabled=True, text="Show structure info")
                win[self.LISTBTN].update(disabled=True, text="Show components")
                win[self.LIBCOL].update(visible=False)
                win[self.LISTCOL].update(visible=False)
                return "👍 Directory does NOT exist. Press Create."

        # ---------- CREATE ----------
        if event == self.CREATE:
            try:
                root.mkdir(parents=True, exist_ok=False)
                win[self.CREATE].update(disabled=True)
                win[self.STRUCT].update(disabled=False)
                return f"✅ Created directory: {root}"
            except FileExistsError:
                return "⚠️ Directory already exists."
            except Exception as e:
                return f"❌ Error: {e}"

        # ---------- CREATE STRUCTURE ----------
        if event == self.STRUCT:
            try:
                self._build_structure(root)
                win[self.LIBTXT].update(self._load_lib_text(root))
                win[self.LIBCOL].update(visible=True)
                win[self.LISTCOL].update(visible=False)
                win[self.TOGGLE].update(disabled=False, text="Hide structure info")
                win[self.LISTBTN].update(disabled=False, text="Show components")
                win[self.STRUCT].update(disabled=True)
                return f"✅ Structure created in {root}"
            except Exception as e:
                return f"❌ Error creating structure: {e}"

        # ---------- TOGGLE STRUCTURE INFO ----------
        if event == self.TOGGLE:
            visible_now = win[self.LIBCOL].visible
            if not visible_now:
                win[self.LIBTXT].update(self._load_lib_text(root))
            win[self.LIBCOL].update(visible=not visible_now)
            win[self.LISTCOL].update(visible=False)
            win[self.TOGGLE].update(text="Hide structure info" if not visible_now
                                    else "Show structure info")
            win[self.LISTBTN].update(text="Show components")
            return None

        # ---------- LIST COMPONENTS (toggle) ----------
        if event == self.LISTBTN:
            visible_now = win[self.LISTCOL].visible
            if visible_now:  # hide
                win[self.LISTCOL].update(visible=False)
                win[self.LISTBTN].update(text="Show components")
                return None
            # show list
            comps = self._scan_components(root) if self._structure_ok(root) else []
            win[self.COMPLIST].update(values=comps)
            win[self.LISTCOL].update(visible=True)
            win[self.LIBCOL].update(visible=False)
            win[self.LISTBTN].update(text="Hide components")
            win[self.TOGGLE].update(text="Show structure info")
            return f"📚 {len(comps)} component file(s) found."

        # ---------- SAVE properties ----------
        if event == self.SAVE:
            try:
                (root / "library.properties").write_text(vals[self.LIBTXT], encoding="utf-8")
                return "💾 Saved library.properties"
            except Exception as e:
                return f"❌ Error saving: {e}"

        return None
