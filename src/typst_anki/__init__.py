from aqt.qt import *
from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons
from .typst_input_dialog import TypstInputDialog

import re
import sys 
import os
import tempfile
import json

addon_path = os.path.dirname(__file__)
sys.path.append(os.path.join(addon_path, "lib"))

import typst
import pypandoc

# Convert Typst Math to MathJax via Pandoc.
def convert_typst_to_mathjax(typst_math: str) -> str:
    mathjax_output = pypandoc.convert_text(f"${typst_math}$", "html", "typst", extra_args=["--mathjax"])
    return re.sub("<\/?p>", "", mathjax_output)

# Convert Typst Math to SVG via the Typst compiler.
def generate_typst_svg(typst_math: str) -> bytes:
    # Pre-amble for inline typst math
    preamble = "#set page(width: auto, height: auto, margin: (x: 0em, y: 0.25em))\n#set text(white)"
    final_code = preamble + "\n" + f"$ {typst_math} $" 
    
    # Create temp file for typst code
    with tempfile.NamedTemporaryFile(mode = "w", suffix = ".typ") as tmp:
        tmp.write(final_code)
        tmp.flush()
        return typst.compile(tmp.name, format = "svg")

# Open an input dialog for typst input, convert and append to note.
def typst_editor(editor: Editor):
    input_dialog = TypstInputDialog()
    input_dialog.input.setFocus()
    input_dialog.button.setDefault(True)
    
    if input_dialog.exec():
        # Get front or back side and insert SVG/MathJax
        input_text, option = input_dialog.text_and_option()
        output_text = (generate_typst_svg(input_text).decode("utf-8") 
                       if option == "Typst SVG" 
                       else convert_typst_to_mathjax(input_text)) 

        editor.web.eval(f"document.execCommand('insertHTML', false, {json.dumps(output_text)});")
        editor.saveNow(editor.loadNoteKeepingFocus)

# Add and register new editor button.
def add_typst_button(buttons, editor: Editor):
    typst_button = editor.addButton(
        icon = None,
        cmd = "typst_button",
        func = typst_editor,
        tip = "Open Typst Math Editor",
        label = "Typst",
        keys = "Ctrl+M, T"
    )

    buttons.append(typst_button)
    return buttons
    
editor_did_init_buttons.append(add_typst_button)
