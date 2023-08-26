from PIL import Image
import threading
import numpy
import time

from Configures import Configures


THREADING_COUNT = 8


class Counter:
    def __init__(self, total):
        self.c = 0
        self.total = total
        self.startTime = 0

    def start(self):
        self.startTime = time.perf_counter()

    def count(self):
        self.c += 1
        print(f"\rBackground Cache: [{round(self.c/self.total * 100, 2)}%]{self.c}/{self.total} "
              f"{round(time.perf_counter()-self.startTime, 2)}s", end="")


class CacheThread(threading.Thread):
    def __init__(self, configures: Configures, taskList: [float], cache: dict,
                 coverImage: Image, backgroundImage: Image,
                 counter: Counter):
        super().__init__()
        self.configures = configures
        self.taskList = taskList
        self.cache = cache
        self.coverImage = coverImage
        self.backgroundImage = backgroundImage
        self.counter = counter

    def run(self) -> None:
        configures = self.configures
        degreeSpeed = -360 / configures.background.coverImageCycle
        newCoverImageSize = (configures.background.coverImageSize * configures.multipy,
                             configures.background.coverImageSize * configures.multipy)
        sx = sy = r = configures.background.coverImageSize // 2 * configures.multipy
        r2 = r ** 2

        for t in self.taskList:
            degree = round(t * degreeSpeed, 2)

            rotatedCoverImage = self.coverImage.rotate(degree, Image.BILINEAR, expand=True)
            newBackgroundImage = self.backgroundImage.copy()
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
            self.cache[t] = data
            self.counter.count()


def get_background_cache(configures: Configures, coverImage: Image, backgroundImage: Image):
    step = 1 / configures.fps
    cache = {round(i * step, 2): None for i in range(configures.background.coverImageCycle * configures.fps)}

    tasks = list(cache.keys())
    threads = []
    counter = Counter(len(cache))
    for i in range(THREADING_COUNT):
        threads.append(CacheThread(configures,
                                   [tasks[j] for j in range(i, len(tasks), THREADING_COUNT)],
                                   cache, coverImage, backgroundImage, counter))
    counter.start()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print()
    return cache
