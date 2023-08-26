class Lyrics:
    def __init__(self, text: str, time):
        self.text = text.replace("\\n", "\n") if len(text) != 0 else " "
        self.time = time

    def __str__(self):
        minute = self.time // 60
        ms = self.time*1000 % 60000
        return "[%.2d:%.2d.%.3d]%s" % (minute, ms // 1000, ms % 1000, self.text)


def get_lyrics(lyricsText: str, offset: float = 0.0) -> [Lyrics]:
    lyrics = []
    for line in lyricsText.split("\n"):
        if line and line[0] == "[":
            if not line[1].isdigit():
                continue
            r = 0
            for c in line:
                r += 1
                if c == "]":
                    break
            m, s = map(float, line[1:r-1].split(":"))
            lyrics.append(Lyrics(line[r:], m*60+s+offset))
    return lyrics
