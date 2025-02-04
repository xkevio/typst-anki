from aqt.qt import *

class PreambleEditDialog(QDialog):
    def __init__(self, parent=None, preamble: str = None):
        QDialog.__init__(self, parent)

        self.resize(500, 500)
        self.setWindowTitle("Edit preamble...")

        self.input = QTextEdit()
        self.input.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.input.setText(preamble)

        save_btn = QPushButton("Save (restart to take effect)")
        save_btn.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(save_btn)

        self.setLayout(layout)