from aqt import mw
from aqt.qt import *

import inspect

class TypstInputDialog(QDialog):
    def __init__(self, parent=None, display_math=False):
        QDialog.__init__(self, parent)

        window_title = "Input Typst math " + ( "(inline)" if not display_math else "(block)" ) + "..."
        window_size = (300, 100) if not display_math else (500, 300)
        window_editor = QLineEdit() if not display_math else QTextEdit()

        self.setWindowTitle(window_title)
        self.resize(window_size[0], window_size[1])

        config = mw.addonManager.getConfig(__name__)

        self.display_math = display_math
        self.input = window_editor

        self.button = QPushButton("Convert")
        self.button.setAutoDefault(False)
        self.button.clicked.connect(self.accept)

        self.info_label_text = inspect.cleandoc(
            """Center-align the inserted equations. 

            SVGs will be displayed as a block with CSS."""
        )
        self.math_jax = QRadioButton("MathJax" if not display_math else "MathJax (with `\[...\]` delimiters)")
        self.typst_svg = QRadioButton("Typst SVG" if not display_math else "Typst SVG (with `display: block`)")

        if config["render-type"] == "mathjax":
            self.math_jax.setChecked(True)
        else:
            self.typst_svg.setChecked(True)

        self.radio_group = [self.math_jax, self.typst_svg]
        radio_layout = QVBoxLayout() if not display_math else QHBoxLayout()

        if display_math:
            self.input.setPlaceholderText(self.info_label_text)
        
        radio_layout.addWidget(self.math_jax)
        radio_layout.addWidget(self.typst_svg)

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.input)
        form_layout.addWidget(self.button)

        hbox_layout = QHBoxLayout() if not display_math else QVBoxLayout()
        hbox_layout.addLayout(radio_layout)
        hbox_layout.addLayout(form_layout)

        self.input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setLayout(hbox_layout)
        
    def text_and_option(self) -> tuple[str, str]:
        input_text = self.input.text() if not self.display_math else self.input.toPlainText()
        selected_option = [r.text() for r in self.radio_group if r.isChecked()][0]
        return input_text, selected_option
