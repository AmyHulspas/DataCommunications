import sys
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, qRgb
from PyQt5.QtCore import Qt, QTimer


class HeatmapWidget(QWidget):
    def __init__(self, grid_width=30, grid_height=20, parent=None):
        super().__init__(parent)

        # Heatmap resolution
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Dummy data placeholder
        self.data = self.generate_dummy_data()

        self.setMinimumSize(400, 300)

    def generate_dummy_data(self):
        """
        Values are from 0.0 to 1.0 in a numpy array
        Replace with real data later
        """
        base = np.random.rand(self.grid_height, self.grid_width)

        # Add a "loud area" blob
        cx, cy = np.random.randint(0, self.grid_width), np.random.randint(0, self.grid_height)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                base[y, x] += np.exp(-dist / 5)

        return np.clip(base, 0.0, 1.0)

    def value_to_color(self, value):
        """
        Maps a sound value between 0 and 1 to a color
        Green is 0, Yellow is 0.5, Red is 1
        """
        if value < 0.5:
            # Green to Yellow
            t = value / 0.5
            r = int(255 * t)
            g = 255
        else:
            # Yellow to Red
            t = (value - 0.5) / 0.5
            r = 255
            g = int(255 * (1 - t))

        b = 0
        return r, g, b

    def create_image(self):
        """
        Converts the heatmap data into a QImage
        """
        image = QImage(
            self.grid_width,
            self.grid_height,
            QImage.Format_RGB32
        )

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                r, g, b = self.value_to_color(self.data[y, x])
                image.setPixel(x, y, qRgb(r, g, b))

        return image

    def paintEvent(self, event):
        """
        Draw and smoothly scale the heatmap to the widget size
        """
        image = self.create_image()
        pixmap = QPixmap.fromImage(image)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(
            self.rect(),
            pixmap
        )
        painter.end

    def update_data(self):
        """
        Regenerates data (simulates live updates)
        Replace this with real sensor input later
        """
        self.data = self.generate_dummy_data()
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Study Space Sound Map")

        # Change resolution here for smoother or coarser heatmap
        self.heatmap = HeatmapWidget(grid_width=40, grid_height=25)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.heatmap)
        self.setCentralWidget(central)

        # Timer to simulate live updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.heatmap.update_data)
        self.timer.start(1000)  # update every second


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec_())