import numpy  as np
import pandas as pd
import PyQt5.QtGui      as qtg
import PyQt5.QtCore     as qtc

from app.views.components import VWBaseView
from app.models           import MAX_PLAYER_X_COORD, MIN_PLAYER_X_COORD, MAX_PLAYER_Y_COORD, MIN_PLAYER_Y_COORD
from app.view_models      import VmdFootballPitch, VmdPitchPlayersData
from app.view_models      import vmd_football_pitch


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

# Diameters of ellipse representing player on pitch.
PLAYER_SIZE = np.array([22, 22])


class VwFootballPitch(VWBaseView):
    """
    Class for football pitch visualization. Contains methods to draw players positions on the pitch based on given data.
    """

    def __init__(self, model: VmdFootballPitch = None, parent=None):
        super(VwFootballPitch, self).__init__(parent=parent)
        # define ranges (in pixels) of exact pitch rectangle (excluding borders on the pitch image)
        self._pitch_x_range = (float(PITCH_BORDER_X), float(FOOTBALL_PITCH_WIDTH  - PITCH_BORDER_X))
        self._pitch_y_range = (float(PITCH_BORDER_Y), float(FOOTBALL_PITCH_HEIGHT - PITCH_BORDER_Y))

        self.setFixedSize(FOOTBALL_PITCH_WIDTH, FOOTBALL_PITCH_HEIGHT)

        self._model = model or vmd_football_pitch
        
        self._setup()
        self.show()

    @staticmethod
    def _return_pixmap(png_file_path: str, scaled_width: int = None, scaled_height: int = None) -> qtg.QPixmap:
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
        pitch_pixmap = self._return_pixmap(FOOTBALL_PITCH_PIXMAP_PATH
                                        ,scaled_height=FOOTBALL_PITCH_HEIGHT
                                        ,scaled_width =FOOTBALL_PITCH_WIDTH)
        # painter to draw on pixmap
        pixmap_painter = qtg.QPainter(pitch_pixmap)
        
        for item in self._model.get_paint_data():
            item: VmdPitchPlayersData = item

            pitch_coordinates = np.array([
                 self._map_x_coordinate(item.x_coord)
                ,self._map_y_coordinate(item.y_coord)
            ])
            pixmap_coordinates = self._get_pixmap_coordinates(pitch_coordinates)

            pixmap_painter.setBrush(qtg.QBrush(item.color))
            pixmap_painter.drawEllipse(pixmap_coordinates)
        
        pixmap_painter.end()

        painter = qtg.QPainter(self)
        painter.drawPixmap(self.rect(), pitch_pixmap)
        painter.end()

    def _set_value_subscriptions(self):
        self._model.player_pitch_data_changed.connect(self._update_view)

    def _bind_buttons_to_commands(self):
        pass

    def _init_actions(self):
        pass

    def _update_view(self, data: pd.Series):
        """
        Draws new positions of players on the pitch, based on given data
        
        :return: None
        """
        self.update()

    def _map_x_coordinate(self, org_x: float) -> int:
        """
        Returns x coordinate in pitch's coordinate system

        :param org_x: origin value of the X coordinate

        :return: Integer calculated X coordinate
        """
        ORG_MIN_X, ORG_MAX_X = MIN_PLAYER_X_COORD, MAX_PLAYER_X_COORD
        NEW_MIN_X, NEW_MAX_X = self._pitch_x_range[0], self._pitch_x_range[1]
        return int(
                (org_x - ORG_MIN_X) / (ORG_MAX_X - ORG_MIN_X) * (NEW_MAX_X - NEW_MIN_X) + NEW_MIN_X
            )
    
    def _map_y_coordinate(self, org_y: float) -> int:
        """
        Returns y coordinate in pitch's coordinate system

        :param org_y: origin value of the Y coordinate
        :return: Integer calculated Y coordinate
        """
        ORG_MIN_Y, ORG_MAX_Y = MIN_PLAYER_Y_COORD, MAX_PLAYER_Y_COORD
        NEW_MIN_Y, NEW_MAX_Y = self._pitch_y_range[0], self._pitch_y_range[1]
        return int(
            (org_y - ORG_MIN_Y) / (ORG_MAX_Y - ORG_MIN_Y) * (NEW_MAX_Y - NEW_MIN_Y) + NEW_MIN_Y
        )
    
    def _get_pixmap_coordinates(self, pitch_coordinates: np.array) -> qtc.QRect:
        """
        Returns coordinates in the pitch pixmap's coordinates frame in a form readable by QPainter object
        (as a QRect object). Function considers spaces around exact pitch field and the way that the ellipse is being
        drawn - there is a need to specify top-left point of a rectangle and its width and height. Ellipse is then
        filling the rectangle specified.

        :param pitch_coordinates: Numpy array containing X and Y pitch raw coordinates
        :return: qt.QRect object with coordinates in pitch's pixmap's coordinate system 
        """
        pixmap_coordinates = pitch_coordinates + PITCH_BORDER_SIZE
        # calculate the rectangle's top-left corner coordinates
        pixmap_coordinates -= PLAYER_SIZE

        top_left_corner = qtc.QPoint(int(pixmap_coordinates[0]), int(pixmap_coordinates[1]))
        size = qtc.QSize(int(PLAYER_SIZE[0]), int(PLAYER_SIZE[1]))

        return qtc.QRect(top_left_corner, size)