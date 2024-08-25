from app.views import VwMainView
from tests.gui._base import visual_test_preview


if __name__ == '__main__':
    view = VwMainView()
    visual_test_preview(view)