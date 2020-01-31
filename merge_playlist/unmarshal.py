import os
import re
from urllib.request import urlopen

from urllib.parse import urlparse
from itertools import chain


def unmarshal_playlist(url_or_file_path):
    if os.path.isfile(url_or_file_path):
        is_url = False
    elif urlparse(url_or_file_path).scheme != "":
        is_url = True
    else:
        raise ValueError("not a url or file system path")

    with urlopen(url_or_file_path) if is_url else open(url_or_file_path, 'rb') as src:
        return _unmarshal_playlist(src)


TXT_GROUP_LINE_SUFFIX = "#genre#"
M3U_SIGN = "#EXTM3U"
M3U_CHANNEL_TAG = "#EXTINF"


def _unmarshal_playlist(src):
    from enum import Enum

    class Format(Enum):
        M3U = 1
        TXT = 2
        OTHERS = 3

    # 根据第一行信息判断文件是 .m3u(8) 还是 .txt
    first_line = src.readline()
    if first_line.startswith(M3U_SIGN.encode('utf-8')):
        which_format = Format.M3U
    elif first_line.strip().endswith(TXT_GROUP_LINE_SUFFIX.encode('utf-8')):
        which_format = Format.TXT
    else:
        raise AttributeError("unsupported playlist format")

    ret = []

    file_lines = chain([first_line], src.readlines())

    def _next_line():
        return next(file_lines).strip().decode("utf-8")

    def parse_m3u():

        def _parse_m3u_channel_attributes(_line):
            def wanna_attr(attr_name):
                want = re.findall(r'{}=\"(.+?)\"'.format(attr_name), _line)
                return want[0] if want else ""

            duration = re.findall(r'{}:([^\s]+)'.format(M3U_CHANNEL_TAG), _line)[0]
            tvg_id = wanna_attr("tvg-id")
            tvg_name = wanna_attr("tvg-name")
            tvg_logo = wanna_attr("tvg-logo")
            group_title = wanna_attr("group-title")
            _channel_name = re.findall(r',(.+?)$', _line)
            _channel_name = _channel_name[0] if _channel_name else ""
            _channel_name = purify_channel_name(_channel_name)

            return [duration, tvg_id, tvg_name, tvg_logo, group_title, _channel_name]

        try:
            _line = _next_line()
        except StopIteration:
            return

        if _line.startswith(M3U_CHANNEL_TAG):
            channel = _parse_m3u_channel_attributes(_line)
            channel.append(_next_line())
            ret.append(channel)

        parse_m3u()

    def parse_txt(current_group_title=""):
        try:
            _line = _next_line()
        except StopIteration:
            return

        if _line.endswith(TXT_GROUP_LINE_SUFFIX):
            current_group_title = _line[:-len(TXT_GROUP_LINE_SUFFIX) - 1]
        else:
            wanna_channel = _line.split(",")
            if len(wanna_channel) == 2:
                channel_name, url = wanna_channel
                channel_name = purify_channel_name(channel_name)
                # duration, tvg_id, tvg_name, tvg_logo, group_title, channel_name, url
                channel = ["-1", "", "", "", current_group_title, channel_name, url]
                ret.append(channel)

        parse_txt(current_group_title)

    if which_format is Format.M3U:
        parse_m3u()
    elif which_format is Format.TXT:
        parse_txt()
    else:
        raise AssertionError("unreachable!")

    return ret


# e.g.: '[国语|香港] 凤凰 中文 FHD' => '凤凰 中文 FHD'
def purify_channel_name(raw_name):
    purified = re.sub(r'\(.+?\)|\[.+?\]', '', raw_name).strip()
    return raw_name if not purified else purified
