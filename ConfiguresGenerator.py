import urllib.request
import urllib.parse
import sys
import json
import os
import copy
import requests

CONFIGURES_EXAMPLE = \
    {
        "audioFilePath": "",
        "coverFilePath": None,
        "lyricsFilePath": None,
        "multilineLyrics": False,
        "advancePoints": [],
        "lyricsOffset": 0,
        "title": "",
        "subTitle": "",

        "outputFilePath": "",
        "outputVideoCodec": "h264_nvenc",
        "outputAudioCodec": "aac",
        "bitrate": "5000k",

        "duration": None,
        "fps": 30,
        "coverCycle": 50,
        "coverRotating": True,

        "application": {
            "useCache": True,
            "showCover": True,
            "preview": False
        }
    }


class ConfiguresFile:
    def __init__(self, songId: str, translation: bool, fp: str, downloadCover: bool):
        self.songId = songId
        self.hasTranslation = translation
        self.filepath = fp
        self.songName = ""
        self.singerNames = []
        self.albumName = ""
        self.lyricsList = {}
        self.downloadCover = downloadCover
        self.coverUrl = ""

    def load(self):
        lyricsResponse = urllib.request.urlopen(f"https://music.163.com/api/song/media?id={self.songId}")
        lyricsText = json.loads(lyricsResponse.read())["lyric"]
        for line in lyricsText.split("\n"):
            if line and line[0] == "[":
                if not line[1].isdigit():
                    continue
                r = 0
                for c in line:
                    if c == "]":
                        break
                    r += 1
                self.lyricsList[line[:r+1]] = line[r+1:]

        if self.hasTranslation:
            translationResponse = urllib.request.urlopen(f"https://music.163.com/api/song/lyric?id={self.songId}&tv=-1")
            translationText = json.loads(translationResponse.read())["tlyric"]["lyric"]
            for line in translationText.split("\n"):
                if line and line[0] == "[":
                    if not line[1].isdigit():
                        continue
                    r = 0
                    for c in line:
                        if c == "]":
                            break
                        r += 1
                    timeStr = line[:r + 1]
                    if timeStr in self.lyricsList:
                        self.lyricsList[timeStr] += "\\n"+line[r + 1:]

    def write_file(self, dirname: str, outputDir: str):
        singerNames = ' '.join(self.singerNames)
        lyricsPath = f"{dirname}//{self.songName} - {singerNames}.lrc"
        configures = copy.deepcopy(CONFIGURES_EXAMPLE)

        if self.downloadCover:
            b = requests.get(self.coverUrl).content
            with open(f"{dirname}//{self.songName} - {singerNames}.jpg", "wb") as f:
                f.write(b)
            configures["coverFilePath"] = f"{dirname}//{self.songName} - {singerNames}.jpg"

        configures["audioFilePath"] = self.filepath
        configures["title"] = self.songName
        configures["subTitle"] = f"{singerNames} - {self.albumName}"
        configures["lyricsFilePath"] = f"//{self.songName} - {singerNames}.lrc"
        configures["multilineLyrics"] = self.hasTranslation
        configures["outputFilePath"] = f"{outputDir}//{self.songName} - {singerNames}.mp4"

        with open(lyricsPath, "w", encoding="utf-8") as f:
            lyricLines = [time+lyrics for time, lyrics in self.lyricsList.items()]
            lyricLines.sort()
            for line in lyricLines:
                f.writelines(line+'\n')

        with open(f"{dirname}//{self.songName} - {singerNames}.json", "w", encoding="utf-8") as f:
            json.dump(configures, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        exit()
    lyricsFiles = []
    f = open(sys.argv[1], encoding="utf-8")
    for line in f:
        if not line:
            continue
        songId, t, filepath, cover = line.strip().split("\t")
        if not songId.isdecimal():
            p = urllib.parse.urlparse(songId)
            songId = urllib.parse.parse_qs(p.query)["id"][0]
        lyricsFiles.append(ConfiguresFile(songId, t == "1", filepath, cover == "1"))
    f.close()

    dirname = os.path.dirname(os.path.abspath(sys.argv[1]))
    url = 'https://music.163.com/api/v3/song/detail?c=[%s]' % (",".join('{id:"%s"}' % l.songId for l in lyricsFiles))
    songInfoResponse = urllib.request.urlopen(url)
    songInfoData = json.loads(songInfoResponse.read())["songs"]
    for i in range(len(lyricsFiles)):
        lyricsFiles[i].songName = songInfoData[i]["name"]
        lyricsFiles[i].singerNames = list(j["name"] for j in songInfoData[i]["ar"])
        lyricsFiles[i].albumName = songInfoData[i]["al"]["name"]
        lyricsFiles[i].coverUrl = songInfoData[i]["al"]["picUrl"]
        lyricsFiles[i].load()
        lyricsFiles[i].write_file(dirname, sys.argv[2])
