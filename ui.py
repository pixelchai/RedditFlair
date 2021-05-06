from qtpy import QtGui, QtCore
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.panel_top = QWidget(self.central_widget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.panel_top.sizePolicy().hasHeightForWidth())
        self.panel_top.setSizePolicy(sizePolicy)
        self.layout_top = QHBoxLayout(self.panel_top)

        self.label_subreddit = QLabel(self.panel_top, text="Subreddit: ")
        self.layout_top.addWidget(self.label_subreddit)

        self.edit_subreddit = QLineEdit(self.panel_top)
        self.layout_top.addWidget(self.edit_subreddit)

        self.label_flair = QLabel(self.panel_top, text="Flair: ")
        self.layout_top.addWidget(self.label_flair)

        self.edit_flair = QLineEdit(self.panel_top)
        self.layout_top.addWidget(self.edit_flair)

        self.btn_go = QPushButton(self.panel_top, text="Go")
        self.layout_top.addWidget(self.btn_go)

        self.central_layout.addWidget(self.panel_top)

        self.canvas = QWidget(self.central_widget)
        self.central_layout.addWidget(self.canvas)

        self.panel_bottom = QWidget(self.central_widget)
        sizePolicy.setHeightForWidth(self.panel_bottom.sizePolicy().hasHeightForWidth())
        self.panel_bottom.setSizePolicy(sizePolicy)
        self.layout_bottom = QHBoxLayout(self.panel_bottom)

        self.btn_prev = QPushButton(self.panel_bottom, text="Prev (A)")
        self.layout_bottom.addWidget(self.btn_prev)

        self.btn_next = QPushButton(self.panel_bottom, text="Next (D)")
        self.layout_bottom.addWidget(self.btn_next)

        self.btn_external = QPushButton(self.panel_bottom, text="Open Externally (X)")
        self.layout_bottom.addWidget(self.btn_external)

        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout_bottom.addItem(horizontal_spacer)

        self.label_no_display = QLabel(self.panel_bottom, text="#0000")
        self.layout_bottom.addWidget(self.label_no_display)

        self.central_layout.addWidget(self.panel_bottom)

        self.setCentralWidget(self.central_widget)