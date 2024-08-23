"""Contains method which displays any PyQt5 widget object inside new window"""

import PyQt5.QtWidgets as qtw
import sys as sys


_test_view_app = qtw.QApplication(sys.argv)

def visual_test_preview(target_widget: qtw.QWidget):
    """Displays any PyQt5 widget object inside new window"""
    
    class HpVisualTestWidget(qtw.QMainWindow):

        def __init__(self, target_widget: qtw.QWidget):
            super(HpVisualTestWidget, self).__init__()
            target_widget.setParent(self)

            self.setWindowTitle("Visual Test View")
            self.setCentralWidget(target_widget)

            self.show()

    app_main_gui = HpVisualTestWidget(target_widget)
    sys.exit(_test_view_app.exec_())