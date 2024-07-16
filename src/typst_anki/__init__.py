from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from aqt.editor import Editor
from aqt.gui_hooks import main_window_did_init, editor_did_init_buttons

import sys 
import os
import tempfile
from pathlib import Path
import json

addon_path = os.path.dirname(__file__)
sys.path.append(os.path.join(addon_path, "lib"))

import typst

def eval_typst(typst_math: str) -> bytes:
    # Pre-amble for inline typst math
    preamble = "#set page(width: auto, height: auto, margin: .5em)\n#set text(white)"
    final_code = preamble + "\n" + f"$ {typst_math} $" 
    
    # Create temp file for typst code
    with tempfile.NamedTemporaryFile(mode = "w", suffix = ".typ") as tmp:
        tmp.write(final_code)
        tmp.flush()
        return typst.compile(tmp.name, format = "svg")

def open_typst_editor(editor: Editor):
    input_text, ok = QInputDialog.getText(editor.widget, "Typst Math (Inline)", "Enter text:")
    if ok and input_text:
       svg_bytes = eval_typst(input_text)

       # Get front or back side and insert SVG
       # editor.web.eval(f"setSideHTML('front', {json.dumps(str(svg_bytes))})")
       editor.web.eval(f"setSideHTML('back', `{svg_bytes.decode("utf-8")}`)")

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
