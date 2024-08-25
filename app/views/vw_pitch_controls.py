import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView
from app.view_models      import VmdCurrentDataset, VmdDatasetListItem
from app.view_models      import vmd_current_dataset

OBJECT_NAME = 'FOOTBALL_PITCH'
OBJECT_LEGEND_IND_NAME = 'FOOTBALL_PITCH_LEGEND_IND'
OBJECT_LEGEND_LBL_NAME = 'FOOTBALL_PITCH_LEGEND_LBL'
OBJECT_CONTROL_FRAME_BUTTON_NAME = 'FOOTBALL_PITCH_CONTROL_FRAME_BUTTON'


class VwPitchControls(VWBaseView):
            
    def __init__(self, model: VmdCurrentDataset = None, parent=None):
        super(VwPitchControls, self).__init__(parent=parent)
        self._model = model or vmd_current_dataset
     
        self._l_legend_ind_1 = self._produce_icon_label('red_rect.png', size_x=90, size_y=90,  label_name=OBJECT_LEGEND_IND_NAME)
        self._l_legend_lbl_1 = self._produce_named_label('ind1', name=OBJECT_LEGEND_LBL_NAME)
        self._l_legend_ind_2 = self._produce_icon_label('blue_rect.png', size_x=90, size_y=90, label_name=OBJECT_LEGEND_IND_NAME)
        self._l_legend_lbl_2 = self._produce_named_label('ind1', name=OBJECT_LEGEND_LBL_NAME)
        
        self._legend_layout = qtw.QHBoxLayout()
        self._legend_layout.addWidget(self._l_legend_ind_1)
        self._legend_layout.addWidget(self._l_legend_lbl_1)
        self._legend_layout.addWidget(self._l_legend_ind_2)
        self._legend_layout.addWidget(self._l_legend_lbl_2)
        self._legend_layout.addStretch()

        self._b_frame_left  = self._produce_button(button_label='<' , button_name=OBJECT_CONTROL_FRAME_BUTTON_NAME)
        self._b_frame_right = self._produce_button(button_label='>' , button_name=OBJECT_CONTROL_FRAME_BUTTON_NAME)
        self._b_frame_read  = self._produce_button(button_label='GO', button_name=OBJECT_CONTROL_FRAME_BUTTON_NAME)
        self._l_timestamp_name  = self._produce_named_label(content='Timestamp', name=OBJECT_LEGEND_LBL_NAME)
        self._l_timestamp_value = self._produce_named_label(content=self._model.get_current_item_data().get_timestamp(), name=OBJECT_LEGEND_LBL_NAME)
        self._l_frame_max   = self._produce_named_label(content=self._model.get_current_item_data().get_frames_no_data(), name=OBJECT_LEGEND_LBL_NAME)
        self._l_frame_curr  = self._produce_line_edit(init_val=self._model.get_current_item_data().get_curr_frame_data(), name=OBJECT_LEGEND_LBL_NAME)

        self._controls_layout = qtw.QHBoxLayout()
        self._controls_layout.addWidget(self._b_frame_left)
        self._controls_layout.addWidget(self._l_timestamp_name)
        self._controls_layout.addWidget(self._l_timestamp_value)
        self._controls_layout.addWidget(self._b_frame_right)
        self._controls_layout.addWidget(self._l_frame_curr)
        self._controls_layout.addWidget(self._produce_named_label(content='/', name=OBJECT_LEGEND_LBL_NAME))
        self._controls_layout.addWidget(self._l_frame_max)
        self._controls_layout.addWidget(self._b_frame_read)
        self._controls_layout.addStretch()

        self._main_layout = qtw.QVBoxLayout()
        self._main_layout.addLayout(self._legend_layout)
        self._main_layout.addLayout(self._controls_layout)

        self.setLayout(self._main_layout)

        self._setup()
        self.show()

    def _set_value_subscriptions(self):
        self._model.dataset_edited.connect(self._update_view)
        self._model.disable_next_frame_btn.connect(lambda x : self._b_frame_right.setDisabled(True) if x else self._b_frame_right.setEnabled(True))
        self._model.disable_prev_frame_btn.connect(lambda x : self._b_frame_left.setDisabled(True)  if x else self._b_frame_left.setEnabled(True))
        self._model.disable_read_frame_btn.connect(lambda x : self._b_frame_read.setDisabled(True)  if x else self._b_frame_read.setEnabled(True))

    def _bind_buttons_to_commands(self):
        self._b_frame_read.clicked.connect(self._model.get_data)
        self._b_frame_left.clicked.connect(self._model.previous_frame)
        self._b_frame_right.clicked.connect(self._model.next_frame)
        self._l_frame_curr.editingFinished.connect(lambda: self._model.set_current_frame(self._l_frame_curr.text()))
        
    def _init_actions(self):
        self._model.check_curr_frame_no()

    def _update_view(self, item: VmdDatasetListItem):
        self._l_timestamp_value.setText(item.get_timestamp())
        self._l_frame_curr.setText(item.get_curr_frame_data())
        self._l_frame_max.setText(item.get_frames_no_data())