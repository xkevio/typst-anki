from aqt import mw
from aqt.qt import *

class TypstInputDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Input Typst...")
        self.resize(300, 100)

        config = mw.addonManager.getConfig(__name__)

        self.input = QLineEdit()
        self.button = QPushButton("Convert")
        self.button.setAutoDefault(False)
        self.button.clicked.connect(self.accept)

        self.math_jax = QRadioButton("MathJax")
        self.typst_svg = QRadioButton("Typst SVG")

        if config["render-type"] == "mathjax":
            self.math_jax.setChecked(True)
        else:
            self.typst_svg.setChecked(True)

        self.radio_group = [self.math_jax, self.typst_svg]

        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.math_jax)
        radio_layout.addWidget(self.typst_svg)

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.input)
        form_layout.addWidget(self.button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(radio_layout)
        hbox_layout.addLayout(form_layout)

        self.input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setLayout(hbox_layout)
        
    def text_and_option(self) -> tuple[str, str]:
        input_text = self.input.text()
        selected_option = [r.text() for r in self.radio_group if r.isChecked()][0]
        return input_text, selected_option
