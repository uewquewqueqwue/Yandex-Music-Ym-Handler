import argparse
import re

from typing import Literal, Tuple
from re_parsing.re_parser import ReParser


YANDEX_MUSIC_ALBUM: str = 'https://music.yandex.ru/album/'
EXAMPLE_LINKS: list = ['https://music.yandex.ru/album/123123',
                       'https://music.yandex.ru/album/123123/track/123123']


def parse(end: str) -> Tuple[str, str, Tuple[str, str, str, str], str, str, str | None, Literal['album', 'track']]:
    if end.isdigit():
        parse = ReParser(YANDEX_MUSIC_ALBUM+end)
        title, album, infotype = parse.get_album_name(), None, 'album'
    else:
        parse = ReParser(YANDEX_MUSIC_ALBUM+end)
        title, infotype = parse.get_track_name(), 'track'
        album = parse.get_album_name_with_track()


    return (title, parse.get_img(), parse.get_artist(),
            parse.get_genre(), parse.get_date(), album, infotype)


def main():
    parses: argparse.ArgumentParser = argparse.ArgumentParser(
        description = 'Find out information about a track or album by '
        'receiving requests from yandex music links', argument_default = None)
    parses.add_argument('-u', '--url', required = True,
                        action = 'store', type = str, 
                        metavar = '', help = 'Specify the link like this: -u link')
    args = parses.parse_args()
    print('\nYandex-Music-Link-Wrapper v.0.1 - by uewquewqueqwue(only regex)')
    print('----------------------------------------------------')
    pat = r"^https://music[.]yandex[.]ru/album/((?P<track>[\d]*/track/[\d]*)|(?P<ntrack>[\d]*[^/]))"
    match = re.search(pat, args.url)

    if match:
        print(f'\u21B3 YaMusic Wrapper - link received {args.url}')
        answer = match.groupdict()
        res_parse = parse(answer["ntrack"]) if answer.get("track") is None else parse(answer["track"])
        temp = 'Album' if res_parse[-1] == 'album' else 'Track'
        print(f'\u21B3 {temp} title - {res_parse[0]}')
        print(f'\u21B3 {temp} cover - {res_parse[1]}')
        None if res_parse[5] is None else print(f'\u21B3 Track from the album - {res_parse[5]}')
        print(f'\u21B3 Performer - {res_parse[2][0]}')
        print(f'  \u21B3 About the performer - {res_parse[2][3]}')
        print(f'  \u21B3 Link to the artist - {res_parse[2][1]}')
        print(f'  \u21B3 Link to the artist\'s avatar - {res_parse[2][2]}')
        print(f'\u21B3 Genres - {res_parse[3]}')
        print(f'\u21B3 Year of release - {res_parse[4]}')


    else: print('the link you specified does not match the format\n'
                +EXAMPLE_LINKS[0]+'\nor\n'+EXAMPLE_LINKS[1])

if __name__ == "__main__":
    main()