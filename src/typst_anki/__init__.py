from aqt.qt import *
from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons
from aqt.utils import showInfo

import sys 
import os
import tempfile

from sys import platform

addon_path = os.path.dirname(__file__)
sys.path.append(os.path.join(addon_path, "lib_linux" if platform == "linux" else "lib_win"))

import typst

def eval_typst(typst_math: str) -> bytes:
    # Pre-amble for inline typst math
    preamble = "#set page(width: auto, height: auto, margin: (x: 0em, y: 0.25em))\n#set text(white)"
    final_code = preamble + "\n" + f"$ {typst_math} $" 
    
    # Create temp file for typst code
    with tempfile.NamedTemporaryFile(mode = "w", suffix = ".typ") as tmp:
        tmp.write(final_code)
        tmp.flush()
        return typst.compile(tmp.name, format = "svg")

def open_typst_editor(editor: Editor):
    current_field_idx = editor.currentField
    input_text, ok = QInputDialog.getText(editor.widget, "Typst Math (Inline)", "Enter text:")
    if ok and input_text:
        # Get front or back side and insert SVG
        svg_str = eval_typst(input_text).decode("utf-8")

        fields = editor.note.col.models.current()["flds"];
        field_names = [f["name"] for f in fields];
        current_field = field_names[current_field_idx]

        if current_field == "Front":
            editor.note["Front"] += svg_str
        elif current_field == "Back":
            editor.note["Back"] += svg_str
        else:
            showInfo("Select a text field!")

        editor.setNote(editor.note)

def add_typst_button(buttons, editor: Editor):
    typst_button = editor.addButton(
        icon = None,
        cmd = "typst_button",
        func = open_typst_editor,
        tip = "Open Typst Math Editor",
        label = "Typst"
    )

    buttons.append(typst_button)
    return buttons
    
editor_did_init_buttons.append(add_typst_button)
