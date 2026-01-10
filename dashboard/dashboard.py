import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class HeatmapWidget(QLabel):
    def __init__(self, grid_width=20, grid_height=20, upscale_factor=20):
        super().__init__()

        # Logical grid size (easy to change later)
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Controls how "continuous" the heatmap looks
        self.upscale_factor = upscale_factor

        # Initial sound data (0 = quiet, 1 = loud)
        self.data = np.zeros((self.grid_height, self.grid_width))

        self.setMinimumSize(
            self.grid_width * self.upscale_factor,
            self.grid_height * self.upscale_factor
        )

    def update_data(self, new_data):
        """Update the sound intensity grid"""
        self.data = np.clip(new_data, 0.0, 1.0)
        self.render_heatmap()

    def render_heatmap(self):
        # Upscale data for smooth appearance
        upscaled = np.kron(
            self.data,
            np.ones((self.upscale_factor, self.upscale_factor))
        )

        height, width = upscaled.shape
        image = QImage(width, height, QImage.Format_RGB888)

        for y in range(height):
            for x in range(width):
                value = upscaled[y, x]
                r, g, b = self.value_to_color(value)
                image.setPixel(x, y, (r << 16) | (g << 8) | b)

        self.setPixmap(QPixmap.fromImage(image))

    @staticmethod
    def value_to_color(value):
        """
        Map sound level to color:
        0.0 -> Green
        0.5 -> Yellow
        1.0 -> Red
        """
        if value < 0.5:
            # Green to Yellow
            ratio = value / 0.5
            r = int(255 * ratio)
            g = 255
        else:
            # Yellow to Red
            ratio = (value - 0.5) / 0.5
            r = 255
            g = int(255 * (1 - ratio))

        b = 0
        return r, g, b


class StudySpaceDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Space Sound Map")

        layout = QVBoxLayout()
        self.heatmap = HeatmapWidget(
            grid_width=25,
            grid_height=25,
            upscale_factor=18
        )

        layout.addWidget(self.heatmap)
        self.setLayout(layout)

        # Timer to simulate live sound updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_fake_data)
        self.timer.start(500)

    def generate_fake_data(self):
        """
        Simulated sound data.
        Replace this with real microphone or sensor input later.
        """
        noise = np.random.rand(
            self.heatmap.grid_height,
            self.heatmap.grid_width
        )

        # Smooth transitions over time
        self.heatmap.update_data(
            0.7 * self.heatmap.data + 0.3 * noise
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudySpaceDashboard()
    window.show()
    sys.exit(app.exec_())