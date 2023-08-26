from moviepy.video.VideoClip import VideoClip
import numpy
import mutagen
from PIL import Image, ImageFilter, ImageEnhance
from PIL.ImageDraw import ImageDraw

from io import BytesIO

from Configures import Configures
from BackgroundCache import get_background_cache


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
    audioFile = mutagen.File(configures.audioInfo.audioFilePath)
    if configures.background.coverImagePath is None:
        coverData = audioFile.tags["APIC:"].data
        io = BytesIO(coverData)
    else:
        io = open(configures.background.coverImagePath, "rb")

    coverImage = Image.open(io)
    coverImage = coverImage.resize((configures.background.coverImageSize * configures.multipy,
                                    configures.background.coverImageSize * configures.multipy))

    backgroundImage = set_background_image(Image.open(io).convert("RGBA"), configures)

    return coverImage, backgroundImage


def get_cover_clip_maker(configures: Configures):
    coverImage, backgroundImage = get_cover_background_image(configures)

    sx = sy = r = configures.background.coverImageSize // 2 * configures.multipy
    r2 = r ** 2
    newCoverImageSize = (configures.background.coverImageSize * configures.multipy,
                         configures.background.coverImageSize * configures.multipy)
    cycle = configures.background.coverImageCycle
    degreeSpeed = -360 / cycle

    if not configures.showCover:
        data = numpy.array(backgroundImage)

        def fun(t: float):
            return data
        return fun

    elif not configures.background.coverRotating:
        newBackgroundImage = backgroundImage.copy()
        newCoverImage = Image.new("RGBA", newCoverImageSize)
        coverPix = coverImage.load()
        newCoverPix = newCoverImage.load()

        ox = coverImage.size[0] // 2
        oy = coverImage.size[1] // 2
        for x in range(ox - r, ox + r):
            for y in range(oy - r, oy + r):
                dx = x - ox
                dy = y - oy
                d = (pow(dx, 2) + pow(dy, 2))
                if d <= r2:
                    newCoverPix[r + dx, r + dy] = coverPix[x, y]
        newCoverImage = newCoverImage.resize((r, r), resample=Image.LANCZOS)
        newBackgroundImage.paste(newCoverImage,
                                 (configures.background.coverImageX, configures.background.coverImageY),
                                 mask=newCoverImage.split()[3])
        data = numpy.array(newBackgroundImage.convert("RGB"))

        return lambda t: data

    elif configures.useCache:
        imageCache = get_background_cache(configures, coverImage, backgroundImage)

        def fun(t: float):
            t = round(t % cycle, 2)
            if t in imageCache:
                return imageCache[t]

            degree = round(t * degreeSpeed, 2)
            rotatedCoverImage = coverImage.rotate(degree, Image.BILINEAR, expand=True)
            newBackgroundImage = backgroundImage.copy()
            newCoverImage = Image.new("RGBA", newCoverImageSize)
            rotatedCoverPix = rotatedCoverImage.load()
            newCoverPix = newCoverImage.load()

            ox = rotatedCoverImage.size[0] // 2
            oy = rotatedCoverImage.size[1] // 2
            for x in range(ox - r, ox + r):
                for y in range(oy - r, oy + r):
                    dx = x - ox
                    dy = y - oy
                    d = (pow(dx, 2) + pow(dy, 2))
                    if d <= r2:
                        newCoverPix[sx + dx, sy + dy] = rotatedCoverPix[x, y]
            newCoverImage = newCoverImage.resize((r, r), resample=Image.LANCZOS)
            newBackgroundImage.paste(newCoverImage,
                                     (configures.background.coverImageX, configures.background.coverImageY),
                                     mask=newCoverImage.split()[3])
            data = numpy.array(newBackgroundImage.convert("RGB"))
            imageCache[degree] = data
            return data
    else:
        def fun(t: float):
            degree = round(t % cycle * degreeSpeed, 2)
            rotatedCoverImage = coverImage.rotate(degree, Image.BILINEAR, expand=True)
            newBackgroundImage = backgroundImage.copy()
            newCoverImage = Image.new("RGBA", newCoverImageSize)
            rotatedCoverPix = rotatedCoverImage.load()
            newCoverPix = newCoverImage.load()

            ox = rotatedCoverImage.size[0] // 2
            oy = rotatedCoverImage.size[1] // 2
            for x in range(ox - r, ox + r):
                for y in range(oy - r, oy + r):
                    dx = x - ox
                    dy = y - oy
                    d = (pow(dx, 2) + pow(dy, 2))
                    if d <= r2:
                        newCoverPix[sx + dx, sy + dy] = rotatedCoverPix[x, y]
            newCoverImage = newCoverImage.resize((r, r), resample=Image.LANCZOS)
            newBackgroundImage.paste(newCoverImage,
                                     (configures.background.coverImageX, configures.background.coverImageY),
                                     mask=newCoverImage.split()[3])
            data = numpy.array(newBackgroundImage.convert("RGB"))
            return data

    return fun


def get_background_video_clip(settings: Configures):
    clip = VideoClip(get_cover_clip_maker(settings))
    return clip
