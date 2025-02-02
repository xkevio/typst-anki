# Typst Math for Anki

### `"render-type"`: `"mathjax"` (default) or `"svg"`
  
- Whether this add-on should export to MathJax via pandoc or invoke the typst compiler and generate an SVG image. Affects the default selection for the editor modal and the replacing functionality.

### `"preamble"`: `"user_files/preamble.typ"` (default)

- The path to a custom preamble typst file for specifying custom functions, page dimensions or text size and color. Default is inside the `user_files` folder in the root folder of this add-on. (TODO!)
