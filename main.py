import argparse
import os
import sys

from merge_playlist.marshal import marshal_playlist
from merge_playlist.merge import merge, DEFAULT_SIMILAR_THRESHOLD
from merge_playlist.unmarshal import unmarshal_playlist


def main():
    parser = argparse.ArgumentParser(description='A toy to merge multimedia playlists')
    parser.add_argument('inputs', metavar='INPUT', type=str, nargs='+',
                        help='location of a .txt/.m3u8 file, either url or file system path')
    parser.add_argument('-o', '--output', type=str,
                        help='write merged playlist to filepath.txt or filepath.m3u8, STDOUT if omitted')
    parser.add_argument('--threshold', type=float, default=DEFAULT_SIMILAR_THRESHOLD,
                        help='if channel name similarity value less than threshold, it is not similar. default: {}'.format(
                            DEFAULT_SIMILAR_THRESHOLD))
    args = parser.parse_args()
    leader_playlist, *crowd_playlists = args.inputs
    output = args.output
    similar_threshold = args.threshold

    leader_playlist = unmarshal_playlist(leader_playlist)
    crowd_playlists = [unmarshal_playlist(crowd_playlist) for crowd_playlist in crowd_playlists]

    playlist = merge(leader_playlist, *crowd_playlists, similar_threshold=similar_threshold)

    if not output:
        output_type = "txt"
        output_file = sys.stdout
    else:
        _, output_ext = os.path.splitext(output)
        output_type = "m3u" if output_ext in [".m3u", ".m3u8"] else "txt"
        output_file = open(output, "w", encoding='utf8')

    playlist_content = marshal_playlist(playlist, output_type)
    print(playlist_content, file=output_file, end='')

    if output:
        output_file.close()


if __name__ == '__main__':
    main()
