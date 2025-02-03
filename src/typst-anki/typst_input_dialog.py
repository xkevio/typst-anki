from aqt import mw
from aqt.qt import *

class TypstInputDialog(QDialog):
    def __init__(self, parent=None, display_math=False):
        QDialog.__init__(self, parent)

        config = mw.addonManager.getConfig(__name__)

        # --- Window configuration based on inline/display math. --- #

        window_title = "Input Typst math " + ( "(inline)" if not display_math else "(block)" ) + "..."
        window_size = (300, 100) if not display_math else (500, 300)
        window_editor = QLineEdit() if not display_math else QTextEdit()

        self.setWindowTitle(window_title)
        self.resize(window_size[0], window_size[1])

        self.display_math = display_math
        self.input = window_editor

        self.button = QPushButton("Convert")
        self.button.setAutoDefault(False)
        self.button.clicked.connect(self.accept)

        self.info_label_text = "Center-align the inserted equations.\n\nSVGs will be displayed as a block with CSS."
        self.math_jax = QRadioButton("MathJax" if not display_math else "MathJax (with `\[...\]` delimiters)")
        self.typst_svg = QRadioButton("Typst SVG" if not display_math else "Typst SVG (with `display: block`)")

        self.radio_group = {"mathjax": self.math_jax, "svg": self.typst_svg}
        self.radio_group[config["render-type"]].setChecked(True)

        # --- Layout configuration based on inline/display math. --- #

        radio_layout = QVBoxLayout() if not display_math else QHBoxLayout()
        radio_layout.addWidget(self.math_jax)
        radio_layout.addWidget(self.typst_svg)

        if display_math:
            self.input.setPlaceholderText(self.info_label_text)
        
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.input)
        form_layout.addWidget(self.button)

        hbox_layout = QHBoxLayout() if not display_math else QVBoxLayout()
        hbox_layout.addLayout(radio_layout)
        hbox_layout.addLayout(form_layout)

        self.input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setLayout(hbox_layout)
        
    def text_and_option(self) -> tuple[str, str]:
        """Returns a tuple of strings containing the text input and the chosen radio button option name."""

        input_text = self.input.text() if not self.display_math else self.input.toPlainText()
        selected_option = [r.text() for r in self.radio_group.values() if r.isChecked()][0]

        return input_text, selected_option
