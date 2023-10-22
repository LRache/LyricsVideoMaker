import numpy as np
from PIL import Image
import threading
import time

from Configures import Configures

THREADING_COUNT = 2


def copy_pix(pix1, pix2, x1, y1, x2, y2):
    pix1[x1, y1] = pix2[x2, y2]


def cal_cover_circle_points(radius: int) -> (list[tuple[int, int]]):
    xArray, yArray = np.mgrid[-radius:radius, -radius:radius]
    indexArray = (xArray ** 2 + yArray ** 2) <= radius ** 2
    return xArray[indexArray], yArray[indexArray]
    # return list((x, y) for x, y in zip(xArray[indexArray], yArray[indexArray]))


def get_zip(x, y):
    return zip(x, y)


def generate_cover_image(degree, coverImage, newCoverImageSize, multipy, dxArray, dyArray):
    rotatedCoverImage: Image.Image = coverImage.rotate(degree, Image.BILINEAR, expand=True)
    newCoverImage: Image.Image = Image.new("RGBA", (newCoverImageSize * multipy, newCoverImageSize * multipy))
    rotatedCoverPix = rotatedCoverImage.load()
    newCoverPix = newCoverImage.load()

    rotatedCenterX = rotatedCoverImage.size[0] // 2
    rotatedCenterY = rotatedCoverImage.size[1] // 2
    newCoverCenter = newCoverImageSize * multipy // 2
    for dx, dy in zip(dxArray, dyArray):
        copy_pix(newCoverPix, rotatedCoverPix, newCoverCenter + dx, newCoverCenter + dy,
                 rotatedCenterX + dx, rotatedCenterY + dy)
    newCoverImage = newCoverImage.resize((newCoverImageSize, newCoverImageSize), resample=Image.LANCZOS)
    return newCoverImage


class Counter:
    def __init__(self, total):
        self.c = 0
        self.total = total
        self.startTime = 0

    def start(self):
        self.startTime = time.perf_counter()

    def count(self):
        self.c += 1
        print(f"\rBackground Cache: [{round(self.c / self.total * 100, 2)}%]{self.c}/{self.total} "
              f"{round(time.perf_counter() - self.startTime, 2)}s", end="")


class CacheThread(threading.Thread):
    def __init__(self, configures: Configures, taskList: [int], cache: list,
                 coverImage: Image, counter: Counter, dArrayZip: zip):
        super().__init__()
        self.configures = configures
        self.taskList = taskList
        self.cache = cache
        self.coverImage = coverImage
        self.counter = counter
        self.dArrayZip = dArrayZip

    def run(self) -> None:
        configures = self.configures
        degreeSpeed = configures.background.coverImageSpeed[0]
        """newCoverImageSize = (configures.background.coverImageSize * configures.multipy,
                             configures.background.coverImageSize * configures.multipy)
        sx = sy = r = configures.background.coverImageSize // 2 * configures.multipy
        r2 = r ** 2"""

        for frameIndex in self.taskList:
            degree = -frameIndex * degreeSpeed

            """rotatedCoverImage = self.coverImage.rotate(degree, Image.BILINEAR, expand=True)
            newCoverImage = Image.new("RGBA", newCoverImageSize)
            rotatedCoverPix = rotatedCoverImage.load()
            newCoverPix = newCoverImage.load()

            ox = rotatedCoverImage.size[0] // 2
            oy = rotatedCoverImage.size[1] // 2
            xArray = np.array(list(x for x in range(ox - r, ox + r) for _ in range(2 * r)))
            dxArray = xArray - ox
            yArray = np.array(list(y for _ in range(2 * r) for y in range(oy - r, oy + r)))
            dyArray = yArray - oy
            indexArray = (np.power(dxArray, 2) + np.power(dyArray, 2)) <= r2
            for dx, dy, x, y in zip(dxArray[indexArray], dyArray[indexArray], xArray[indexArray], yArray[indexArray]):
                newCoverPix[sx + dx, sy + dy] = rotatedCoverPix[x, y]

            
            for x in range(ox - r, ox + r):
                for y in range(oy - r, oy + r):
                    dx = x - ox
                    dy = y - oy
                    d = (dx * dx + dy * dy)
                    if d <= r2:
                        newCoverPix[sx + dx, sy + dy] = rotatedCoverPix[x, y]
            newCoverImage = newCoverImage.resize((r, r), resample=Image.LANCZOS)"""

            self.cache[frameIndex] = generate_cover_image(degree, self.coverImage,
                                                          self.configures.background.coverImageSize,
                                                          self.configures.multipy, self.dArrayZip)
            self.counter.count()


def get_cover_image_cache_list(configures: Configures, coverImage: Image):
    totalCoverFrameCount = int(360 / configures.background.coverImageSpeed[0])
    cache: list[None | Image.Image] = [None for _ in range(totalCoverFrameCount)]

    """threads = []
    counter = Counter(totalCoverFrameCount)
    for i in range(THREADING_COUNT):
        threads.append(CacheThread(configures,
                                   [j for j in range(i, totalCoverFrameCount, THREADING_COUNT)],
                                   cache, coverImage, counter))
    counter.start()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()"""

    dxArray, dyArray = cal_cover_circle_points(configures.background.coverImageSize * configures.multipy // 2)
    degreeSpeed = configures.background.coverImageSpeed[0]
    counter = Counter(totalCoverFrameCount)
    counter.start()
    for frameIndex in range(totalCoverFrameCount):
        degree = -frameIndex * degreeSpeed
        cache[frameIndex] = generate_cover_image(degree, coverImage, configures.background.coverImageSize,
                                                 configures.multipy, dxArray, dyArray)
        counter.count()
    cache[10].show()
    print()
    return cache


def test():
    coverImage = Image.open("D://Pictures//音乐专辑封面//曾经我也想过一了百了.jpg")
    coverImage = coverImage.resize((800, 800))
    circlePoints = cal_cover_circle_points(400)
    newCoverImage = generate_cover_image(-60, coverImage, 800, 2, circlePoints)
    newCoverImage.save("./debug/test1.png")
    newCoverImage = generate_cover_image(-30, coverImage, 800, 2, circlePoints)
    newCoverImage.save("./debug/test2.png")


if __name__ == '__main__':
    test()
