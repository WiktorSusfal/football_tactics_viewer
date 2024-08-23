import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView

OBJECT_NAME = 'FOOTBALL_PITCH'
OBJECT_LEGEND_IND_NAME = 'FOOTBALL_PITCH_LEGEND_IND'
OBJECT_LEGEND_LBL_NAME = 'FOOTBALL_PITCH_LEGEND_LBL'
OBJECT_CONTROL_FRAME_BUTTON_NAME = 'FOOTBALL_PITCH_CONTROL_FRAME_BUTTON'


class VwPitchControls(VWBaseView):
            
    def __init__(self, parent=None):
        super(VwPitchControls, self).__init__(parent=parent)
     
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
        self._l_timestamp_value = self._produce_named_label(content='N/A', name=OBJECT_LEGEND_LBL_NAME)
        self._l_timestamp_max   = self._produce_named_label(content='0', name=OBJECT_LEGEND_LBL_NAME)
        self._l_timestamp_curr  = self._produce_line_edit(init_val='0', name=OBJECT_LEGEND_LBL_NAME)

        self._controls_layout = qtw.QHBoxLayout()
        self._controls_layout.addWidget(self._b_frame_left)
        self._controls_layout.addWidget(self._l_timestamp_name)
        self._controls_layout.addWidget(self._l_timestamp_value)
        self._controls_layout.addWidget(self._b_frame_right)
        self._controls_layout.addWidget(self._l_timestamp_curr)
        self._controls_layout.addWidget(self._produce_named_label(content='/', name=OBJECT_LEGEND_LBL_NAME))
        self._controls_layout.addWidget(self._l_timestamp_max)
        self._controls_layout.addWidget(self._b_frame_read)
        self._controls_layout.addStretch()

        self._main_layout = qtw.QVBoxLayout()
        self._main_layout.addLayout(self._legend_layout)
        self._main_layout.addLayout(self._controls_layout)

        self.setLayout(self._main_layout)

        self._setup()
        self.show()

    def _set_value_subscriptions(self):
        pass

    def _bind_buttons_to_commands(self):
        pass

    def _init_actions(self):
        pass