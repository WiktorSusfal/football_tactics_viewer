import numpy as np
import PyQt5.QtGui      as qtg
import PyQt5.QtCore     as qtc

from app.views.components import VWBaseView


FOOTBALL_PITCH_PIXMAP_PATH = 'resources/img/test_football_field.png'
# In analyzed datasets the size of pitch is normalized to width: 120 and height: 80, so the ratio between
# width and height (which is 1.5) should remain.
# Following variables are the size of whole pitch image (with borders).
FOOTBALL_PITCH_HEIGHT = 446
FOOTBALL_PITCH_WIDTH = 670
# Following variables are the size of borders - distance from the start of image to the borderlines of the pitch.
PITCH_BORDER_X = 22
PITCH_BORDER_Y = 6
PITCH_BORDER_SIZE = np.array([PITCH_BORDER_X, PITCH_BORDER_Y])
# Original ranges of coordinates from datasets.
ORG_X_RANGE = (0.0, 120.0)
ORG_Y_RANGE = (0.0, 80.0)
# Diameters of ellipse representing player on pitch.
PLAYER_SIZE = np.array([22, 22])


class VwFootballPitch(VWBaseView):
    """
    Class for football pitch visualization. Contains methods to draw players positions on the pitch based on given data.
    """

    def __init__(self, parent=None):
        super(VwFootballPitch, self).__init__(parent=parent)
        # define ranges (in pixels) of exact pitch rectangle (excluding borders on the pitch image)
        self._pitch_x_range = (float(PITCH_BORDER_X), float(FOOTBALL_PITCH_WIDTH  - PITCH_BORDER_X))
        self._pitch_y_range = (float(PITCH_BORDER_Y), float(FOOTBALL_PITCH_HEIGHT - PITCH_BORDER_Y))

        # define color sets for icons representing players on pitch; main keys are integer indexes of teams from the
        # 'FTV_JsonData.FTV_JsonDataManager.lineups_main' pandas dataframe
        self.icon_colors = {
            0: {'keeper': qtg.QColor(255, 165, 0), 'player': qtg.QColor(255, 0, 0)},
            1: {'keeper': qtg.QColor(255, 165, 0), 'player': qtg.QColor(0, 0, 255)}
        }

        self.setFixedSize(FOOTBALL_PITCH_WIDTH, FOOTBALL_PITCH_HEIGHT)

        self._pitch_pixmap = self.returnPixmap(FOOTBALL_PITCH_PIXMAP_PATH,
                                              scaled_height=FOOTBALL_PITCH_HEIGHT, scaled_width=FOOTBALL_PITCH_WIDTH
                                              )

        self._setup()
        self.show()

    @staticmethod
    def returnPixmap(png_file_path: str, scaled_width: int = None, scaled_height: int = None) -> qtg.QPixmap:
        """
        Returns pixmap of the given png file, scaled with given width and height.

        :param png_file_path: String path to png file.
        :param scaled_width: Optional width parameter to scale pixmap.
        :param scaled_height: Optional height parameter to scale pixmap.

        :return: QPixmap object
        """

        pixmap_image = qtg.QPixmap(png_file_path)

        if scaled_width and scaled_height:
            pixmap_image = pixmap_image.scaled(scaled_width, scaled_height, qtc.Qt.IgnoreAspectRatio)
        elif scaled_width:
            pixmap_image = pixmap_image.scaledToWidth(scaled_width)
        elif scaled_height:
            pixmap_image = pixmap_image.scaledToHeight(scaled_height)

        return pixmap_image

    def paintEvent(self, event):
        """
        Function to draw the football pitch image initially on screen.

        :param event: PyQt5 event.
        :return: None
        """
        painter = qtg.QPainter(self)
        painter.drawPixmap(self.rect(), self._pitch_pixmap)

    def _set_value_subscriptions(self):
        pass

    def _bind_buttons_to_commands(self):
        pass

    def _init_actions(self):
        pass