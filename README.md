# typst-anki

Convert `typst` math code to `MathJax` (via pandoc) or `SVG`s (via the typst compiler) for use in Anki flashcards. Click either the `Typst` button or press <kbd>Ctrl + M, T</kbd>. Add custom functions inside [`preamble.py`](src/typst_anki/preamble.py)!

> [!IMPORTANT]  
> On MacOS, make sure `pandoc` is available under `/usr/local/bin/pandoc` otherwise Anki cannot find it.

## Installation

```sh
git clone git@github.com:xkevio/typst-anki.git
cd typst-anki/src/typst_anki

mkdir lib # <- this stores external dependencies for Anki.
pip install typst -t ./lib/
pip install pypandoc -t ./lib/

zip -r typst_anki.zip __init__.py typst_input_dialog.py manifest.json ./lib/
```

Then, open Anki > Tools > Addons > Install from file > `typst_anki.zip`.
(Pandoc needs to be installed on your system and available via `$PATH`.) Or, if you wish, use [`just`](https://github.com/casey/just).

## TODO 

- [ ] **Feature:** Use Typst HTML export when it releases (MathML). 
- [ ] **Inconsistency:** `Typst SVG` option uses display math as otherwise small margins will cut parts off while `MathJax` always uses inline math for now.
- [ ] **Issue:** On some systems, inserting MathJax will first just display the raw MathJax markup and only transform after user interaction.
    
