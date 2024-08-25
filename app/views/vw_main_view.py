import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView
from app.views import VwDatasetList, VwMainDataToolbar, VwFootballPitch, VwPitchControls, VwDatasetDetails

class VwMainView(VWBaseView):

    def __init__(self, parent=None):
        super(VwMainView, self).__init__(parent=parent)

        self._vw_dataset_list    = VwDatasetList(parent=self)
        self._vw_main_toolbar    = VwMainDataToolbar(parent=self)
        self._vw_pitch_view      = VwFootballPitch(parent=self)
        self._vw_pitch_controls  = VwPitchControls(parent=self)
        self._vw_dataset_details = VwDatasetDetails(parent=self)

        self._right_pane_layout = qtw.QVBoxLayout()
        self._right_pane_layout.addWidget(self._vw_main_toolbar )
        self._right_pane_layout.addWidget(self._vw_pitch_view )
        self._right_pane_layout.addWidget(self._vw_pitch_controls )
        self._right_pane_layout.addWidget(self._vw_dataset_details )
        self._right_pane_layout.addStretch()

        self._main_layout = qtw.QHBoxLayout()
        self._main_layout.addWidget(self._vw_dataset_list)
        self._main_layout.addLayout(self._right_pane_layout)

        self.setLayout(self._main_layout)

        self._setup()
        self.show()

    def _set_value_subscriptions(self):
        pass

    def _bind_buttons_to_commands(self):
        pass

    def _init_actions(self):
        pass

