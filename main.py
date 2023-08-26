from Configures import Configures, load_configures
from GenerateVideo import generate_video

import sys
import argparse


def main():
    if len(sys.argv) == 1:
        exit()

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("path", type=str, help="Configures.json文件名")
    parser.add_argument("-p", action="store_true", help="启用预览")
    parser.add_argument("-nocache", action="store_true")
    parser.add_argument("--start", type=float, default=0.0, help="预览开始时间")
    parser.add_argument("--end", type=float, default=None, help="预览结束时间")
    parser.add_argument("--offset", type=float, default=0.0, help="歌词偏移时间")

    args = parser.parse_args()
    path = args.path
    preview = args.p
    start = args.start
    end = args.end
    offset = args.offset
    nocache = args.nocache

    configures = Configures()
    load_configures(configures, path)
    configures.audioInfo.lyricsOffset += offset
    if preview:
        configures.preview = True
        configures.background.coverRotating = False
    if nocache:
        configures.useCache = False
    generate_video(configures, start, end)


if __name__ == '__main__':
    main()
