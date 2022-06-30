import argparse

from rich.console import Console
from rich.panel import Panel

from parsing.parser import Static

# Consts

# EXAMPLE_LINKS = (
#     "https://music.yandex.com/album/123123",
#     "https://music.yandex.com/album/123123/track/123123",
# )
STATIC = "[ [bold red]Ym STATIC[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
INFO = "[ [bold red]Ym INFO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
DETAILS = "[ [bold red]Ym DETAILS[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
CREAT = "[ [bold red]Ym CREATIVITY[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
PICTURE = "[ [bold red]Ym PICTURE[/bold red] ]"
ERRNO = "[ [bold red]Ym ERRNO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
GRE = "[bold green]"
YEL = "[bold yellow]"
YELEND = "[/bold yellow]"
GREEND = "[/bold green]"
VERSION = "v1.13.1"
console = Console(highlight=False)


# Utilitarian functions


def decor_join(item: list) -> str:
    """decorative gluing"""

    return f"{GRE}{f'{GREEND}, {GRE}'.join(item)}{GREEND}"


def output_artist(
    nots: str, artists: list, det: bool, creat: bool, stat: Static
) -> None:
    """transferred decor"""

    if det:
        a_det = stat.artists_details

    if creat:
        a_creat = stat.artists_creativity

    for numb, i in enumerate(artists):
        print()
        console.print(
            f"[ [bold red]Ym STATIC {YEL}->{YELEND} Artist branch"
            "[/bold red] ] [bold yellow]\u21AF[/bold yellow] Uploaded"
        )
        print()
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
                + (GRE + a_det[numb].latest_release if a_det[numb].latest_release else nots)
            )
            console.print(
                f"{DETAILS} Popular tracks - "
                + (decor_join(a_det[numb].popular_tracks) if a_det[numb].popular_tracks else nots)
            )
            console.print(
                f"{DETAILS} Popular albums - "
                + (decor_join(a_det[numb].popular_albums) if a_det[numb].popular_albums else nots)
            )
            console.print(
                f"{DETAILS} Playlists - "
                + (decor_join(a_det[numb].playlists) if a_det[numb].playlists else nots)
            )
            console.print(
                f"{DETAILS} Videos - "
                + (decor_join(a_det[numb].videos) if a_det[numb].videos else nots)
            )
            console.print(
                f"{DETAILS} Similar artists - "
                + (decor_join(a_det[numb].similar) if a_det[numb].similar else nots)
            )
        if creat:
            print()
            console.print(
                f"[ [bold red]Ym STATIC {YEL}->{YELEND} Artist creativity branch"
                "[/bold red] ] [bold yellow]\u21AF[/bold yellow] Uploaded"
            )
            print()
            console.print(f"{CREAT} List of all albums - {decor_join(a_creat[numb].albums)}")
            console.print(f"{CREAT} List of all tracks - {decor_join(a_creat[numb].tracks)}")
            console.print(
                f"{CREAT} List of all compilations - "
                + (decor_join(a_creat[numb].compilations) if a_creat[numb].compilations else nots)
            )
            console.print(
                f"{CREAT} List of all videos - "
                + (decor_join(a_creat[numb].videos) if a_creat[numb].videos else nots)
            )
            console.print(
                f"{CREAT} List of all similar artists - "
                + (decor_join(a_creat[numb].similar) if a_creat[numb].similar else nots)
            )


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
    artists_base = stat.artists
    print()
    console.print(f"{INFO} Find out information about the artist")
    if artists_base:
        for i in artists_base:
            console.print(
                f"{INFO} The artist: {GRE}{i.name}{GREEND}, "
                f"his {decor_join(['description', 'avatar'])} were received!"
            )
            if det:
                console.print(
                    INFO
                    + " "
                    + decor_join(
                        ["Latest release", "popular tracks", "popular albums", "videos"]
                    )
                    + " on the page,"
                    f"{GRE}similar artists{GREEND} have been received!"
                )
            if creat:
                console.print(
                    f"{INFO} All {decor_join(['tracks', 'albums', 'compilations'])}"
                    " have been received!"
                )
    else:
        console.print(f"{INFO} The artists were not uploaded, this is a compilation")
    print()

    nots = f"{GRE}Not specified"
    temp_artists = "Artists" if len(artists_base) > 1 else "Artist"
    temp_coll = (
        decor_join(i.name for i in artists_base)
        if artists_base
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
            f"{STATIC} Number of tracks in the album - {GRE}"
            f"{stat.album.number_tracks}{GREEND} | the length of the entire "
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
            f"{STATIC} Number of tracks in the album - {GRE}"
            + str(stat.album.number_tracks)
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
    if artists_base:
        output_artist(nots, artists_base, det, creat, stat)

    if det and not artists_base and stat.type_url == "album":
        console.print(
            f"{ERRNO} Artist details are not available this is" " a compilation"
        )
    if creat and not artists_base and stat.type_url == "album":
        console.print(
            f"{ERRNO} Artist creativity are not available this is" " a compilation"
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
