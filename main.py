import sys
from PySide6.QtWidgets import QApplication
from CTGAnalyzerApp import CTGAnalyzerApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CTGAnalyzerApp()
    sys.exit(app.exec())
