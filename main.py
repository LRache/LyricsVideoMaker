from Configures import Configures, load_configures
from GenerateVideo import generate_video
from VideoPreviewer import MainWindow, VideoViewer

from PyQt5.QtWidgets import QApplication

import sys
import os
import psutil
import argparse
import gc
import time


def preview_video(configures):
    app = QApplication(sys.argv)
    window = MainWindow(configures)
    window.centerWidget.videoViewer.resize_viewer(VideoViewer.ViewerSize.SIZE_1080p)
    window.show()
    window.play_preview()
    return app.exec_()


def main():
    if len(sys.argv) == 1:
        return

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-path", dest="list", nargs="+", help="Configures.json文件名")
    parser.add_argument("-p", action="store_true", help="启用预览")
    parser.add_argument("-f", action="store_true", help="全屏预览")
    parser.add_argument("-nocache", action="store_true")
    parser.add_argument("--offset", type=float, default=0.0, help="歌词偏移时间")

    args = parser.parse_args()
    path = args.list
    preview = args.p
    offset = args.offset
    nocache = args.nocache

    for p in path:
        print("当前进程的内存使用：%.4fMB" % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))
        print(f'处理"{p}"')
        configures = Configures()
        load_configures(configures, p)
        configures.audioInfo.lyricsOffset += offset
        if nocache:
            configures.useCache = False

        if preview:
            preview_video(configures)
        else:
            startTime = time.time()
            videoClip = generate_video(configures)
            videoClip.write_videofile(configures.output.filePath,
                                      codec=configures.output.videoCodec,
                                      bitrate=configures.output.bitrate,
                                      audio_codec=configures.output.audioCodec)
            print(f"Finished in {time.time() - startTime}s")
            videoClip.close()
            del videoClip
        gc.collect()


if __name__ == '__main__':
    main()
