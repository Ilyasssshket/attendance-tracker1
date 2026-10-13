import sys
from PyQt6.QtWidgets import QApplication
from components import AttendanceMainWindow


def main():
    application = QApplication(sys.argv)
    application.setApplicationName("Учёт посещений")
    application.setStyle("Fusion")

    main_window = AttendanceMainWindow()
    main_window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()
