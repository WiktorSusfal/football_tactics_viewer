from app.views import VwDatasetDetails
from tests.gui._base import visual_test_preview


if __name__ == '__main__':
    view = VwDatasetDetails()
    view.setStyleSheet("background-color: #2f3b52;")
    visual_test_preview(view)