from app.views.vw_dataset_list_item import VwDatasetListItem
from tests.gui._base import visual_test_preview


if __name__ == '__main__':
    view = VwDatasetListItem()
    view.setStyleSheet("background-color: #2f3b52;")
    visual_test_preview(view)