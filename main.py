import argparse
import re
import sys
from datetime import timedelta
from typing import NamedTuple

from rich.console import Console
from rich.panel import Panel
# from re_parsing.parser import Static

from re_parsing.re_parser import (
    ADDITIONALLY,
    BASIC,
    ERRNO,
    GREEN,
    GREENEND,
    INFO,
    PICTURE,
    ReParser,
)

console = Console(highlight=False)

YANDEX_MUSIC_ALBUM: str = "https://music.yandex.ru/album/"
EXAMPLE_LINKS: tuple = (
    "https://music.yandex.ru/album/123123",
    "https://music.yandex.ru/album/123123/track/123123",
)
VERSION = "v1.7"


class Track(NamedTuple):
    """returns the data container"""

    title: str
    img: str
    artists: list
    genre: str
    date: str
    labels: list
    tracks: int
    album_name: str | bool
    type_link: str
    length_tracks: timedelta
    similar_tracks: list


def dataparse(url: str, cover: bool, additional: bool) -> Track:
    """return ready-made dataparse"""

    pat = (
        r"^https://music[.]yandex[.](?:com|ru)/album/((?P<track>[\d]*/tr"
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
                artists=parses.get_artists(additional),
                genre=parses.get_genre(),
                date=parses.get_date(),
                labels=parses.get_label(),
                tracks=parses.get_numbers_song(),
                album_name=False,
                type_link=parses.get_type_link(),
                length_tracks=parses.get_length_tracks(end),
                similar_tracks=False,
            )

        parses = ReParser(YANDEX_MUSIC_ALBUM + end)
        return Track(
            title=parses.get_track_name(),
            img=parses.get_img(cover),
            artists=parses.get_artists(additional),
            genre=parses.get_genre(),
            date=parses.get_date(),
            labels=parses.get_label(),
            tracks=parses.get_numbers_song(),
            album_name=parses.get_album_name_with_track(),
            type_link=parses.get_type_link(),
            length_tracks=parses.get_length_tracks(end),
            similar_tracks=parses.get_similar_tracks(),
        )

    console.print(
        f"{ERRNO} the link you specified does not match the format\n"
        + EXAMPLE_LINKS[0]
        + "\nor\n"
        + EXAMPLE_LINKS[1]
    )
    return sys.exit()


def decor_join(item) -> str:
    """_"""  # TODO

    return f"{GREEN}{f'{GREENEND}, {GREEN}'.join(item)}{GREENEND}"


def output_console(url: str, simt: bool, cover: bool, additional: bool):
    """return a beautiful output in the console"""

    print()
    console.print(
        Panel.fit(
            f"{GREEN}Yandex-Music-Link-Wrapper{GREENEND} - "
            "by [bold red]uewquewqueqwue[/bold red]"
            f"(only regex) {GREEN}< qdissh@gmail.com >{GREENEND}",
            title="[bold yellow]Information[/bold yellow]",
            subtitle=f"[bold yellow]{VERSION}[/bold yellow]",
        )
    )

    res_parse = dataparse(url, cover, additional)

    temp = "Album" if res_parse.type_link == "album" else "Track"
    temp_artist = "Artists" if len(res_parse.artists) > 1 else "Artist"
    temp_coll = (
        decor_join(i.artist_name for i in res_parse.artists)
        if res_parse.artists
        else f"{GREEN}Lost of artists{GREENEND}"
    )
    if cover:
        console.print(
            Panel.fit(
                res_parse.img[1],
                title=PICTURE,
                subtitle="Built with \U0001F49C by ov3rwrite",
            )
        )
        print()

    console.print(f"{BASIC} {temp} title - {GREEN}{res_parse.title}")
    console.print(
        f"{BASIC} {temp} cover - "
        f"{GREEN}[link={res_parse.img[0]}]ctrl + click me[/link]"
    )
    if res_parse.type_link == "track":
        console.print(
            f"{BASIC} Track length - {GREEN}" f"{res_parse.length_tracks}{GREENEND}"
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
            f" - {GREEN}{res_parse.length_tracks}{GREENEND}"
        )
    console.print(f"{BASIC} {temp_artist} - {temp_coll}")
    console.print(f"{BASIC} Genres - {decor_join(res_parse.genre)}")
    console.print(
        f"{BASIC} Year of release - {GREEN}{res_parse.date}{GREENEND} | "
        f"Labels - {decor_join(res_parse.labels)}\n"
    )
    # res_parse.artists[0].video_link
    for i in res_parse.artists:
        console.print(
            f"{ADDITIONALLY} About {GREEN}{i.artist_name}{GREENEND} - "
            f"{i.artist_about if i.artist_about else 'There is no description'}"
        )
        console.print(
            f"{ADDITIONALLY} Link to the artist - "
            f"{GREEN}[link={i.artist_link}]ctrl + click me[/link]"
        )
        temp_avatar = i.artist_avatar
        temp_avatar = (
            f"[link={temp_avatar}]ctrl + click me[/link]"
            if temp_avatar
            else "There is no avatar"
        )
        console.print(
            f"{ADDITIONALLY} Link to the artist's avatar - " f"{GREEN}{temp_avatar}\n"
        )
        if additional:
            console.print(
                f"{ADDITIONALLY} Popular tracks - {decor_join(i.popular_tracks)}"
            )
            console.print(
                f"{ADDITIONALLY} Popular albums - {decor_join(i.popular_album)}"
            )
            console.print(
                f"{ADDITIONALLY} Latest release - {GREEN}{i.latest_release}{GREENEND}"
            )
            temp_playlist = "Playlists" if len(i.playlists) > 1 else "Playlist"
            console.print(f"{ADDITIONALLY} {temp_playlist} - {decor_join(i.playlists)}")
            print()

    if additional and res_parse.type_link == "album":
        console.print(
            f"{ERRNO} Additional are not available, is it an album or a collection"
        )

    if simt and res_parse.type_link == "album":
        console.print(
            f"{ERRNO} Similar tracks are not available, "
            "is it an album or a collection. Specify a track "
            "from there, we will use it to find similar tracks."
        )

    if simt and res_parse.type_link != "album":
        console.print(
            f"{ADDITIONALLY} Similar tracks to the specified - "
            f"{decor_join(res_parse.similar_tracks)}"
        )


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
    parses.add_argument(
        "-adtl",
        "--additional",
        action="store_true",
        help="Additional information from artists",
    )

    args = parses.parse_args()
    output_console(args.url, args.similar_tracks, args.cover, args.additional)
    # stat = Static(args.url)
    # artistreq = stat.artists(True)

    # artist = []
    # for i in artistreq:
    #     # artist.append(i.name)
    #     # artist.append(i.avatar)
    #     # artist.append(i.about)
    #     # artist.append()
    #     # artist.append(i.latest_release)
    #     # artist.append(i.playlists)
    #     # artist.append(i.popular_albums)
    #     # artist.append(i.popular_tracks)
    #     # artist.append(i.similar_artists)
    #     artist.append(i.listeners_month)
    #     artist.append(i.likes_month)
    # print(
    #     stat.type_url, 'type\n',
    #     stat.genre, 'genre\n',
    #     stat.date, 'date\n',
    #     stat.labels, 'labels\n',
    #     stat.cover, 'cover\n',
    #     # stat.album.name,
    #     # stat.album.number_songs,
    #     # stat.album.length,
    #     stat.track.name, 'track name\n',
    #     stat.track.length, 'track length\n',
    #     stat.track.similar_tracks, 'track sim\n',
    #     *artist
    #     # s.name,
    #     # s.avatar,
    #     # s.about
    #     # stat.artists[0].name,
    #     # stat.artists[0].avatar,
    #     # stat.artists[0].about
    # )


if __name__ == "__main__":
    main()
