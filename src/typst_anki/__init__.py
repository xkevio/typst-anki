from aqt.qt import *
from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons
from .typst_input_dialog import TypstInputDialog
from sys import platform

import re
import sys 
import os
import tempfile
import json

from .preamble import PREAMBLE
from .anki_version_detection import anki_point_version

addon_path = os.path.dirname(__file__)
sys.path.append(os.path.join(addon_path, "lib"))

# FIXME: Workaround as I cannot get MacOS to find any kind of pandoc otherwise.
if platform == "darwin":
    os.environ.setdefault('PYPANDOC_PANDOC', '/usr/local/bin/pandoc')

import typst
import pypandoc

# Convert Typst Math to MathJax via Pandoc.
def convert_typst_to_mathjax(typst_math: str) -> str:
    mathjax_output = pypandoc.convert_text(f"{PREAMBLE}\n${typst_math}$", "html", "typst", extra_args=["--mathjax"])
    return re.sub("<\/?p>", "", mathjax_output)

# Convert Typst Math to SVG via the Typst compiler.
def generate_typst_svg(typst_math: str) -> bytes:
    # Pre-amble for inline typst math
    final_code = PREAMBLE + "\n" + f"$ {typst_math} $" 
    
    # Create temp file for typst code
    with tempfile.NamedTemporaryFile(mode = "w", suffix = ".typ") as tmp:
        tmp.write(final_code)
        tmp.flush()
        return typst.compile(tmp.name, format = "svg")

# Alternative option: write inline math between dollar signs, extract and replace.
def collect_and_replace(editor: Editor):
    current_field_idx = editor.currentField
    
    fields = editor.note.col.models.current()["flds"];
    field_names = [f["name"] for f in fields];
    current_field = field_names[current_field_idx]

    new_front = re.sub("\$(.*?)\$", lambda match: convert_typst_to_mathjax(match.group(1)), editor.note["Front"])
    new_back = re.sub("\$(.*?)\$", lambda match: convert_typst_to_mathjax(match.group(1)), editor.note["Back"])

    if current_field == "Front":
        editor.note["Front"] = new_front
    elif current_field == "Back":
        editor.note["Back"] = new_back
    else:
        showInfo("Select a text field!")

    editor.setNote(editor.note)

# Open an input dialog for typst input, convert and append to note.
def typst_editor(editor: Editor):
    input_dialog = TypstInputDialog()
    input_dialog.input.setFocus()
    input_dialog.button.setDefault(True)
    
    if input_dialog.exec():
        # Get front or back side and insert SVG/MathJax
        input_text, option = input_dialog.text_and_option()
        output_text = (generate_typst_svg(input_text).decode("utf-8").replace("<svg", "<svg style=\"vertical-align: middle\"") 
                       if option == "Typst SVG" 
                       else convert_typst_to_mathjax(input_text)) 

        # see: https://github.com/ijgnd/anki__editor_add_table/commit/f236029d43ae8f65fa93a684ba13ea1bdfe64852
        js_insert_html = (f"document.execCommand('insertHTML', false, {json.dumps(output_text)});"
                          if anki_point_version <= 49
                          else f"setTimeout(function() {{ document.execCommand('insertHTML', false, {json.dumps(output_text)}); }}, 50);")

        editor.web.evalWithCallback(js_insert_html, editor.saveNow(editor.loadNoteKeepingFocus))

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

    typst_r_button = editor.addButton(
        icon = None,
        cmd = "typst_r_button",
        func = collect_and_replace,
        tip = "Replace and Insert Typst Math",
        label = "Typst Replace",
        keys = "Ctrl+M, R"
    )

    buttons.extend([typst_button, typst_r_button])
    return buttons
    
editor_did_init_buttons.append(add_typst_button)
