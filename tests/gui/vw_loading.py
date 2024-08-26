from app.views import VwLoading
from tests.gui._base import visual_test_preview


if __name__ == '__main__':
    view = VwLoading()
    view.manage(True)
    visual_test_preview(view)