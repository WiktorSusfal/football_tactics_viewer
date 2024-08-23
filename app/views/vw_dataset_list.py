import PyQt5.QtWidgets as qtw

from app.views.components.vw_base_view   import VWBaseView
from app.views.components.vw_list_widget import VwListWidget
from app.views.vw_dataset_list_item      import VwDatasetListItem
from app.view_models                     import VmdDatasetList, VmdDatasetListItem


OBJECT_NAME = 'DATASET_LIST'
OBJECT_TITLE_LABEL_NAME = 'OBJECT_TITLE_LABEL'
OBJECT_LINE_EDIT_NAME = 'DATASET_LIST_LINE_EDIT'
OBJECT_ADD_BUTTON_NAME = 'DATASET_LIST_ADD_BUTTON'


class VwDatasetList(VWBaseView):

    def __init__(self, model: VmdDatasetList = None, parent=None):
        super(VwDatasetList, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)
        self._model = model or VmdDatasetList()
        
        self._l_title_label  = self._produce_named_label(content='Add new dataset', name=OBJECT_TITLE_LABEL_NAME)
        self._selection_list = VwListWidget()
        
        self._i_dname_input = self._produce_line_edit(name=OBJECT_LINE_EDIT_NAME )
        self._b_add_button  = self._produce_button(button_label="+", button_name=OBJECT_ADD_BUTTON_NAME)

        self._add_layout = qtw.QHBoxLayout()
        self._add_layout.addWidget(self._i_dname_input)
        self._add_layout.addWidget(self._b_add_button)

        main_layout = qtw.QVBoxLayout()
        main_layout.addWidget(self._l_title_label)
        main_layout.addLayout(self._add_layout)
        main_layout.addWidget(self._selection_list, stretch=0)
        
        self.setLayout(main_layout)

        self._setup()
        self.show()

    def _bind_buttons_to_commands(self):
        self._b_add_button.clicked.connect(lambda: self._model.add_item(self._i_dname_input.text()))

    def _set_value_subscriptions(self):
        self._model.list_item_added.connect(self._add_item)
        self._model.list_item_deleted.connect(self._delete_item)

        self._selection_list.currentItemChanged.connect(self._send_item_changed_info)

    def _init_actions(self):
        pass

    def _add_item(self, item: VmdDatasetListItem):
        item_widget = VwDatasetListItem(model=item, parent=self._selection_list)

        list_item = qtw.QListWidgetItem(self._selection_list)
        list_item.setSizeHint(item_widget.sizeHint())
        
        self._selection_list.addItem(list_item)
        self._selection_list.setItemWidget(list_item, item_widget)
        self._selection_list.setCurrentItem(list_item)

    def _delete_item(self, item: VmdDatasetListItem):
        for row in range(self._selection_list.count()):
            ref_item = self._selection_list.item(row)
            item_widget: VwDatasetListItem = self._selection_list.itemWidget(ref_item)
            
            if item_widget._model.get_id() == item.get_id():
                 target_item = self._selection_list.takeItem(row)
                 del target_item
                 break

    def _send_item_changed_info(self, item: qtw.QListWidgetItem):
        item_widget = None
        if item:
            item_widget: VwDatasetListItem = self._selection_list.itemWidget(item)
        
        self._model.change_current_item(item_widget._model if item_widget else None)