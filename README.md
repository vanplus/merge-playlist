Merge Playlist
===============

A toy to merge multimedia playlists! Let's begin ^_^

![Ah!](https://i.imgur.com/fN3Nl9m.png)

I have a playlist ❤

```
CCTV-1综合HD,http://xn--g6w251d.com/.m3u8
CCTV-2财经,p8p://xn--g6w251d.com/p8p/.ts
CCTV-4国际,rtmp://xn--g6w251d.com/rtmp/live
CCTV-7军事农业,vjms://xn--g6w251d.com/vjms/live
```

I have another playlist ❤

```
CCTV-1 综合 FHD,http://xn--0zwm56d.com/.m3u8
CCTV-2,p8p://xn--0zwm56d.com/p8p/.ts
CCTV-7 国防军事 FHD,vjms://xn--0zwm56d.com/vjms/live
CCTV-8电视剧,p2p://xn--0zwm56d.com/p2p/.ts
```

Ah!


```
CCTV-1综合HD,http://xn--g6w251d.com/.m3u8
CCTV-1 综合 FHD,http://xn--0zwm56d.com/.m3u8
CCTV-2财经,p8p://xn--g6w251d.com/p8p/.ts
CCTV-2,p8p://xn--0zwm56d.com/p8p/.ts
CCTV-4国际,rtmp://xn--g6w251d.com/rtmp/live
CCTV-7军事农业,vjms://xn--g6w251d.com/vjms/live
CCTV-7 国防军事 FHD,vjms://xn--0zwm56d.com/vjms/live
CCTV-8电视剧,p2p://xn--0zwm56d.com/p2p/.ts
```

My television has a good day ❤❤❤ 

Usage
----

```sh
git clone https://github.com/vanplus/merge-playlist
cd merge-playlist
pip3 install -r requirements.txt
python3 main.py -o output.m3u8 http://example.com/playlist.m3u8 /path_to_file.txt ftp://example.com/playlist.m3u8
python3 main.py --help
```
