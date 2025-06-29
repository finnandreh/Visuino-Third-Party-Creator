import PySimpleGUI as sg
from pathlib import Path
from glob import glob


# ── helpers ─────────────────────────────────────────────────────────────
def _default_arduino_lib_dir() -> Path:
    h = Path.home()
    return h / "Documents" / "Arduino" / "libraries" if (h / "Documents").exists() \
           else h / "Arduino" / "libraries"


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
    VERIFY, CREATE, STRUCT = "-VERIFY-", "-CREATE-", "-STRUCT-"
    TOGGLE, SAVE           = "-TOGGLELIB-", "-SAVELIB-"
    LISTBTN                = "-LISTCOMP-"
    NEWBTN, EDITBTN        = "-NEWCOMP-", "-EDITCOMP-"
    WORKDIR, NICK          = "-WORKDIR-", "-NICKNAME-"
    LIBTXT, LIBCOL         = "-LIBTXT-", "-LIBCOL-"
    LISTCOL, COMPLIST      = "-LISTCOL-", "-COMPLIST-"

    def __init__(self) -> None:
        default = _default_arduino_lib_dir()

        # ── controls top rows ─────────────────────────────────────────
        self.layout = [
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
                sg.Button("Create component", key=self.NEWBTN, disabled=True),
                sg.Button("Edit component", key=self.EDITBTN, disabled=True),
            ],
        ]

        # ── shared area (editor ↔ list) ───────────────────────────────
        shared = sg.Column(
            [[
                sg.Column(
                    [
                        [sg.Text("library.properties content:")],
                        [sg.Multiline("", size=(80, 12), key=self.LIBTXT)],
                        [sg.Button("Save properties", key=self.SAVE)],
                    ],
                    key=self.LIBCOL, visible=False, expand_x=True,
                ),
                sg.Column(
                    [
                        [sg.Text("Components in library:")],
                        [sg.Listbox(values=[], size=(80, 12),
                                    key=self.COMPLIST, enable_events=True)],
                    ],
                    key=self.LISTCOL, visible=False, expand_x=True,
                ),
            ]],
            expand_x=True,
        )
        self.layout.append([shared])

    # ── helpers ───────────────────────────────────────────────────────
    def _effective_path(self, vals) -> Path:
        base = Path(vals[self.WORKDIR]).expanduser()
        nick = vals[self.NICK].strip()
        return base / nick if nick else base

    def _structure_ok(self, root: Path) -> bool:
        return all((root / p).exists() for p in
                   ["SRC", "Visuino/images", "library.properties", "visuino.library"])

    def _scan_components(self, root: Path, nickname: str) -> list[str]:
        pat = f"{nickname}*.vcomp" if nickname else "*.vcomp"
        out = []
        for p in glob(str(root / "Visuino" / pat)):
            stem = Path(p).stem
            if nickname and stem.startswith(nickname + "."):
                stem = stem[len(nickname) + 1:]
            out.append(stem)
        return out

    # --- create .vcomp skeleton --------------------------------------
    def _create_component_file(self, root: Path, nick: str, comp: str) -> str:
        if not comp:
            return "⚠️ No component name entered."
        fname = f"{nick}.{comp}.vcomp" if nick else f"{comp}.vcomp"
        fpath = root / "Visuino" / fname
        try:
            fpath.touch(exist_ok=False)
            return f"✅ Created {fname}"
        except FileExistsError:
            return f"⚠️ {fname} already exists."
        except Exception as e:
            return f"❌ Error creating component: {e}"

    # ── dispatcher ────────────────────────────────────────────────────
    def handle_event(self, event, vals, win) -> str | None:
        root = self._effective_path(vals)
        nick = vals[self.NICK].strip()

        # ---------- VERIFY ----------
        if event == self.VERIFY:
            if root.exists():
                if self._structure_ok(root):
                    # structure already fine
                    for k in (self.TOGGLE, self.LISTBTN):
                        win[k].update(disabled=False)
                    win[self.STRUCT].update(disabled=True)
                    win[self.CREATE].update(disabled=True)
                    win[self.EDITBTN].update(disabled=True)
                    return "✅ Directory & structure OK."
                else:
                    # dir exists, structure missing → enable STRUCT
                    win[self.CREATE].update(disabled=True)
                    win[self.STRUCT].update(disabled=False)
                    return "ℹ️ Directory exists, create structure next."
            else:
                # dir missing → enable CREATE
                win[self.CREATE].update(disabled=False)
                win[self.STRUCT].update(disabled=True)
                return "👍 Ready to create directory."

        # ---------- CREATE ----------
        if event == self.CREATE:
            try:
                root.mkdir(parents=True, exist_ok=False)
                win[self.CREATE].update(disabled=True)
                win[self.STRUCT].update(disabled=False)
                return "✅ Directory created."
            except Exception as e:
                return f"❌ {e}"

        # ---------- CREATE STRUCTURE ----------
        if event == self.STRUCT:
            try:
                (root / "SRC").mkdir(parents=True, exist_ok=True)
                (root / "Visuino" / "images").mkdir(parents=True, exist_ok=True)
                (root / "visuino.library").touch(exist_ok=True)
                if not (root / "library.properties").exists():
                    (root / "library.properties").write_text(_TEMPLATE_PROPERTIES)
                # show editor panel
                win[self.LIBTXT].update((root / "library.properties").read_text())
                win[self.LIBCOL].update(visible=True)
                win[self.TOGGLE].update(disabled=False, text="Hide structure info")
                win[self.LISTBTN].update(disabled=False)
                win[self.NEWBTN].update(disabled=True)
                win[self.STRUCT].update(disabled=True)
                return "✅ Structure scaffolded."
            except Exception as e:
                return f"❌ {e}"

        # ---------- TOGGLE editor ----------
        if event == self.TOGGLE:
            vis = win[self.LIBCOL].visible
            win[self.LIBCOL].update(visible=not vis)
            win[self.LISTCOL].update(visible=False)
            win[self.TOGGLE].update(text="Hide structure info" if not vis
                                    else "Show structure info")
            win[self.LISTBTN].update(text="Show components")
            win[self.NEWBTN].update(disabled=True)
            win[self.EDITBTN].update(disabled=True)
            if not vis:
                win[self.LIBTXT].update((root / "library.properties").read_text())
            return None

        # ---------- LIST components ----------
        if event == self.LISTBTN:
            vis = win[self.LISTCOL].visible
            if vis:
                win[self.LISTCOL].update(visible=False)
                win[self.LISTBTN].update(text="Show components")
                win[self.NEWBTN].update(disabled=True)
                win[self.EDITBTN].update(disabled=True)
                return None
            comps = self._scan_components(root, nick)
            win[self.COMPLIST].update(values=comps)
            win[self.LISTCOL].update(visible=True)
            win[self.LIBCOL].update(visible=False)
            win[self.LISTBTN].update(text="Hide components")
            win[self.NEWBTN].update(disabled=False)
            win[self.EDITBTN].update(disabled=True)
            win[self.TOGGLE].update(text="Show structure info")
            return f"📚 {len(comps)} component(s)."

        # ---------- LIST selection ----------
        if event == self.COMPLIST:
            win[self.EDITBTN].update(disabled=not vals[self.COMPLIST])
            return None

        # ---------- placeholder Create/Edit component ----------
                # ---------- CREATE component ----------
        if event == self.NEWBTN:
            nick = vals[self.NICK].strip()
            comp = sg.popup_get_text("New component name:",
                                     title="Create component")
            if comp is None:        # user cancelled
                return None
            comp = comp.strip()
            msg = self._create_component_file(root, nick, comp)
            # refresh list
            files = self._scan_components(root, nick)
            win[self.COMPLIST].update(values=files)
            return msg


        # ---------- SAVE ----------
        if event == self.SAVE:
            (root / "library.properties").write_text(vals[self.LIBTXT], encoding="utf-8")
            return "💾 Saved library.properties"

        return None
