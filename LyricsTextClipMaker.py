from moviepy.editor import TextClip

from Configures import Configures
from LyricsPaser import Lyrics


def get_one_lyrics_text_clip(lyrics: str, configures: Configures,
                             showStartTime: float, currentStartTime: float,
                             currentEndTime: float, showEndTime: float) -> [TextClip]:
    moveTime = configures.lyrics.lineSplit / configures.lyrics.moveSpeed

    bottomClip: TextClip = TextClip(lyrics, fontsize=configures.lyrics.fontSize,
                                    font=configures.lyrics.fontFileName,
                                    color=configures.lyrics.color)\
        .set_fps(configures.fps)\
        .set_start(showStartTime)\
        .set_end(currentStartTime + moveTime/2)
    topClip: TextClip = TextClip(lyrics, fontsize=configures.lyrics.fontSize,
                                 font=configures.lyrics.fontFileName,
                                 color=configures.lyrics.color)\
        .set_fps(configures.fps)\
        .set_start(currentEndTime - moveTime/2)\
        .set_end(showEndTime)
    middleClip: TextClip = TextClip(lyrics, fontsize=configures.lyrics.fontSize,
                                    font=configures.lyrics.currentFontFileName,
                                    color=configures.lyrics.currentColor)\
        .set_fps(configures.fps)\
        .set_start(currentStartTime + moveTime/2)\
        .set_end(currentEndTime - moveTime/2)

    moveUpStartTime = currentStartTime - showStartTime - moveTime/2
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

    return bottomClip, middleClip, topClip


def get_lyrics_text_clip_list(configures: Configures) -> [TextClip]:
    lyricsTextClipList = []
    lyricsList: [Lyrics] = configures.audioInfo.lyrics
    lyricsLength = len(configures.audioInfo.lyrics)
    lyricsTextClipList.extend(get_one_lyrics_text_clip(
        lyricsList[0].text, configures, 0, lyricsList[0].time, lyricsList[1].time, lyricsList[2].time
    ))
    print(f"Generate Lyrics Clip: " + str(lyricsList[0]))

    for i in range(1, lyricsLength-2):
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[i].text, configures,
            lyricsList[i-1].time, lyricsList[i].time,
            lyricsList[i+1].time, lyricsList[i+2].time
        ))
        print(f"Generate Lyrics Clip: " + str(lyricsList[i]))
    if lyricsLength == 2:
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[1].text, configures,
            lyricsList[0].time, lyricsList[1].time,
            configures.duration, configures.duration
        ))
        print(f"Generate Lyrics Clip: " + str(lyricsList[1]))
    else:
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[-2].text, configures,
            lyricsList[-3].time, lyricsList[-2].time,
            lyricsList[-1].time, configures.duration
        ))
        print(f"Generate Lyrics Clip: " + str(lyricsList[-2]))
        lyricsTextClipList.extend(get_one_lyrics_text_clip(
            lyricsList[-1].text, configures,
            lyricsList[-2].time, lyricsList[-1].time,
            configures.duration, configures.duration
        ))
        print(f"Generate Lyrics Clip: " + str(lyricsList[-1]))

    return lyricsTextClipList
