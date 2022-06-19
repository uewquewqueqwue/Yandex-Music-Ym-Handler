import os
import re
from datetime import timedelta
from typing import NamedTuple

from rich.console import Console

from re_parsing.simple_request import Request
from re_parsing.console_picture import generate_art

# TODO

# FIXME
# -st with an album or collection

console = Console()

# DECORATION CONSOLE CONSTS
BASIC = "[ [bold red]Ym BASIC[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
INFO = "[ [bold red]Ym INFO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
ADDITIONALLY = (
    "[ [bold red]Ym ADDITIONALLY[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
)
PICTURE = "[ [bold red]Ym PICTURE[/bold red] ]"
GREEN = "[bold green]"
GREENEND = "[/bold green]"


def _convert_to_timedelta(lst: list) -> timedelta:
    """converts input data to timedelta format"""

    seconds: int = 0
    for i in lst:
        numb_a, numb_b = list(map(int, i.split(":")))
        numb_a *= 60
        seconds += numb_a + numb_b

    return timedelta(seconds=seconds)


def _default_links(lst: list) -> list:
    """return a list of links"""

    return_list: list = []
    for i in lst:
        return_list.extend([ReParser.YANDEX_MUSIC_ARTIST + i[0]])

    return return_list


def _full_size_image(sym_image: str) -> str:
    """we get a link to the full size of the image"""

    return (
        ReParser.YANDEX_IMAGES
        + sym_image.split(";")[-3][:-4]
        + "/"
        + sym_image.split(";")[-2][:-4]
        + "/m1000x1000"
    )


def _check_len(lst: list) -> list | bool:
    """checking the length of the list"""

    if len(lst) != 0:
        return lst
    return False


def _fix_symbol(item: list | tuple | str) -> list:
    """corrects the ' character in strings"""

    symbol_case = {
        "&#39;": "\u0027",
        "&#8212;": "\u2014",
        "&#38;": "\u0026",
        "&#47;": "\u002F",
        "&#34;": "\u0022",
    }
    done_str: item = item
    if isinstance(item, str):
        for i, j in symbol_case.items():
            done_str: str = item.replace(i, j)
        return [done_str]

    for i, j in symbol_case.items():
        done_str: list = list(map(lambda a: a.replace(i, j), done_str))
    return done_str


class Artist(NamedTuple):
    """returns the data container"""

    links: list
    names: list
    avatar_about: dict


class ReParser:
    """returns does a search on the available pages"""

    YANDEX_IMAGES: str = "https://avatars.yandex.net/get-music-content/"
    YANDEX_MUSIC_ARTIST: str = "https://music.yandex.ru/artist/"

    def __init__(self, url: str):
        self.url: str = url
        self.parse: str = Request(self.url).parse_url()

    def get_img(self, cover: bool) -> str:
        """getting a list of link elements"""

        console.print(f"{INFO} The request is {GREEN}successful!{GREENEND} Expect")
        print()

        pat: list = (
            r"<img(?:\s+[^>]*)class=\"entity-cover__image\s"
            r"deco-pane\"(?:\s+[^>]*)src=([\"\'])(.+?)\1"
        )

        temp: str = re.findall(pat, self.parse, re.M,)[
            0
        ][1]

        temp_url: str = _full_size_image(temp)
        if cover:
            Request(temp_url).time_parse()
            bytes_image = generate_art("image.jpg")
            os.remove("image.jpg")
            return temp_url, bytes_image

        return temp_url

    def get_track_name(self) -> str:
        """we get the name of the song"""

        check_correct: list = re.findall(r"<title>(\w+)", self.parse)
        if check_correct[0].lower() != "яндекс":

            temp: str = re.findall(
                r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\">(.+?[^<]*)",
                self.parse,
                re.M,
            )[-1]

            return _fix_symbol(temp)[0]

        return self.get_album_name()

    def get_artist(self) -> Artist:
        """we get (the artist, a link to him,
        a link to his avatar, his description)

        not all artists on the service have
        official avatars, some have requests from
        their search engine so I had to add a check"""

        console.print(f"{INFO} Find out information about the artist")

        temp_artist_link_block: str = re.findall(
            r"<span\sclass=\"d-artists(.+?)</a></span>",
            self.parse,
            re.M,
        )[0]

        temp_artist_link_artists: list = re.findall(
            r"href=\"/artist/(\d+)\"\s+[^>]*>(.+?[^<]*)",
            temp_artist_link_block,
            re.M,
        )
        temp_artist_link_artists = list(map(_fix_symbol, temp_artist_link_artists))

        temp_artist_links: dict = {}
        if len(temp_artist_link_artists) > 1:
            for i in temp_artist_link_artists:
                get_artist_request = GetArtist(i[0])
                temp_artist_links[i[1]] = [
                    get_artist_request.artist_avatar(),
                    _fix_symbol(get_artist_request.artist_about())[0],
                ]
                console.print(
                    f"{INFO} The artist: {GREEN}{i[1]}{GREENEND}, "
                    "his description, avatar were received"
                )
            print()
            return Artist(
                names=list(temp_artist_links.keys()),
                links=_default_links(temp_artist_link_artists),
                avatar_about=temp_artist_links,
            )
        if self.check_collection():
            console.print(
                f"{INFO} This is a {GREEN}collection{GREENEND}, "
                "it contains a lot of artists\n(in the future, it is possible"
                "for an additional the argument can get information about "
                "all artists)\n"
            )

            return Artist(
                names=["A lot of artists, because this is a collection"],
                links=False,
                avatar_about=False,
            )

        get_artist_request = GetArtist(temp_artist_link_artists[0][0])
        temp_artist_links[temp_artist_link_artists[0][1]] = [
            get_artist_request.artist_avatar(),
            _fix_symbol(get_artist_request.artist_about())[0],
        ]
        console.print(
            f"{INFO} The artist: {GREEN}{temp_artist_link_artists[0][1]}"
            f"{GREENEND}, his description, avatar were received\n"
        )

        return Artist(
            names=[temp_artist_link_artists[0][1]],
            links=_default_links(temp_artist_link_artists),
            avatar_about=temp_artist_links,
        )

    def get_album_name(self) -> str:
        """getting the name from the page from the album page"""

        temp: str = re.findall(
            r"<span(?:\s+[^>]*)class=\"deco-typo\">(.+?[^<]*)",
            self.parse,
            re.M,
        )[0]

        return _fix_symbol(temp)[0]

    def get_album_name_with_track(self) -> str:
        """getting the name from the track page

        the track may be incorrectly specified, but the album itself is correct,
        in this case, it will just find the album name"""

        temp: list = re.findall(
            (
                r"<a(?:\s+[^>]*)href=\"/album/([\w]*)\"\s"
                r"class=\"d-link\sdeco-link\">(.+?[^<]*)"
            ),
            self.parse,
            re.M,
        )

        if _check_len(temp):
            # if len(temp) != 0:
            # if len(temp[0]) > 1:
            #     return temp[0][1]
            return _fix_symbol(temp[0][1])[0]
            # return self.get_album_name()

        print(
            "  \u21B3 Your link is correct, but it contains a non-existent "
            "track, information about the album will be displayed"
        )

        return self.get_album_name()

    def get_tracktime(self, track) -> str:
        """return track time"""

        temp: list = re.findall(
            (
                rf"class=\"d-track__name\".+?[^<]*<a\shref=\"/album/{track}\""
                r".+?typo-track deco-typo-secondary\">(\w+[^<]*)"
            ),
            self.parse,
            re.M,
        )

        if _check_len(temp):
            return _convert_to_timedelta([temp[0]])

        return self.length_all_tracks()

    def get_genre(self) -> str:
        """we get the genre of the track (album)"""

        return re.findall(
            (
                r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\s"
                r"deco-link_mimic\stypo\">(.+?[^<]*)"
            ),
            self.parse,
            re.M,
        )[0]

    def get_date(self) -> str:
        """we get the date of the track (album)"""

        return re.findall(
            r"<span\s+class=\"typo deco-typo-secondary\">(.+?[^<]*)",
            self.parse,
            re.M,
        )[0]

    def get_label(self) -> list:
        """return label"""

        temp: list = re.findall(
            r"<a\shref=\"/label/\d+\"\sclass=\"d-link\sdeco-link\">(.+?[^<]*)",
            self.parse,
            re.M,
        )

        return _fix_symbol(temp)

    def get_numbers_song(self) -> int:
        """return number of songs in the album"""

        return len(
            re.findall(
                r"<div\sclass=\"d-track\stypo-track\sd-track_selectable",
                self.parse,
                re.M,
            )
        )

    def get_similar_tracks(self) -> list:
        """returns a list of similar songs by track"""

        temp: str = re.findall(
            r"sidebar__section-title\stypo-caps\sdeco-typo-seco"
            r"ndary.+?class=\"footer\"",
            self.parse,
            re.M,
        )[0]

        list_tracks: list = list(
            map(
                lambda x: x.strip(),
                re.findall(
                    r"d-track__title\sdeco-link\sdeco-link_stronger\">(.+?[^<]*)",
                    temp,
                    re.M,
                ),
            )
        )

        return list_tracks

    def check_collection(self) -> bool:
        """checks whether this album is a compilation"""

        temp: list = re.findall(
            r"<span\sclass=\"deco-typo-secondary\s+\">(.+?)</",
            self.parse,
            re.M,
        )

        if not temp or temp[0] != "сборник":
            return False
        return True

    def length_all_tracks(self) -> list:
        """return the length of the entire album(timedelta)"""

        temp: list = re.findall(
            r"<div\sclass=\"d-track\stypo-track\sd-track_selecta"
            r"ble.+?typo-track deco-typo-secondary\">(\w+[^<]*)",
            self.parse,
            re.M,
        )

        return _convert_to_timedelta(temp)


class GetArtist(ReParser):
    """all info of artist"""

    def __init__(self, artist_code: str) -> str:
        super().__init__(self.YANDEX_MUSIC_ARTIST + artist_code + "/info")

    def artist_name(self) -> str:
        """return artist name"""

        return re.findall(
            r"<a(?:\s+[^>]*)class=\"d-link deco-link\"\stitle=\"(.+?[^\"]*)",
            self.parse,
            re.M,
        )

    def artist_avatar(self) -> str | bool:
        """return artist avatar"""

        if re.findall(r"artist-pics__pic\sartist-pics__pic_empty", self.parse):
            return False

        temp_artist_avatar: str = re.search(
            r"<img\ssrc=\"[^/blocks](.+?[^\"]*)",
            self.parse,
            re.M,
        ).groups()[0]

        if re.search(r"\bw=\b", temp_artist_avatar):
            temp_artist_avatar_end: str = "&"
            for i in temp_artist_avatar.split(";"):
                temp_artist_avatar_end += i
            return "https:" + temp_artist_avatar_end.replace("&#47", "\u002F").replace(
                "&#38", "\u0026"
            )

        return _full_size_image(temp_artist_avatar)

    def artist_about(self) -> str:
        """return artist about"""

        temp_artist_about: list[str] = re.findall(
            r"<div\sclass=\"page-artist__description\stypo\">(.+?[^<]*)",
            self.parse,
            re.M,
        )

        if len(temp_artist_about) < 1:
            return "There is no description"

        return temp_artist_about[0]
