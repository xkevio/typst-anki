# typst-anki

Convert `typst` math code to `MathJax` (via pandoc) or `SVG`s (via the typst compiler) for use in Anki flashcards. Click either the `Typst` button or press <kbd>Ctrl + M, T</kbd>.

> [!IMPORTANT]  
> Use `MathJax` for consistency. The `SVG`s directly from Typst are very misaligned inside the text field.

## Installation

```sh 
git clone git@github.com:xkevio/typst-anki.git
cd typst-anki/src/typst_anki

mkdir lib_{win, linux} # <- depending on your system!
pip download typst -d ./lib_{win, linux}/ # <- unpack the .whl file!
pip download pypandoc -d ./lib_{win, linux}/ # <- unpack the .whl file!

zip -r typst_anki.zip __init__.py typst_input_dialog.py manifest.json ./lib_{win, linux}/
```

## TODO 

- [ ] **Inconsistency:** `Typst SVG` option uses display math as otherwise small margins will cut parts off while `MathJax` always uses inline math for now.
    
