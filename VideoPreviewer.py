import time
import enum

import numpy
from PyQt5.QtWidgets import QMainWindow, QWidget, QOpenGLWidget, QHBoxLayout, QGroupBox, QVBoxLayout, QToolButton, \
    QSlider, QLabel, QStyle, QTableWidget, QTableWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer, Qt
from PyQt5.QtGui import QImage, QPainter, QColor, QFont, QSurfaceFormat, QMouseEvent, QKeyEvent

from moviepy.video.VideoClip import VideoClip

from Configures import Configures
from GenerateVideo import generate_video


class VideoViewer(QOpenGLWidget):
    class ViewerSize(enum.Enum):
        SIZE_1080p = 0
        SIZE_720p = 1

    class MediaStatus(enum.Enum):
        NO_MEDIA = 0
        PLAYING = 1
        STOPPED = 2
        PAUSED = 3

    def __init__(self, videoClip: VideoClip = None, audioPath: str = None):
        super().__init__()

        self.playerTimer = QTimer()
        self.mediaPlayer = QMediaPlayer()

        self.videoClip: VideoClip | None = None
        self.frameImage: QImage | None = None
        self.currentTime: int = 0
        self.timeStep: int = 0
        self.status = VideoViewer.MediaStatus.NO_MEDIA
        self.startTime: float = 0
        self.startPosition: float = 0
        self.endTime: float = 0
        self.lastTime: float = -1
        self.currentFps = 0
        self.frameImageWidth = 1920
        self.frameImageHeight = 1080
        self.load_frame_image = self.load_frame_image_1080p

        self.playerTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self.playerTimer.timeout.connect(self.playerTimer_timeout)
        self.mediaPlayer.mediaStatusChanged.connect(self.mediaPlayer_mediaStatusChanged)

        if videoClip is not None:
            self.set_video(videoClip, audioPath)

        surfaceFormat = QSurfaceFormat.defaultFormat()
        surfaceFormat.setSamples(4)
        self.setFormat(surfaceFormat)

    def load_frame_image_1080p(self):
        frame = self.videoClip.get_frame(self.currentTime)
        frameData = numpy.array(frame)
        self.frameImage = QImage(frameData, frame.shape[1], frame.shape[0], QImage.Format_RGB888). \
            scaled(1920, 1080, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def load_frame_image_720p(self):
        frame = self.videoClip.get_frame(self.currentTime)
        frameData = numpy.array(frame)
        self.frameImage = QImage(frameData, frame.shape[1], frame.shape[0], QImage.Format_RGB888) \
            .scaled(1280, 720, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def load_frame_image_without_resize(self):
        frame = self.videoClip.get_frame(self.currentTime)
        frameData = numpy.array(frame)
        self.frameImage = QImage(frameData, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

    def playerTimer_timeout(self):
        self.currentTime = self.mediaPlayer.position() / 1000
        if self.lastTime != -1 and self.currentTime != self.lastTime:
            self.currentFps = 1 / (self.currentTime - self.lastTime)
        self.lastTime = self.currentTime

        if self.endTime < self.currentTime:
            self.stop()
            return
        self.load_frame_image()
        self.update()
        self.video_time_changed(self.currentTime)

    def mediaPlayer_mediaStatusChanged(self):
        if self.mediaPlayer.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia:
            self.stop()

    def paintGL(self) -> None:
        if self.status != VideoViewer.MediaStatus.STOPPED and self.frameImage is not None:
            painter = QPainter()
            painter.begin(self)
            painter.drawImage(0, 0, self.frameImage)
            painter.setPen(QColor(0xff, 0xff, 0xff))
            painter.setFont(QFont("Arial", 20))
            painter.drawText(0, 30, "%.2f" % self.currentTime)
            painter.drawText(0, 60, "%.0fFPS" % self.currentFps)
            painter.end()

    def play(self):
        self.lastTime = -1
        if self.status == VideoViewer.MediaStatus.STOPPED:
            self.timeStep = int(1000 / self.videoClip.fps)

            self.playerTimer.setInterval(self.timeStep)
            self.mediaPlayer.play()
            self.playerTimer.start()

            self.status = VideoViewer.MediaStatus.PLAYING
        elif self.status == VideoViewer.MediaStatus.PAUSED:
            self.startTime = time.perf_counter() - self.startPosition
            self.playerTimer.start()
            self.mediaPlayer.play()

            self.status = VideoViewer.MediaStatus.PLAYING

    def stop(self):
        self.mediaPlayer.stop()
        self.playerTimer.stop()
        self.status = VideoViewer.MediaStatus.STOPPED
        self.startPosition = 0
        self.video_play_stop()

    def pause(self):
        self.mediaPlayer.pause()
        self.playerTimer.stop()
        self.startPosition = self.currentTime

        self.status = VideoViewer.MediaStatus.PAUSED

    def set_position(self, t: float):
        self.mediaPlayer.setPosition(int(t * 1000))
        print("set_position：", t)

    def set_video(self, videoClip: VideoClip, audioPath: str = None):
        self.stop()

        if audioPath is None:
            videoClip.audio.write_audiofile(".//temp.mp3")
            audioPath = ".//temp.mp3"
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(audioPath)))
        self.mediaPlayer.setVolume(100)

        self.videoClip = videoClip
        self.endTime = videoClip.duration
        self.status = VideoViewer.MediaStatus.STOPPED

    def resize_viewer(self, size):
        if size == VideoViewer.ViewerSize.SIZE_720p:
            self.setFixedSize(1280, 720)
            if self.videoClip.size == (1280, 720):
                self.load_frame_image = self.load_frame_image_without_resize
            else:
                self.load_frame_image = self.load_frame_image_720p

        elif size == VideoViewer.ViewerSize.SIZE_1080p:
            self.setFixedSize(1920, 1080)
            if self.videoClip.size == (1920, 1080):
                self.load_frame_image = self.load_frame_image_without_resize
            else:
                self.load_frame_image = self.load_frame_image_1080p

    def video_time_changed(self, s: float):
        ...

    def video_play_stop(self):
        ...


class TimeSlider(QSlider):
    def __init__(self):
        super().__init__(Qt.Horizontal)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        super().mousePressEvent(ev)
        if ev.button() == Qt.LeftButton:
            v = int(ev.pos().x() / self.width() * self.maximum())
            self.setValue(v)
            self.mouse_press_value_changed(v)

    def mouse_press_value_changed(self, value: int):
        ...


def format_time(t: float):
    m = t // 60
    ms = t * 1000 % 60000
    return "%.2d:%.2d.%.3d" % (m, ms // 1000, ms % 1000)


class CentralWidget(QWidget):
    def __init__(self, configures: Configures | None = None):
        super().__init__()

        self.configures = configures

        self.videoViewer = VideoViewer()
        self.playButton = QToolButton()
        self.stopButton = QToolButton()
        self.timeSlider = TimeSlider()
        self.timeLabel = QLabel("00:00.000/00:00.000")
        self.lyricsTable = QTableWidget()

        self.totalTimeString = "00:00.000"

        self.init_ui()

        self.playButton.clicked.connect(self.play_button_clicked)
        self.lyricsTable.cellDoubleClicked.connect(self.lyrics_table_double_clicked)
        self.videoViewer.video_time_changed = self.video_time_changed
        self.videoViewer.video_play_stop = self.video_play_stop
        self.timeSlider.mouse_press_value_changed = self.press_slider_time_changed

        self.timeSlider.setTickInterval(5000)
        self.timeSlider.setTickPosition(QSlider.TicksBelow)
        self.lyricsTable.setColumnCount(2)
        self.lyricsTable.setHorizontalHeaderLabels(["时间", "歌词"])
        self.lyricsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.lyricsTable.setEditTriggers(QTableWidget.NoEditTriggers)

        if configures is not None:
            self.set_video(configures)

    def init_ui(self):
        previewGroupBox = QGroupBox("预览")
        previewGroupBox.setFont(QFont("Microsoft YaHei"))
        lyricsGroupBox = QGroupBox("歌词")
        lyricsGroupBox.setFont(QFont("Microsoft YaHei"))

        self.playButton.setFixedSize(30, 30)
        self.stopButton.setFixedSize(30, 30)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        timeBarLayout = QHBoxLayout()
        timeBarLayout.addWidget(self.playButton)
        timeBarLayout.addWidget(self.stopButton)
        timeBarLayout.addWidget(self.timeSlider)
        timeBarLayout.addWidget(self.timeLabel)

        previewGroupBoxLayout = QVBoxLayout()
        previewGroupBoxLayout.addWidget(self.videoViewer)
        previewGroupBoxLayout.addLayout(timeBarLayout)
        previewGroupBoxLayout.addStretch()
        previewGroupBox.setLayout(previewGroupBoxLayout)

        lyricsGroupBoxLayout = QVBoxLayout()
        lyricsGroupBoxLayout.addWidget(self.lyricsTable)
        lyricsGroupBox.setLayout(lyricsGroupBoxLayout)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(previewGroupBox)
        hBoxLayout.addWidget(lyricsGroupBox)
        self.setLayout(hBoxLayout)

    def video_time_changed(self, s: float):
        self.timeLabel.setText(f"{format_time(s)}/{self.totalTimeString}")
        self.timeSlider.setValue(int(s * 1000))

    def video_play_stop(self):
        self.video_time_changed(0)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def set_video(self, configures: Configures):
        self.configures = configures
        self.setWindowTitle(f"预览 - {configures.audioInfo.titleText}")
        videoClip = generate_video(configures)
        self.videoViewer.set_video(videoClip, configures.audioInfo.audioFilePath)

        self.totalTimeString = format_time(videoClip.duration)
        self.timeLabel.setText(f"00:00.000/{self.totalTimeString}")
        self.timeSlider.setMaximum(int(videoClip.duration * 1000))
        self.timeSlider.setValue(0)

        if self.configures.audioInfo.lyrics is not None:
            self.lyricsTable.setRowCount(len(self.configures.audioInfo.lyrics))
            for i in range(len(self.configures.audioInfo.lyrics)):
                self.lyricsTable.setItem(i, 0, QTableWidgetItem(format_time(self.configures.audioInfo.lyrics[i].time)))
                self.lyricsTable.setItem(i, 1, QTableWidgetItem(self.configures.audioInfo.lyrics[i].text))

    def play_preview(self):
        self.videoViewer.resize_viewer(VideoViewer.ViewerSize.SIZE_1080p)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.videoViewer.play()

    def pause_preview(self):
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.videoViewer.pause()

    def set_position(self, t: float):
        self.videoViewer.set_position(t)

    def press_slider_time_changed(self, t: int):
        self.set_position(t / 1000)

    def play_button_clicked(self):
        if self.videoViewer.status == VideoViewer.MediaStatus.STOPPED or \
                self.videoViewer.status == VideoViewer.MediaStatus.PAUSED:
            self.play_preview()
        elif self.videoViewer.status == VideoViewer.MediaStatus.PLAYING:
            self.pause_preview()

    def lyrics_table_double_clicked(self):
        t = self.configures.audioInfo.lyrics[self.lyricsTable.currentRow()].time
        self.set_position(t)


class MainWindow(QMainWindow):
    def __init__(self, configures: Configures | None):
        super().__init__()
        self.centerWidget = CentralWidget()
        self.configures: Configures | None = None
        self.init_ui()

        if configures is not None:
            self.set_configures(configures)

    def init_ui(self):
        self.setCentralWidget(self.centerWidget)

    def set_configures(self, configures: Configures):
        self.configures = configures
        self.centerWidget.set_video(configures)
        self.setWindowTitle(f"预览 - {configures.audioInfo.titleText} [{configures.audioInfo.subTitleText}]")

    def play_preview(self):
        self.centerWidget.play_preview()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            self.play_preview()
        else:
            super().keyPressEvent(event)
