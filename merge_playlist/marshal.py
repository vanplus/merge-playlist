from merge_playlist.unmarshal import TXT_GROUP_LINE_SUFFIX, M3U_SIGN, M3U_CHANNEL_TAG


def marshal_playlist(playlist, output_type):
    if output_type == "m3u":
        return _marshal_playlist_m3u(playlist)
    elif output_type == "txt":
        return _marshal_playlist_txt(playlist)
    else:
        raise AttributeError("unsupported playlist format")


def _marshal_playlist_m3u(playlist):
    content = M3U_SIGN + '\n'
    for duration, tvg_id, tvg_name, tvg_logo, group_title, channel_name, url in playlist:
        content += '{}:{} tvg-id="{}" tvg-name="{}" tvg-logo="{}" group-title="{}",{}\n{}\n'.format(M3U_CHANNEL_TAG,
                                                                                                    duration,
                                                                                                    tvg_id,
                                                                                                    tvg_name,
                                                                                                    tvg_logo,
                                                                                                    group_title,
                                                                                                    channel_name,
                                                                                                    url)
    return content


def _marshal_playlist_txt(playlist):
    content = ""

    current_group = None
    for _, _, _, _, group_title, channel_name, url in playlist:
        if group_title != current_group:
            current_group = group_title
            content += "{},{}\n".format(current_group, TXT_GROUP_LINE_SUFFIX)
        content += "{},{}\n".format(channel_name, url)

    return content
