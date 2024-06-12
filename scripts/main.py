from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from Vista.start_window import StartWindow
import os
import sys

# recogemos las constantes del .env
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec())