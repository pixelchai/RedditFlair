from qtpy import QtGui, QtCore
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import *
import requests

class CanvasWidget(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._off_x = 0
        self._off_y = 0
        self._scale = 1

        self._pixmap = None

    def _recalc_im(self):
        if self._pixmap is None:
            return

        w, h = self._pixmap.width(), self._pixmap.height()
        cw, ch = self.width(), self.height()

        self._scale = max(0, min(cw / w, ch / h))
        self._off_x, self._off_y = cw/2 - w*self._scale/2, ch/2 - h*self._scale/2

    def set_image(self, qim):
        self._pixmap = QtGui.QPixmap.fromImage(qim.copy())
        self._recalc_im()

    def resizeEvent(self, event):
        self._recalc_im()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # paint background
        brush = QtGui.QBrush(Qt.black, Qt.Dense4Pattern)
        painter.fillRect(0, 0, self.width(), self.height(), brush)

        # paint pixmap
        if self._pixmap is not None:
            painter.drawPixmap(
                self._off_x,
                self._off_y,
                self._pixmap.width() * self._scale,
                self._pixmap.height() * self._scale,
                self._pixmap
            )

class MainWindow(QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # region widgets
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

        # self.panel_centre = QWidget(self.central_widget)
        # self.layout_centre = QVBoxLayout(self.panel_centre)
        #
        # self.label_title = QLabel(self.panel_centre, text="TITLE HERE")
        # sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        # self.label_title.setSizePolicy(sizePolicy)
        # self.layout_centre.addWidget(self.label_title)
        #
        # self.canvas = QWidget(self.panel_centre)
        # self.layout_centre.addWidget(self.canvas)
        #
        # self.central_layout.addWidget(self.panel_centre)
        self.canvas = CanvasWidget(self.central_widget)
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
        # endregion

        # test:
        url = 'https://source.unsplash.com/random'
        data = requests.get(url, stream=True).content

        image = QtGui.QImage()
        image.loadFromData(data)

        self.canvas.set_image(image)