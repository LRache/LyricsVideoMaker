from moviepy.editor import CompositeVideoClip, AudioFileClip, vfx
from moviepy.video.VideoClip import TextClip

from BackgroundVideoClipMaker import get_background_video_clip
from LyricsTextClipMaker import get_lyrics_text_clip_list
from Configures import Configures
from LyricsPaser import get_lyrics

import time


def get_title_text_clip(configures: Configures):
    titleClip: TextClip = TextClip(configures.audioInfo.titleText,
                                   color=configures.title.textColor,
                                   fontsize=configures.title.fontSize,
                                   font=configures.title.fontFileName)
    titleClip = titleClip.set_duration(configures.duration)
    titleClip = titleClip.set_position(("center", configures.title.posY))

    title2Clip: TextClip = TextClip(configures.audioInfo.subTitleText,
                                    color=configures.title.textColor,
                                    fontsize=configures.title.subFontSize,
                                    font=configures.title.subFontFileName)
    title2Clip = title2Clip.set_duration(configures.duration)
    title2Clip = title2Clip.set_position(("center", configures.title.subPosY))

    return titleClip, title2Clip


def generate_video(configures: Configures, start: float = None, end: float = None):
    startTime = time.time()
    if configures.audioInfo.lyricsFilePath is not None:
        with open(configures.audioInfo.lyricsFilePath, encoding='utf-8') as f:
            text = f.read()
            configures.audioInfo.lyrics = get_lyrics(text[1:] if text and text[0] == "\ufeff" else text,
                                                     configures.audioInfo.lyricsOffset)

    mainAudioClip = AudioFileClip(configures.audioInfo.audioFilePath)
    if configures.duration is None:
        configures.duration = mainAudioClip.duration

    configures.cal()

    clips = [get_background_video_clip(configures)]
    clips.extend(get_title_text_clip(configures))
    if configures.audioInfo.lyricsFilePath is not None:
        clips.extend(get_lyrics_text_clip_list(configures))

    mainVideoClip: CompositeVideoClip = CompositeVideoClip(
        clips,
        configures.videoSize)
    mainVideoClip = mainVideoClip.set_audio(mainAudioClip)
    mainVideoClip = mainVideoClip.set_fps(configures.fps)
    mainVideoClip = mainVideoClip.set_duration(configures.duration)

    if configures.preview:
        mainVideoClip.subclip(start, end).preview()
    else:
        mainVideoClip.write_videofile(configures.output.filePath,
                                      codec=configures.output.videoCodec,
                                      bitrate=configures.output.bitrate,
                                      audio_codec=configures.output.audioCodec)
        print(f"Finished in {time.time() - startTime}s")
