from aqt.qt import *
from aqt.editor import Editor
from aqt.gui_hooks import editor_did_init_buttons
from aqt.utils import showInfo
from sys import platform

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

# ----------------------------------------------------- #

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
    
def svg_to_base64_img(svg: bytes) -> str:
    """Returns an HTML img tag with the `svg` byte sequence encoded as base64 as the source."""
    svg_b64 = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
    return f'<img style="vertical-align: middle;" src="{svg_b64}">'

# ----------------------------------------------------- #

def collect_and_replace(editor: Editor):
    """Collects all text between dollar signs and converts it to MathJax in-place."""

    if editor.currentField is None:
        showInfo("Select a text field!")
        return 
    
    fields = editor.note.col.models.current()["flds"]
    field_names = [f["name"] for f in fields]
    current_field = field_names[editor.currentField]

    new_note_text = re.sub(
        "\$(.*?)\$", 
        lambda match: convert_typst_to_mathjax(match.group(1)), 
        editor.note[current_field]
    )

    editor.note[current_field] = new_note_text
    editor.setNote(editor.note)

def typst_editor(editor: Editor):
    """Open an input dialog for typst input, convert and append to note.

    - If the option checkbox is set to MathJax, a pandoc process is called to convert typst math.
    - If the option checkbox is set to SVG, the typst compiler is called directly and exports as SVG.

    Calls `evalWithCallback` to append MathJax/SVG with `insertHTML` via Javascript.
    """

    input_dialog = TypstInputDialog()
    input_dialog.input.setFocus()
    input_dialog.button.setDefault(True)
    
    # Get front or back side and insert SVG/MathJax.
    if input_dialog.exec():
        input_text, option = input_dialog.text_and_option()

        # Convert SVG to base64 and enclose in <img> tag for vertical alignment and easier cursor movement.
        svg_string = svg_to_base64_img(generate_typst_svg(input_text))
        output_text = svg_string if option == "Typst SVG" else convert_typst_to_mathjax(input_text)

        # see: https://github.com/ijgnd/anki__editor_add_table/commit/f236029d43ae8f65fa93a684ba13ea1bdfe64852
        js_insert_html = (f"document.execCommand('insertHTML', false, {json.dumps(output_text)});"
                          if anki_point_version <= 49
                          else f"setTimeout(function() {{ document.execCommand('insertHTML', false, {json.dumps(output_text)}); }}, 40);")

        editor.web.evalWithCallback(js_insert_html, editor.saveNow(editor.loadNote))

def add_typst_button(buttons, editor: Editor):
    """Returns an array of two editor buttons (Typst Editor, Typst Replace)."""
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
