from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class AnswerDialog(QDialog):
    def __init__(self, message, image_number, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Answer Check")
        self.setFixedSize(300, 200)
        self.setStyleSheet("background-color: #191414; color: #FFFFFF")

        layout = QVBoxLayout()

        # Image setup based on image_number
        if image_number == 1:
            image_path = "assets/green_tick_transp.png"
        elif image_number == 2:
            image_path = "assets/red_cross_transp.png"
        elif image_number == 3:
            image_path = "assets/celebration.png"
        else:
            image_path = ""

        if image_path:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(pixmap.width() * 0.25, pixmap.height() * 0.25, Qt.KeepAspectRatio)
            image_label = QLabel()
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        self.ok_button = QPushButton("Ok")
        self.ok_button.setStyleSheet("background-color: #1DB954; color: #191414;")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)