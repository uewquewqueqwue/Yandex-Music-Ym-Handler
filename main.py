import argparse

from rich.console import Console
from rich.panel import Panel

from re_parsing.parser import Static

# Consts

# EXAMPLE_LINKS = (
#     "https://music.yandex.com/album/123123",
#     "https://music.yandex.com/album/123123/track/123123",
# )
STATIC = "[ [bold red]Ym STATIC[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
INFO = "[ [bold red]Ym INFO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
DETAILS = "[ [bold red]Ym DETAILS[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
PICTURE = "[ [bold red]Ym PICTURE[/bold red] ]"
ERRNO = "[ [bold red]Ym ERRNO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
GRE = "[bold green]"
YEL = "[bold yellow]"
YELEND = "[/bold yellow]"
GREEND = "[/bold green]"
VERSION = "v1.12"
console = Console(highlight=False)

# Utilitarian functions


def decor_join(item: list) -> str:
    """decorative gluing"""

    return f"{GRE}{f'{GREEND}, {GRE}'.join(item)}{GREEND}"


def output_artist(nots: str, artists: list, det: bool, creat: bool) -> None:
    """transferred decor"""

    for i in artists:
        console.print(
            f"{STATIC} About {GRE}{i.name}{GREEND} - "
            f"{i.about if i.about else nots}",
        )
        console.print(
            f"{STATIC} Link to the artist - "
            f"{GRE}[link={i.url}]ctrl + click me[/link]"
        )
        temp_avatar = i.avatar
        temp_avatar = (
            f"{GRE}[link={temp_avatar}]ctrl + click me[/link]" if temp_avatar else nots
        )
        console.print(f"{STATIC} Link to the artist's avatar - {temp_avatar}")
        console.print(
            f"{STATIC} Listeners per month - {GRE}{i.listeners_month}{GREEND} "
            f"| Likes per month - {GRE}{i.likes_month}"
        )
        if det:
            print()
            console.print(
                f"[ [bold red]Ym STATIC {YEL}->{YELEND} Artist details branch"
                "[/bold red] ] [bold yellow]\u21AF[/bold yellow] Uploaded"
            )
            print()
            console.print(
                f"{DETAILS} Latest release - "
                f"{GRE}+{i.latest_release if i.latest_release else nots}"
            )
            console.print(
                f"{DETAILS} Popular tracks - "
                f"{decor_join(i.popular_tracks) if i.popular_tracks else nots}"
            )
            console.print(
                f"{DETAILS} Popular albums - "
                f"{decor_join(i.popular_albums) if i.popular_albums else nots}"
            )
            console.print(
                f"{DETAILS} Playlists - "
                f"{decor_join(i.playlists) if i.playlists else nots}"
            )
            console.print(
                f"{DETAILS} Videos - "
                f"{decor_join(i.video_names) if i.video_names else nots}"
            )
            console.print(
                f"{DETAILS} Similar artists - "
                f"{decor_join(i.similar_artists) if i.similar_artists else nots}"
            )
        if creat:
            pass


def output_console(url: str, det: bool, creat: bool, cover: bool) -> None:
    """main output

    Args:
        url (str): specified url
        det (bool): artist details
        creat (bool): artist creativity
        cover (bool): cover album, track, compilation
    """

    print()
    console.print(
        Panel.fit(
            f"{GRE}Ym Handler{GREEND} - "
            "by [bold red]uewquewqueqwue[/bold red]"
            f"(only regex \U0001F638 \U0001F63C) {GRE}< qdissh@gmail.com >{GREEND}",
            title="[bold yellow]Information[/bold yellow]",
            subtitle=f"[bold yellow]{VERSION}[/bold yellow]",
        )
    )
    stat = Static(url)
    artistsreq = stat.artists(det, creat)
    print()
    console.print(f"{INFO} Find out information about the artist")
    if artistsreq:
        for i in artistsreq:
            console.print(
                f"{INFO} The artist: {GRE}{i.name}{GREEND}, "
                "his description, avatar were received"
            )
            if det:
                console.print(
                    f"{INFO} The latest release, popular tracks, "
                    "popular albums, videos on the page, "
                    "similar artists have been received!"
                )
    else:
        console.print(f"{INFO} The artists were not uploaded, this is a compilation")
    print()

    nots = f"{GRE}Not specified"
    temp_artists = "Artists" if len(artistsreq) > 1 else "Artist"
    temp_coll = (
        decor_join(i.name for i in artistsreq)
        if artistsreq
        else f"{GRE}Lost of artists{GREEND}"
    )
    if cover:
        console.print(
            Panel.fit(
                stat.braille_art(stat.cover),
                title=PICTURE,
                subtitle="Built with \U0001F49C by ov3rwrite",
            )
        )
        print()
    if stat.type_url == "album":
        console.print(
            f"[ [bold red]Ym STATIC {YEL}->{YELEND} Album branch"
            "[/bold red] ] [bold yellow]\u21AF[/bold yellow] Uploaded"
        )
        print()
        console.print(f"{STATIC} Album title - {GRE}{stat.album.name}")
        console.print(
            f"{STATIC} Album cover - {GRE}[link={stat.cover}]ctrl + click me[/link]"
        )
        console.print(
            f"{STATIC} Number of songs in the album - {GRE}"
            f"{stat.album.number_songs}{GREEND} | the length of the entire "
            f"album - {GRE}{stat.album.length}{GREEND}"
        )
    else:
        console.print(
            f"[ [bold red]Ym STATIC {YEL}->{YELEND} Track branch"
            "[/bold red] ] [bold yellow]\u21AF[/bold yellow] Uploaded"
        )
        print()
        console.print(f"{STATIC} Track title - {GRE}{stat.track.name}")
        console.print(
            f"{STATIC} Track cover - {GRE}[link={stat.cover}]ctrl + click me[/link]"
        )
        console.print(f"{STATIC} Track length - {GRE}{stat.track.length}")
        console.print(f"{STATIC} Track from the album - {GRE}{stat.track.album_name}")
        console.print(
            f"{STATIC} Number of songs in the album - {GRE}"
            + str(stat.album.number_songs)
        )
        console.print(
            f"{STATIC} The length of the entire album - {GRE}" + str(stat.album.length)
        )
    console.print(f"{STATIC} {temp_artists} - {temp_coll}")
    console.print(f"{STATIC} Genres - {decor_join(stat.genre)}")
    console.print(
        f"{STATIC} Year of release - {GRE}{stat.date}{GREEND} | "
        f"Labels - {decor_join(stat.labels)}"
    )
    print()
    if artistsreq:
        console.print(
            f"[ [bold red]Ym STATIC {YEL}->{YELEND} Artist branch"
            "[/bold red] ] [bold yellow]\u21AF[/bold yellow] Uploaded"
        )
        print()
        output_artist(nots, artistsreq, det, creat)

    if det and not artistsreq and stat.type_url == "album":
        console.print(
            f"{ERRNO} Artist details are not available this is"
            " a compilation"
        )
    if creat and not artistsreq and stat.type_url == "album":
        console.print(
            f"{ERRNO} Artist creativity are not available this is"
            " a compilation"
        )


# Main


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
        "-c",
        "--cover",
        action="store_true",
        help="Cover track or album or compilation",
    )
    parses.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Additional information from artists",
    )
    parses.add_argument(
        "-cr",
        "--creativity",
        action="store_true",
        help="Show similar tracks to the specified one",
    )

    args = parses.parse_args()
    output_console(args.url, args.details, args.creativity, args.cover)


if __name__ == "__main__":
    main()
