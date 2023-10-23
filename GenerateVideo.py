import os

import psutil
from moviepy.editor import CompositeVideoClip, AudioFileClip
from moviepy.video.VideoClip import TextClip

from BackgroundVideoClipMaker import get_background_video_clip
from LyricsTextClipMaker import get_lyrics_text_clip_list
from Configures import Configures
from LyricsPaser import get_lyrics


def get_title_text_clip(configures: Configures):
    titleClip: TextClip = TextClip(configures.audioInfo.titleText,
                                   color=configures.title.textColor,
                                   fontsize=configures.title.fontSize,
                                   font=configures.title.fontFileName)
    titleClip = titleClip.set_duration(configures.duration)
    titleClip = titleClip.set_position(("center", configures.title.posY))

    subTitleClip: TextClip = TextClip(configures.audioInfo.subTitleText,
                                      color=configures.title.textColor,
                                      fontsize=configures.title.subFontSize,
                                      font=configures.title.subFontFileName)
    subTitleClip = subTitleClip.set_duration(configures.duration)
    subTitleClip = subTitleClip.set_position(("center", configures.title.subPosY))

    return titleClip, subTitleClip


def generate_video(configures: Configures):
    if configures.audioInfo.lyricsFilePath is not None:
        with open(configures.audioInfo.lyricsFilePath, encoding='utf-8') as f:
            text = f.read()
            configures.audioInfo.lyrics = get_lyrics(text[1:] if text and text[0] == "\ufeff" else text,
                                                     configures.audioInfo.lyricsOffset)
        for i in configures.audioInfo.advancePoints:
            configures.audioInfo.lyrics[i].advance = True

    mainAudioClip = AudioFileClip(configures.audioInfo.audioFilePath, fps=configures.audioInfo.fps)
    if configures.duration is None:
        configures.duration = mainAudioClip.duration

    configures.cal()

    clips = [get_background_video_clip(configures)]
    clips.extend(get_title_text_clip(configures))
    if configures.audioInfo.lyricsFilePath is not None:
        print("Generate Lyrics Clip:")
        clips.extend(get_lyrics_text_clip_list(configures))

    mainVideoClip: CompositeVideoClip = CompositeVideoClip(
        clips,
        configures.videoSize)
    mainVideoClip = mainVideoClip.set_audio(mainAudioClip)
    mainVideoClip = mainVideoClip.set_fps(configures.fps)
    mainVideoClip = mainVideoClip.set_duration(configures.duration)

    print("当前进程的内存使用：%.4fMB" % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))
    return mainVideoClip
