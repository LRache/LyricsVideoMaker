from moviepy.video.VideoClip import VideoClip
import numpy
import mutagen
from PIL import Image, ImageFilter, ImageEnhance
from PIL.ImageDraw import ImageDraw

from io import BytesIO

from Configures import Configures
from GenerateBackgroundImage import generate_cover_circle_mask, generate_background_image


def set_background_image(backgroundImage: Image, configures: Configures):
    multipy = configures.multipy
    videoSize = (configures.videoSize[0] * multipy, configures.videoSize[1] * multipy)
    recordPixmapX = configures.background.recordPixmapX * multipy
    recordPixmapY = configures.background.recordPixmapY * multipy
    recordPixmapR = configures.background.recordPixmapR * multipy
    coverImageX = configures.background.coverImageX * multipy
    coverImageY = configures.background.coverImageY * multipy
    recordArcBeginWidth = configures.background.recordArcBeginWidth * multipy
    recordArcWidth = configures.background.recordArcWidth * multipy
    recordArcSplit = configures.background.recordArcSplit * multipy
    coverImageSize = configures.background.coverImageSize * multipy

    backgroundImage = backgroundImage.resize(videoSize)
    backgroundImage = backgroundImage.filter(ImageFilter.GaussianBlur(100))
    backgroundImage = ImageEnhance.Brightness(backgroundImage).enhance(0.6)

    draw = ImageDraw(backgroundImage)
    draw.ellipse((recordPixmapX, recordPixmapY,
                  recordPixmapX + recordPixmapR * 2,
                  recordPixmapY + recordPixmapR * 2),
                 (0, 0, 0))

    for i in range(configures.background.recordArcCount, 0, -1):
        draw.ellipse(
            (
                coverImageX - recordArcBeginWidth - recordArcWidth * i - recordArcSplit * i,
                coverImageY - recordArcBeginWidth - recordArcWidth * i - recordArcSplit * i,
                coverImageX + coverImageSize + recordArcBeginWidth + recordArcWidth * i + recordArcSplit * i,
                coverImageY + coverImageSize + recordArcBeginWidth + recordArcWidth * i + recordArcSplit * i,
            ), configures.background.recordArcColor
        )
        draw.ellipse(
            (
                coverImageX - recordArcBeginWidth - recordArcWidth * (i - 1) - recordArcSplit * i,
                coverImageY - recordArcBeginWidth - recordArcWidth * (i - 1) - recordArcSplit * i,
                coverImageX + coverImageSize + recordArcBeginWidth + recordArcWidth * (i - 1) + recordArcSplit * i,
                coverImageY + coverImageSize + recordArcBeginWidth + recordArcWidth * (i - 1) + recordArcSplit * i,
            ), (0, 0, 0)
        )

    return backgroundImage.resize(configures.videoSize, Image.LANCZOS)


def get_cover_background_image(configures: Configures):
    if configures.background.coverImagePath is None:
        audioFile = mutagen.File(configures.audioInfo.audioFilePath)
        coverData = audioFile.tags["APIC:"].data
        io = BytesIO(coverData)
    else:
        io = open(configures.background.coverImagePath, "rb")

    coverImage = Image.open(io)
    coverImage = coverImage.resize((configures.background.coverImageSize,
                                    configures.background.coverImageSize))

    backgroundImage = set_background_image(Image.open(io).convert("RGB"), configures)

    return coverImage, backgroundImage


def get_cover_clip_maker(configures: Configures):
    coverImage, backgroundImage = get_cover_background_image(configures)

    if not configures.showCover:
        data = numpy.array(backgroundImage)
        return lambda t: data

    elif not configures.background.coverRotating:
        maskImage = generate_cover_circle_mask(configures.background.coverImageSize // 2)
        data = numpy.array(generate_background_image(0,
                                                     (configures.background.coverImageX,
                                                      configures.background.coverImageY),
                                                     coverImage, maskImage, backgroundImage))

        return lambda t: data

    else:
        maskImage = generate_cover_circle_mask(configures.background.coverImageSize // 2)

        def fun(t: float):
            angle = -(t % configures.background.coverImageCycle / configures.background.coverImageCycle * 360)
            return numpy.array(generate_background_image(angle,
                                                         (configures.background.coverImageX,
                                                          configures.background.coverImageY),
                                                         coverImage, maskImage, backgroundImage))

        return fun


def get_background_video_clip(settings: Configures):
    clip = VideoClip(get_cover_clip_maker(settings))
    return clip
