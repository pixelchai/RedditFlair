from qtpy import QtGui, QtCore
from qtpy.QtCore import Qt, QTimer, QObject, Signal, QThread
from qtpy.QtWidgets import *
import collections
import requests
import core
import traceback
import webbrowser

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
        try:
            self._pixmap = QtGui.QPixmap.fromImage(qim.copy())
            self._recalc_im()
        except:
            traceback.print_exc()
            raise
        self.repaint()

    def clear_image(self):
        self._pixmap = None
        self.repaint()

    def resizeEvent(self, event):
        self._recalc_im()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # paint background
        brush = QtGui.QBrush(Qt.black, Qt.Dense4Pattern)
        painter.fillRect(0, 0, self.width(), self.height(), brush)

        try:
            # paint pixmap
            if self._pixmap is not None:
                painter.drawPixmap(
                    self._off_x,
                    self._off_y,
                    self._pixmap.width() * self._scale,
                    self._pixmap.height() * self._scale,
                    self._pixmap
                )
        except:
            traceback.print_exc()

class PostList:
    def __init__(self, gen=None, prefetch=5):
        self._prev = collections.deque(maxlen=50)
        self._next = collections.deque()
        self._cur = None

        self._gen = gen
        self.prefetch = prefetch

        self._no = 0

    def append(self, obj):
        self._next.append(obj)

    def next_count(self):
        return len(self._next)

    def next(self):
        if self._gen is not None:
            while self.next_count() < self.prefetch:
                self.append(next(self._gen))

        # raises IndexError if len(self._next) <= 0
        self._prev.append(self._cur)
        self._cur = self._next.popleft()
        self._no += 1
        return self._cur

    def prev_count(self):
        return len(self._prev)

    def prev(self):
        # raises IndexError if len(self._prev) <= 0
        self._next.appendleft(self._cur)
        self._cur = self._prev.pop()
        self._no -= 1
        return self._cur

    def cur(self):
        return self._cur

    def get_no(self) -> int:
        return self._no

    def clear(self):
        self._cur = None
        self._prev.clear()
        self._next.clear()
        self._no = 0

    def set_generator(self, gen):
        self.clear()
        self._gen = gen

class SubmissionLoader(QObject):
    """
    Worker class for lazily loading submission images
    """
    loaded = Signal(QtGui.QImage)
    done = Signal()

    def __init__(self, submission, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.submission = submission
        self.im = None
        self._title = None

    @property
    def title(self):
        if self._title is not None:
            return self._title
        else:
            return self.submission.title

    def _load_url(self, url):
        data = requests.get(url, stream=True).content

        try:
            image = QtGui.QImage()
            image.loadFromData(data)
            self.im = image

            print(f"{self.submission.id}: Loaded: {url}")
            self.loaded.emit(self.im)
        except:
            print(f"ERROR loading: {self.submission.id}: Loaded: {url}")
            traceback.print_exc()

    def load(self):
        try:
            self._title = self.submission.title
        except:
            pass

        try:
            for resolution in self.submission.preview["images"][0]["resolutions"]:
                try:
                    self._load_url(resolution["url"])
                except:
                    pass
        except AttributeError:
            pass  # continue to below

        self._load_url(self.submission.url)
        self.done.emit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.api = core.Api()
        self.post_list = PostList(prefetch=core.config.get("prefetch", 5))

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

        self.panel_centre = QWidget(self.central_widget)
        self.layout_centre = QVBoxLayout(self.panel_centre)

        self.label_title = QLabel(self.panel_centre, text="TITLE HERE")
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        self.layout_centre.addWidget(self.label_title)

        self.canvas = CanvasWidget(self.panel_centre)
        self.layout_centre.addWidget(self.canvas)

        self.central_layout.addWidget(self.panel_centre)

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

        self._skip_callback = self._btn_next_clicked

        self.btn_go.clicked.connect(self._btn_go_clicked)
        self.btn_next.clicked.connect(self._btn_next_clicked)
        self.btn_prev.clicked.connect(self._btn_prev_clicked)
        self.btn_external.clicked.connect(self._btn_external_clicked)

        QShortcut(QtGui.QKeySequence("D"), self, lambda: self._btn_next_clicked())
        QShortcut(QtGui.QKeySequence("A"), self, lambda: self._btn_prev_clicked())
        QShortcut(QtGui.QKeySequence("X"), self, lambda: self._btn_external_clicked())

        self.btn_next.setFocus()

        # need to keep reference to threads otherwise will get GC'd
        self._threads = []

        # load config
        try:
            self.edit_subreddit.setText(core.config["prev_subreddit"])
            self.edit_flair.setText(core.config["prev_flair"])
            self.btn_go.click()
        except:
            pass

    def _get_generator(self):
        def _handle_thread_termination(thread):
            try:
                thread.quit()
                thread.wait()
                thread.deleteLater()
            except RuntimeError:
                pass

        subreddit = self.edit_subreddit.text()
        flair = self.edit_flair.text()

        core.config["prev_subreddit"] = subreddit
        core.config["prev_flair"] = flair

        for submission in self.api.search(
            subreddit,
            flair
        ):
            if not submission.is_self and submission.media is None:
                # maybe do extra filtering here later

                # instantiate and start SubmissionLoader thread
                submission_loader = SubmissionLoader(submission, None)
                thread = QThread()
                submission_loader.moveToThread(thread)
                thread.started.connect(submission_loader.load)

                submission_loader.done.connect(lambda: _handle_thread_termination(thread))

                thread.start()
                self._threads.append(thread)
                yield submission_loader

    def _btn_go_clicked(self):
        self.post_list.set_generator(self._get_generator())
        self.canvas.clear_image()
        print("updated generator!")
        self._btn_next_clicked()

    def _update_im(self, im):
        if im is not None:
            try:
                self.canvas.set_image(im)
                print("updated canvas im!")
            except:
                try:
                    self._skip_callback()
                    print("skipped due to error!")
                except:
                    traceback.print_exc()

    def _load_from_submission_loader(self, get_submission_loader_func):
        self.canvas.clear_image()

        try:
            cur_submission_loader = self.post_list.cur()
            if cur_submission_loader is not None:
                cur_submission_loader.disconnect()
        except:
            traceback.print_exc()

        submission_loader = get_submission_loader_func()
        if submission_loader is not None:
            self._update_im(submission_loader.im)
            submission_loader.loaded.connect(self._update_im)

            self.label_title.setText(submission_loader.title)
            self.label_no_display.setText(f"#{self.post_list.get_no():05d}")

    def _btn_next_clicked(self):
        self._skip_callback = self._btn_next_clicked
        self._load_from_submission_loader(self.post_list.next)

    def _btn_prev_clicked(self):
        self._skip_callback = self._btn_prev_clicked

        if self.post_list.prev_count() > 0:
            self._load_from_submission_loader(self.post_list.prev)

    def _btn_external_clicked(self):
        submission_loader = self.post_list.cur()
        webbrowser.open(submission_loader.submission.shortlink)