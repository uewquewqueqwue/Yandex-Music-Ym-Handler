import argparse
import re
import sys
from datetime import timedelta
from typing import NamedTuple

from rich.console import Console
from rich.panel import Panel

from re_parsing.re_parser import (ADDITIONALLY, BASIC, GREEN, GREENEND, INFO,
                                  PICTURE, ReParser)

console = Console()

YANDEX_MUSIC_ALBUM: str = "https://music.yandex.ru/album/"
EXAMPLE_LINKS: tuple = (
    "https://music.yandex.ru/album/123123",
    "https://music.yandex.ru/album/123123/track/123123",
)
VERSION = 'v1.7'

class Track(NamedTuple):
    """returns the data container"""

    title: str
    img: str
    artist: tuple
    genre: str
    date: str
    labels: list
    tracks: int
    album_name: str | bool
    type_link: str
    tracktime: timedelta
    similar_tracks: list


def dataparse(url: str, cover: bool) -> Track:
    """return ready-made dataparse"""

    pat = (
        r"^https://music[.]yandex[.]ru/album/((?P<track>[\d]*/tr"
        r"ack/[\d]*)|(?P<ntrack>[\d]*[^/]))"
    )
    match = re.search(pat, url)

    if match:
        console.print(f"{INFO} Link received {match.group()}")
        answer = match.groupdict()

        end = answer["ntrack"] if not answer.get("track") else answer["track"]

        if end.isdigit():
            parses = ReParser(YANDEX_MUSIC_ALBUM + end)
            return Track(
                title=parses.get_album_name(),
                img=parses.get_img(cover),
                artist=parses.get_artist(),
                genre=parses.get_genre(),
                date=parses.get_date(),
                labels=parses.get_label(),
                tracks=parses.get_numbers_song(),
                album_name=False,
                type_link="album",
                tracktime=parses.get_tracktime(end),
                similar_tracks=False,
            )

        parses = ReParser(YANDEX_MUSIC_ALBUM + end)
        return Track(
            title=parses.get_track_name(),
            img=parses.get_img(cover),
            artist=parses.get_artist(),
            genre=parses.get_genre(),
            date=parses.get_date(),
            labels=parses.get_label(),
            tracks=parses.get_numbers_song(),
            album_name=parses.get_album_name_with_track(),
            type_link="track",
            tracktime=parses.get_tracktime(end),
            similar_tracks=parses.get_similar_tracks(),
        )

    console.print(
        "[bold red]ALERT![/bold red] the link you specified does not match the format\n"
        + EXAMPLE_LINKS[0]
        + "\nor\n"
        + EXAMPLE_LINKS[1]
    )
    return sys.exit()


def output_console(url: str, simt: bool, cover: bool):
    """return a beautiful output in the console"""

    console.print(
        Panel.fit(
            f"{GREEN}Yandex-Music-Link-Wrapper {VERSION}{GREENEND} - "
            "by [bold red]uewquewqueqwue[/bold red]"
            "(only regex) [bold yellow]< qdissh@gmail.com >[/bold yellow]",
            title="Information",
        )
    )

    res_parse = dataparse(url, cover)

    temp = "Album" if res_parse.type_link == "album" else "Track"
    temp_artist = "Artists" if len(res_parse.artist.names) > 1 else "Artist"
    if cover:
        console.print(Panel.fit(res_parse.img[1], title=PICTURE))
    console.print(f"{BASIC} {temp} title - {GREEN}{res_parse.title}")
    console.print(
        f"{BASIC} {temp} cover - "
        f"{GREEN}[link={res_parse.img[0]}]ctrl + click me[/link]"
    )

    if res_parse.album_name:
        console.print(
            f"{BASIC} Track length - {GREEN}" f"{res_parse.tracktime}{GREENEND}"
        )
        console.print(
            f"{BASIC} Album - {GREEN}{res_parse.album_name}{GREENEND} "
            f"| {GREEN}{res_parse.tracks}{GREENEND} (number of songs in"
            f"the album)"
        )
    else:
        console.print(
            f"{BASIC} Number of songs in the album - {GREEN}{res_parse.tracks}{GREENEND}"
            f" | the length of the entire album"
            f" - {GREEN}{res_parse.tracktime}{GREENEND}"
        )
    console.print(
        f"{BASIC} {temp_artist} - "
        f"{GREEN}{', '.join(res_parse.artist.names)}{GREENEND}"
    )
    console.print(f"{BASIC} Genres - {GREEN}{res_parse.genre}")
    console.print(
        f"{BASIC} Year of release - {GREEN}{res_parse.date}{GREENEND} | "
        f"Labels - {GREEN}{', '.join(res_parse.labels)}\n"
    )
    if res_parse.artist.avatar_about:
        for i, k in enumerate(res_parse.artist.avatar_about):
            console.print(
                f"{ADDITIONALLY} About {GREEN}{k}{GREENEND} - "
                f"{res_parse.artist.avatar_about[k][1]}"
            )
            console.print(
                f"{ADDITIONALLY} Link to the artist - "
                f"{GREEN}[link={res_parse.artist.links[i]}]ctrl + click me[/link]"
            )
            temp_avatar = res_parse.artist.avatar_about[k][0]
            temp_avatar = temp_avatar if temp_avatar else "There is no avatar"
            console.print(
                f"{ADDITIONALLY} Link to the artist's avatar - "
                f"{GREEN}[link={temp_avatar}]ctrl + click me[/link]\n"
            )
    if simt and res_parse.similar_tracks:
        console.print(f"{ADDITIONALLY} Similar tracks to the specified")
        console.print(f"{ADDITIONALLY} {', '.join(res_parse.similar_tracks)}")


def main() -> None:
    """return main"""

    parses: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Find out information about a track or album by "
        "receiving requests from yandex music links",
        argument_default=None,
    )
    parses.add_argument(
        "-u",
        "--url",
        required=True,
        action="store",
        type=str,
        metavar="",
        help="Specify the link like this: -u link",
    )
    parses.add_argument(
        "-st",
        "--similar_tracks",
        action="store_true",
        help="Show similar tracks to the specified one",
    )
    parses.add_argument(
        "-c",
        "--cover",
        action="store_true",
        help="Cover track or album or collection",
    )

    args = parses.parse_args()
    output_console(args.url, args.similar_tracks, args.cover)


if __name__ == "__main__":
    main()
