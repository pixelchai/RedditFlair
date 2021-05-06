from qtpy import QtWidgets
import ui

app = QtWidgets.QApplication([])

window = ui.MainWindow()
window.show()

app.exec_()