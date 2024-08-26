from PyQt5.QtWidgets import QApplication

from app.views   import VwMainWindow
from app.helpers import get_styles_code


app = QApplication([])
app.setStyleSheet(get_styles_code())
app_main_gui = VwMainWindow()