import sys
import os
import subprocess
import webbrowser
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QProgressBar, QTextEdit, QLabel, QComboBox, 
                             QColorDialog, QFontDialog, QSlider, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor, QFont

class InstallWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str, str)

    def __init__(self, library_name, install_dir, pip_options):
        super().__init__()
        self.library_name = library_name
        self.install_dir = install_dir
        self.pip_options = pip_options

    def run(self):
        command = [sys.executable, "-m", "pip", "install", self.library_name, "--target", self.install_dir] + self.pip_options
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        for i in range(101):
            self.progress.emit(i)
            self.msleep(50)  # Simulated progress

        stdout, stderr = process.communicate()
        success = (process.returncode == 0)
        self.finished.emit(success, stdout, stderr)

class PyLibCopy(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyLibCopy')
        self.setGeometry(100, 100, 700, 500)
        self.setStyleSheet(self.get_default_style())

        main_layout = QVBoxLayout()

        # Logo and title
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png")  # Add your logo file
        logo_label.setPixmap(logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)
        self.title_label = QLabel("<h2>PyLibCopy</h2>")
        self.title_label.setAlignment(Qt.AlignCenter)  # Metni ortalama

        header_layout.addWidget(self.title_label)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(header_layout)

        # Library name input
        input_layout = QHBoxLayout()
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Enter library name")
        input_layout.addWidget(self.text_edit)
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(["Latest version", "Specific version"])
        input_layout.addWidget(self.version_combo)
        
        main_layout.addLayout(input_layout)

        # Pip options
        self.pip_options = QLineEdit()
        self.pip_options.setPlaceholderText("Additional pip options (e.g., --no-deps)")
        main_layout.addWidget(self.pip_options)

        # Buttons
        button_layout = QHBoxLayout()
        self.install_button = QPushButton('Install Library')
        self.install_button.clicked.connect(self.installLibrary)
        button_layout.addWidget(self.install_button)

        self.github_button = QPushButton('GitHub Repo https://github.com/JustLachin/PyLibCopy')
        self.github_button.clicked.connect(self.openGitHub)
        button_layout.addWidget(self.github_button)

        self.pypi_button = QPushButton('PyPI Page')
        self.pypi_button.clicked.connect(self.openPyPI)
        button_layout.addWidget(self.pypi_button)

        main_layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Log viewer
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        main_layout.addWidget(self.log_view)

        # Customization options
        customization_layout = QHBoxLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme", "Custom Theme"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        customization_layout.addWidget(self.theme_combo)

        self.color_button = QPushButton('Change Accent Color')
        self.color_button.clicked.connect(self.change_accent_color)
        customization_layout.addWidget(self.color_button)

        self.font_button = QPushButton('Change Font')
        self.font_button.clicked.connect(self.change_font)
        customization_layout.addWidget(self.font_button)

        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(50, 100)
        self.transparency_slider.setValue(100)
        self.transparency_slider.valueChanged.connect(self.change_transparency)
        customization_layout.addWidget(QLabel("Transparency:"))
        customization_layout.addWidget(self.transparency_slider)

        self.always_on_top = QCheckBox("Always on Top")
        self.always_on_top.stateChanged.connect(self.toggle_always_on_top)
        customization_layout.addWidget(self.always_on_top)

        main_layout.addLayout(customization_layout)

        self.setLayout(main_layout)

        self.worker = None
        self.accent_color = "#4a4a4a"  # Default accent color

    def get_default_style(self):
        return """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #5a5a5a;
                padding: 3px;
            }
        """

    def change_theme(self, index):
        if index == 0:  # Dark Theme
            self.setStyleSheet(self.get_default_style())
        elif index == 1:  # Light Theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #d0d0d0;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #a0a0a0;
                    padding: 3px;
                }
            """)
        else:  # Custom Theme
            color = QColorDialog.getColor()
            if color.isValid():
                self.setStyleSheet(f"""
                    QWidget {{
                        background-color: {color.name()};
                        color: {'#000000' if color.lightness() > 128 else '#ffffff'};
                    }}
                    QPushButton {{
                        background-color: {color.lighter().name()};
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }}
                    QPushButton:hover {{
                        background-color: {color.lighter().lighter().name()};
                    }}
                    QLineEdit, QTextEdit, QComboBox {{
                        background-color: {color.darker().name()};
                        border: 1px solid {color.lighter().name()};
                        padding: 3px;
                    }}
                """)

    def change_accent_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.accent_color = color.name()
            self.setStyleSheet(self.styleSheet() + f"""
                QPushButton {{
                    background-color: {self.accent_color};
                }}
                QPushButton:hover {{
                    background-color: {color.lighter().name()};
                }}
            """)

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.setFont(font)
            self.title_label.setFont(QFont(font.family(), 16, QFont.Bold))

    def change_transparency(self, value):
        self.setWindowOpacity(value / 100.0)

    def toggle_always_on_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def openGitHub(self):
        webbrowser.open('https://github.com/JustLachin/PyLibCopy')

    def openPyPI(self):
        library_name = self.text_edit.text()
        if library_name:
            webbrowser.open(f'https://pypi.org/project/{library_name}/')
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter a library name first.')

    def installLibrary(self):
        library_name = self.text_edit.text()
        if not library_name:
            QMessageBox.warning(self, 'Warning', 'Please enter a library name.')
            return

        if self.version_combo.currentText() == "Specific version":
            version, ok = QInputDialog.getText(self, 'Enter Version', 'Enter the library version:')
            if ok and version:
                library_name += f"=={version}"

        install_dir = QFileDialog.getExistingDirectory(self, 'Select Target Directory')
        if not install_dir:
            return

        pip_options = self.pip_options.text().split()

        self.progress_bar.setValue(0)
        self.install_button.setEnabled(False)

        self.worker = InstallWorker(library_name, install_dir, pip_options)
        self.worker.progress.connect(self.updateProgress)
        self.worker.finished.connect(self.installFinished)
        self.worker.start()

        self.log_view.append(f"Installing: {library_name}\nTarget directory: {install_dir}\nAdditional options: {' '.join(pip_options)}")

    def updateProgress(self, value):
        self.progress_bar.setValue(value)

    def installFinished(self, success, stdout, stderr):
        self.install_button.setEnabled(True)
        self.progress_bar.setValue(100)

        if stdout:
            self.log_view.append("STDOUT:\n" + stdout)
        if stderr:
            self.log_view.append("STDERR:\n" + stderr)

        if success:
            QMessageBox.information(self, 'Success', f"The library '{self.text_edit.text()}' was successfully installed.")
            
            # Get information about the installed library
            try:
                info = subprocess.check_output([sys.executable, "-m", "pip", "show", self.text_edit.text()]).decode()
                self.log_view.append("\nLibrary Information:\n" + info)
            except:
                self.log_view.append("\nCouldn't retrieve library information.")
        else:
            QMessageBox.critical(self, 'Error', 'An error occurred while installing the library.')

        # Post-installation cleanup
        try:
            subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], check=True)
            self.log_view.append("\nCache cleared.")
        except:
            self.log_view.append("\nError while clearing cache.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyLibCopy()
    window.show()
    sys.exit(app.exec_())
