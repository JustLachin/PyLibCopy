import sys
import subprocess
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressDialog, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class InstallWorker(QThread):
    finished = pyqtSignal(bool, str, str)  # Success, stdout, stderr

    def __init__(self, library_name, install_dir):
        super().__init__()
        self.library_name = library_name
        self.install_dir = install_dir

    def run(self):
        command = [sys.executable, "-m", "pip", "install", self.library_name, "--target", self.install_dir]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            success = (result.returncode == 0)
            self.finished.emit(success, result.stdout, result.stderr)
        except Exception as e:
            self.finished.emit(False, "", str(e))


class PyLibCopy(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyLibCopy')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.text_edit = QLineEdit()
        layout.addWidget(self.text_edit)

        self.install_button = QPushButton('Install Library')
        self.install_button.clicked.connect(self.installLibrary)
        layout.addWidget(self.install_button)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        # Buton oluştur
        self.button = QPushButton('GitHub Repo https://github.com/JustLachin/PyLibCopy')
        self.button.clicked.connect(self.openGitHub)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.worker = None

    def openGitHub(self):
        # GitHub deposu linkini aç
        webbrowser.open('')

    def installLibrary(self):
        library_name = self.text_edit.text()
        if not library_name:
            QMessageBox.warning(self, 'Warning', 'Please enter a library name.')
            return

        install_dir = QFileDialog.getExistingDirectory(self, 'Select Target Directory')
        if not install_dir:
            return

        self.progress_dialog = QProgressDialog("Installing...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Library Installation")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.show()

        self.worker = InstallWorker(library_name, install_dir)
        self.worker.finished.connect(self.installFinished)
        self.worker.start()

    def installFinished(self, success, stdout, stderr):
        self.progress_dialog.close()

        # Add installation logs to log view
        if stdout:
            self.log_view.append("STDOUT:\n" + stdout)
        if stderr:
            self.log_view.append("STDERR:\n" + stderr)

        if success:
            QMessageBox.information(self, 'Success', f"The library '{self.text_edit.text()}' was installed successfully.")
        else:
            QMessageBox.critical(self, 'Error', 'An error occurred while installing the library.')

    def showLog(self):
        self.log_view.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyLibCopy()
    window.show()
    sys.exit(app.exec_())
