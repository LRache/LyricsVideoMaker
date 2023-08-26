import json

from LyricsPaser import Lyrics


class AudioInfo:
    audioFilePath: str = None
    titleText: str = None
    subTitleText: str = None
    lyricsFilePath: str = None

    lyrics: [Lyrics] = None
    lyricsOffset: float = 0.0


class LyricsConfigures:
    fontFileName: str = "msyh.ttc"
    currentFontFileName: str = "msyhbd.ttc"
    fontSize: int = 40
    lineSplit = 80
    color: str = "rgb(158, 160, 155)"
    currentColor: str = "rgb(227, 224, 235)"
    multiline: bool = False

    line1Y = 780
    lineY: [int] = [line1Y, line1Y+lineSplit, line1Y+lineSplit*2]
    moveSpeed = 300

    def set_multiline(self, flag: bool):
        self.multiline = flag
        if flag:
            self.fontSize = 35
            self.lineSplit = 95
        else:
            self.fontSize = LyricsConfigures.fontSize
            self.lineSplit = LyricsConfigures.lineSplit
        self.lineY = [self.line1Y, self.line1Y + self.lineSplit, self.line1Y + self.lineSplit * 2]


class TitleConfigures:
    fontFileName: str = "msyhbd.ttc"
    fontSize: int = 50
    posY: int = 650
    subFontFileName: str = "msyh.ttc"
    subFontSize: int = 30
    subPosY: int = 710
    textColor = "rgb(213, 213, 210)"


class OutputConfigures:
    videoCodec: str = "h264_nvenc"
    audioCodec: str = "aac"
    filePath: str = None
    bitrate: str = "10000k"


class BackgroundConfigures:
    coverImageSize = 400
    coverImageX: int = 0
    coverImageY: int = 150
    recordPixmapR: int = 300
    recordPixmapX: int = 0
    recordPixmapY: int = 0
    recordArcWidth: int = 3
    recordArcSplit: int = 2
    recordArcBeginWidth: int = 20

    coverImageCycle = 50
    coverImagePath = None

    recordArcCount = 10

    recordColor = (0, 0, 0)
    recordArcColor = (36, 37, 39)

    coverRotating = True


class Configures:
    fps = 30
    duration: int = 0
    videoSize = (1920, 1080)
    videoSize_ = (3840, 2160)
    videoWidth, videoHeight = videoSize

    useCache = True
    showCover = True
    preview = False
    multipy = 2

    def __init__(self):
        self.audioInfo = AudioInfo()
        self.lyrics = LyricsConfigures()
        self.title = TitleConfigures()
        self.background = BackgroundConfigures()
        self.output = OutputConfigures()

    def cal(self):
        self.background.coverImageX = self.videoWidth // 2 - self.background.coverImageSize // 2
        self.background.recordPixmapX = self.background.coverImageX + self.background.coverImageSize // 2 - \
                                        self.background.recordPixmapR
        self.background.recordPixmapY = self.background.coverImageY + self.background.coverImageSize // 2 - \
                                        self.background.recordPixmapR


def load_configures(configures: Configures, path: str):
    with open(path, encoding="utf-8") as f:
        c: dict = json.load(f)

    configures.background.coverImagePath = c.get("coverFilePath", BackgroundConfigures.coverImagePath)
    configures.background.coverRotating = c.get("coverRotating", BackgroundConfigures.coverRotating)

    configures.audioInfo.audioFilePath = c["audioFilePath"]
    configures.audioInfo.lyricsFilePath = c.get("lyricsFilePath", AudioInfo.lyricsFilePath)
    configures.audioInfo.lyricsOffset = c.get("lyricsOffset", AudioInfo.lyricsOffset)
    configures.audioInfo.titleText = c.get("title", AudioInfo.titleText)
    configures.audioInfo.subTitleText = c.get("subTitle", AudioInfo.subTitleText)

    configures.output.filePath = c.get("outputFilePath", OutputConfigures.filePath)
    configures.output.videoCodec = c.get("outputVideoCodec", OutputConfigures.videoCodec)
    configures.output.audioCodec = c.get("outputAudioCodec", OutputConfigures.audioCodec)
    configures.output.bitrate = c.get("bitrate", OutputConfigures.bitrate)

    configures.lyrics.set_multiline(c.get("multilineLyrics", LyricsConfigures.multiline))

    configures.duration = c.get("duration", Configures.duration)
    configures.fps = c.get("fps", Configures.fps)

    configures.useCache = c["application"]["useCache"]
    configures.showCover = c["application"]["showCover"]
    configures.preview = c["application"]['preview']
    configures.showCover = c["application"]["showCover"]
