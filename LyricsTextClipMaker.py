import numpy
from PIL import Image, ImageDraw
from moviepy.editor import TextClip, ImageClip

from Configures import Configures
from LyricsPaser import Lyrics


advancePointImageClip: ImageClip


def get_one_lyrics_text_clip(lyrics: str, configures: Configures,
                             showStartTime: float, currentStartTime: float,
                             currentEndTime: float, showEndTime: float,
                             advance: bool = False) -> [TextClip]:
    if not lyrics:
        return []

    clips = []
    if advance:
        pointClip0 = advancePointImageClip.set_position(configures.advancePointPositionList[0]) \
            .set_start(max(currentStartTime - 6, 0)).set_end(currentStartTime-0.8)
        pointClip1 = advancePointImageClip.set_position(configures.advancePointPositionList[1])\
            .set_start(max(currentStartTime - 6, 0)).set_end(currentStartTime-1.8)
        pointClip2 = advancePointImageClip.set_position(configures.advancePointPositionList[2]) \
            .set_start(max(currentStartTime - 6, 0)).set_end(currentStartTime-2.8)

        clips.extend((pointClip0, pointClip1, pointClip2))

    moveTime = configures.lyrics.lineSplit / configures.lyrics.moveSpeed

    bottomClip: TextClip = TextClip(lyrics, fontsize=configures.lyrics.fontSize,
                                    font=configures.lyrics.fontFileName,
                                    color=configures.lyrics.color)\
        .set_fps(configures.fps)\
        .set_start(showStartTime)\
        .set_end(currentStartTime)
    topClip: TextClip = TextClip(lyrics, fontsize=configures.lyrics.fontSize,
                                 font=configures.lyrics.fontFileName,
                                 color=configures.lyrics.color)\
        .set_fps(configures.fps)\
        .set_start(currentEndTime - moveTime)\
        .set_end(showEndTime)
    middleClip: TextClip = TextClip(lyrics, fontsize=configures.lyrics.fontSize,
                                    font=configures.lyrics.currentFontFileName,
                                    color=configures.lyrics.currentColor)\
        .set_fps(configures.fps)\
        .set_start(currentStartTime)\
        .set_end(currentEndTime - moveTime)

    moveUpStartTime = currentStartTime - showStartTime - moveTime
    moveUpStopTime = configures.lyrics.lineSplit / configures.lyrics.moveSpeed

    def bottom_clip_move_fun(t: float):
        if t <= moveUpStartTime:
            return "center", configures.lyrics.lineY[2]
        else:
            return "center", configures.lyrics.lineY[2] - (t - moveUpStartTime) * configures.lyrics.moveSpeed

    def top_clip_move_fun(t: float):
        if t <= moveUpStopTime:
            return "center", configures.lyrics.lineY[0] + (moveUpStopTime - t) * configures.lyrics.moveSpeed
        else:
            return "center", configures.lyrics.lineY[0]

    bottomClip = bottomClip.set_position(bottom_clip_move_fun).crossfadein(0.5)
    topClip = topClip.set_position(top_clip_move_fun).crossfadeout(0.5)
    middleClip = middleClip.set_position(("center", configures.lyrics.lineY[1]))
    clips.extend((bottomClip, middleClip, topClip))

    return clips


def get_lyrics_text_clip_list(configures: Configures) -> [TextClip]:
    global advancePointImageClip

    lyricsTextClipList = []
    lyricsList: [Lyrics] = configures.audioInfo.lyrics
    lyricsLength = len(configures.audioInfo.lyrics)

    lyricsTextClipList.extend(get_one_lyrics_text_clip(
        lyricsList[0].text, configures, 0, lyricsList[0].time, lyricsList[1].time, lyricsList[2].time,
        lyricsList[0].advance
    ))
    print(str(lyricsList[0]))

    advancePointImage = Image.new("RGBA", (configures.advancePointSize, configures.advancePointSize))
    drawer = ImageDraw.ImageDraw(advancePointImage)
    drawer.ellipse((0, 0, configures.advancePointSize, configures.advancePointSize), fill=configures.advancePointColor)
    advancePointImageClip = ImageClip(numpy.array(advancePointImage), transparent=True)

    for i in range(1, lyricsLength-2):
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[i].text, configures,
            lyricsList[i-1].time, lyricsList[i].time,
            lyricsList[i+1].time, lyricsList[i+2].time,
            lyricsList[i].advance
        ))
        print(str(lyricsList[i]))
    if lyricsLength == 2:
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[1].text, configures,
            lyricsList[0].time, lyricsList[1].time,
            configures.duration, configures.duration,
            lyricsList[1].advance
        ))
        print(str(lyricsList[1]))
    else:
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[-2].text, configures,
            lyricsList[-3].time, lyricsList[-2].time,
            lyricsList[-1].time, configures.duration,
            lyricsList[-2].advance
        ))
        print(str(lyricsList[-2]))
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[-1].text, configures,
            lyricsList[-2].time, lyricsList[-1].time,
            configures.duration, configures.duration,
            lyricsList[-1].advance
        ))
        print(str(lyricsList[-1]))

    return lyricsTextClipList
