import argparse
import re
from typing import NamedTuple

from re_parsing.re_parser import ReParser

YANDEX_MUSIC_ALBUM: str = "https://music.yandex.ru/album/"
EXAMPLE_LINKS: tuple = (
    "https://music.yandex.ru/album/123123",
    "https://music.yandex.ru/album/123123/track/123123",
)


class Track(NamedTuple):
    """returns the data container"""

    title: str
    img: str
    artist: tuple
    genre: str
    date: str
    label: str
    tracks: int
    album: str | None
    infotype: str
    tracktime: str


def dataparse(end: str) -> Track:
    """returns ready-made dataparse"""

    if end.isdigit():
        parses = ReParser(YANDEX_MUSIC_ALBUM + end)
        title, album, infotype = parses.get_album_name(), None, "album"
        tracktime = None
    else:
        parses = ReParser(YANDEX_MUSIC_ALBUM + end)
        title, infotype = parses.get_track_name(), "track"
        album = parses.get_album_name_with_track()
        tracktime = parses.get_tracktime(end)

    return Track(
        title=title,
        img=parses.get_img(),
        artist=parses.get_artist(),
        genre=parses.get_genre(),
        date=parses.get_date(),
        label=parses.get_label(),
        tracks=parses.get_numbers_song(),
        album=album,
        infotype=infotype,
        tracktime=tracktime,
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
    args = parses.parse_args()

    print("\nYandex-Music-Link-Wrapper v1.1 - by uewquewqueqwue(only regex)[qdissh@gmail.com]")
    print("----------------------------------------------------")

    pat = (
        r"^https://music[.]yandex[.]ru/album/((?P<track>[\d]*/tr"
        r"ack/[\d]*)|(?P<ntrack>[\d]*[^/]))"
    )
    match = re.search(pat, args.url)

    if match:
        print(f"\u21B3 YaMusic-Link-Wrapper - link received {match.group()}")
        answer = match.groupdict()
        res_parse = (
            dataparse(answer["ntrack"])
            if answer.get("track") is None
            else dataparse(answer["track"])
        )
        temp = "Album" if res_parse.infotype == "album" else "Track"  # decoration
        temp_artist = (
            "Artists" if isinstance(res_parse.artist.names, list) else "Artist"
        )  # decoration
        temp_names = (
            ",".join(res_parse.artist.names)
            if isinstance(res_parse.artist.names, list)
            else res_parse.artist.names
        )
        print(f"\u21B3 {temp} title - {res_parse.title}")
        print(f"\u21B3 {temp} cover - {res_parse.img}")
        if res_parse.album is not None:
            print(
                f"\u21B3 Track from the album - {res_parse.album} "
                f"{res_parse.tracks}(number of songs in the album) | "
                f"Track length - {res_parse.tracktime}"
            )
        else:
            print(f"  \u21B3 Number of songs in the album - {res_parse.tracks}")
        print(f"\u21B3 {temp_artist} - {temp_names}")
        if res_parse.artist.avatar_about is not None:
            for i, k in enumerate(res_parse.artist.avatar_about):
                print(f"  \u21B3 About {k} - {res_parse.artist.avatar_about[k][1]}")
                print(
                    "  \u21B3 Link to the artist - "
                    f"{ReParser.YANDEX_MUSIC_ARTIST+res_parse.artist.links[i][0]}/info"
                )
                print(
                    f"  \u21B3 Link to the artist's avatar - {res_parse.artist.avatar_about[k][0]}"
                )
        print(f"\u21B3 Genres - {res_parse.genre}")
        print(f"\u21B3 Year of release - {res_parse.date} | Labels - {res_parse.label}")
        return

    print(
        "the link you specified does not match the format\n"
        + EXAMPLE_LINKS[0]
        + "\nor\n"
        + EXAMPLE_LINKS[1]
    )


if __name__ == "__main__":
    main()
