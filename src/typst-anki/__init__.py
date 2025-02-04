from typing import Any, cast
from aqt import mw
from aqt.qt import *
from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons, webview_did_receive_js_message, editor_did_init_shortcuts
from aqt.utils import showInfo
from sys import platform
from enum import Enum
from functools import partial

import re
import sys 
import os
import tempfile
import json
import base64

from .preamble import PREAMBLE
from .anki_version_detection import anki_point_version
from .typst_input_dialog import TypstInputDialog

addon_path = os.path.dirname(__file__)
sys.path.append(os.path.join(addon_path, "lib"))

# FIXME: Workaround as I cannot get MacOS to find any kind of pandoc otherwise.
if platform == "darwin":
    os.environ.setdefault("PYPANDOC_PANDOC", "/usr/local/bin/pandoc")

import typst
import pypandoc

config = mw.addonManager.getConfig(__name__)


# ----- Conversion utility: Typst -> MathJax, Typst -> SVG, SVG -> Base64. ----- #

class Export(Enum):
    MATHJAX = 1
    SVG = 2

def generate_typst(typst_math: str, render_type: Export, display_math: bool) -> str:
    output = ""

    if render_type == Export.MATHJAX:
        typst_math = " " + typst_math + " " if display_math else typst_math
        output = convert_typst_to_mathjax(typst_math)
    else:
        output = svg_to_base64_img(generate_typst_svg(typst_math), display_math)

    return output

def convert_typst_to_mathjax(typst_math: str) -> str:
    """Returns MathJax markup by calling a pandoc process with `typst_math` as input."""
    mathjax_output = pypandoc.convert_text(f"{PREAMBLE}\n${typst_math}$", "html", "typst", extra_args=["--mathjax"])
    return re.sub("<\/?p>", "", mathjax_output)

def generate_typst_svg(typst_math: str) -> bytes:
    """Returns a sequence of bytes representing an SVG string obtained from compiling `typst_math` to SVG."""

    # Pre-amble for inline typst math.
    final_code = PREAMBLE + "\n" + f"$ {typst_math} $" 
    
    # Create temp file for typst code.
    with tempfile.NamedTemporaryFile(mode = "w", suffix = ".typ") as tmp:
        tmp.write(final_code)
        tmp.flush()
        return typst.compile(tmp.name, format = "svg")
    
def svg_to_base64_img(svg: bytes, display_math=False) -> str:
    """Returns an HTML img tag with the `svg` byte sequence encoded as base64 as the source."""
    svg_b64 = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
    return (f'<img style="vertical-align: middle;" src="{svg_b64}">' 
            if not display_math 
            else f'<img style="display: block; margin-left: auto; margin-right: auto;" src="{svg_b64}">')


# ----- Replace functionality, editor input and callback definition for the context menu. ----- #

def collect_and_replace(editor: Editor):
    """Collects all text between dollar signs and converts it to MathJax in-place."""

    if editor.currentField is None:
        showInfo("Select a text field!")
        return 
    
    fields = editor.note.col.models.current()["flds"]
    field_names = [f["name"] for f in fields]
    current_field = field_names[editor.currentField]

    export = Export.MATHJAX if config["render-type"] == "mathjax" else Export.SVG
    display_math = lambda x: x.startswith(" ") and x.endswith(" ")

    new_note_text = re.sub(
        "\$(.*?)\$", 
        lambda match: generate_typst(match.group(1), export, display_math(match.group(1))), 
        editor.note[current_field]
    )

    editor.note[current_field] = new_note_text
    editor.setNote(editor.note)

def typst_editor(editor: Editor, display_math=False):
    """Open an input dialog for typst input, convert and append to note.

    - If the option checkbox is set to MathJax, a pandoc process is called to convert typst math.
    - If the option checkbox is set to SVG, the typst compiler is called directly and exports as SVG.

    Calls `evalWithCallback` to append MathJax/SVG with `insertHTML` via Javascript.
    """

    input_dialog = TypstInputDialog(display_math=display_math)
    input_dialog.input.setFocus()
    input_dialog.button.setDefault(True)
    
    # Get front or back side and insert SVG/MathJax.
    if input_dialog.exec():
        input_text, option = input_dialog.text_and_option()

        # Convert SVG to base64 and enclose in <img> tag for vertical alignment and easier cursor movement.
        output_text = generate_typst(input_text, Export.SVG if option.startswith("Typst SVG") else Export.MATHJAX, display_math)

        # see: https://github.com/ijgnd/anki__editor_add_table/commit/f236029d43ae8f65fa93a684ba13ea1bdfe64852.
        js_insert_html = (f"document.execCommand('insertHTML', false, {json.dumps(output_text)});"
                          if anki_point_version <= 49
                          else f"""
                            setTimeout(() => {{ document.execCommand('insertHTML', false, {json.dumps(output_text)}); }}, 20);
                            { 'setTimeout(() => pycmd("reload_note"), 40);' if not option.startswith("Typst SVG") else "" }
                            """)

        editor.web.eval(js_insert_html)

# TODO: preamble settings.
def settings_cb(_editor: Editor):
    preamble_settings = QDialog()

    preamble_settings.resize(500, 500)
    preamble_settings.setWindowTitle("Edit preamble...")

    preamble_input = QTextEdit()
    preamble_input.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    preamble_input.setPlaceholderText(PREAMBLE)

    layout = QVBoxLayout()
    layout.addWidget(preamble_input)
    layout.addWidget(QPushButton("Save"))

    preamble_settings.setLayout(layout)
    preamble_settings.exec()

def typst_menu_cb(editor: Editor):
    """Callback for the context menu of the dedicated "typst" button.

    Shows a menu similar to the native "Equations" menu with the following items:
    - Typst Math inline (opens the editor and uses inline math),
    - Typst Math block (opens the editor and uses display math),
    - Typst Math replace (replaces all instances of typst math between dollar signs with rendered math),
    - Edit preamble (opens a settings menu for modifying the preamble)
    """

    menu = QMenu(editor.mw)
    menu.setContentsMargins(5, 5, 5, 5)

    menu_and_action = [
        ("Typst Math inline", "Ctrl+M, T", partial(typst_editor, editor)),
        ("Typst Math block", "Ctrl+M, B", partial(typst_editor, editor, True)),
        ("Typst Math replace", "Ctrl+M, R", partial(collect_and_replace, editor)),
        ("---", None, None),
        ("Edit preamble...", QKeySequence(), partial(settings_cb, editor))
    ]

    for action, shortcut, cmd in menu_and_action:
        if action == "---":
            menu.addSeparator()
        else:
            act = QAction(action, menu)
            act.setShortcutVisibleInContextMenu(True)
            act.setShortcut(shortcut)

            if not cmd is None:
                act.triggered.connect(cmd)

            menu.addAction(act)

    pos = QCursor.pos()
    menu.exec(pos)


# ----- Registration of GUI hooks for proper note reloading, shortcuts and buttons. ----- #

def reload_note(handled: tuple[bool, Any], cmd: str, ctx: Any) -> tuple[bool, Any]:
    """Reload note callback for saving unsaved edits and loading note via `pycmd()`."""
    
    if cmd != "reload_note" or not isinstance(ctx, Editor):
        return handled 
    
    editor = cast(Editor, ctx)
    editor.saveNow(editor.loadNoteKeepingFocus)

    return (True, None)

def init_shortcuts(keys: list[tuple], editor: Editor):
    """Initialize and add shortcuts to global shortcut hook."""

    keys.extend([
        ("Ctrl+M, T", partial(typst_editor, editor)),
        ("Ctrl+M, B", partial(typst_editor, editor, True)),
        ("Ctrl+M, R", partial(collect_and_replace, editor)),
    ])

def add_typst_button(buttons, editor: Editor):
    """Appends the `typst` button opening a context menu with all the options."""

    typst_menu = editor.addButton(
        icon = None,
        cmd = "typst_menu",
        func = typst_menu_cb,
        tip = "Equations (Typst)",
        label = "𝕋ypst",
    )

    buttons.append(typst_menu)
    

editor_did_init_buttons.append(add_typst_button)
webview_did_receive_js_message.append(reload_note)
editor_did_init_shortcuts.append(init_shortcuts)
