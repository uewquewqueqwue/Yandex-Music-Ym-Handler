import os
import re
from datetime import timedelta

from rich.console import Console

from braillert.generator import generate_art
from braillert.colors import RICH_COLORS, RICH_RESETTER
from re_parsing.request import Request

# TODO
# check latest release - yes
# decoration join - yes

# FIXME
# -st with an album or collection - yes
# -adtl with an album or collection - yes

# return list(genre)
# fix type_link

# MAYBE
# time to artist
# text songs in .txt
# lost of artists in collection

console = Console()

# DECORATION CONSOLE CONSTS
BASIC = "[ [bold red]Ym BASIC[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
INFO = "[ [bold red]Ym INFO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
ADDITIONALLY = (
    "[ [bold red]Ym ADDITIONALLY[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
)
PICTURE = "[ [bold red]Ym PICTURE[/bold red] ]"
ERRNO = "[ [bold red]Ym ERRNO[/bold red] ] [bold yellow]\u21AF[/bold yellow]"
GREEN = "[bold green]"
GREENEND = "[/bold green]"

YANDEX_IMAGES = "https://avatars.yandex.net/get-music-content/"
YANDEX_MUSIC_ARTIST = "https://music.yandex.ru/artist/"


def _convert_to_timedelta(lst: list) -> timedelta:
    """converts input data to timedelta format"""

    seconds = 0
    for i in lst:
        numb_a, numb_b = list(map(int, i.split(":")))
        numb_a *= 60
        seconds += numb_a + numb_b

    return timedelta(seconds=seconds)


def _default_links(lst: list) -> list:
    """return a list of links"""

    return_list = []
    for i in lst:
        return_list.extend([YANDEX_MUSIC_ARTIST + i[0]])

    return return_list


def _full_size_image(sym_image: str) -> str:
    """we get a link to the full size of the image"""

    return (
        YANDEX_IMAGES
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


def _fix_symbol(item: str | tuple | list):
    """corrects the ' character in strings"""

    symbol_case = {
        "&#39;": "\u0027",
        "&#8212;": "\u2014",
        "&#38;": "\u0026",
        "&#47;": "\u002F",
        "&#34;": "\u0022",
    }
    done_str = item
    if isinstance(item, str):
        for i, j in symbol_case.items():
            done_str: str = item.strip().replace(i, j)

        return [done_str]

    for i, j in symbol_case.items():
        done_str: list = list(map(lambda a: a.strip().replace(i, j), done_str))

    return done_str


class Artist:
    """all info of artist"""

    def __init__(self, artist_code: str):
        self.artist_link = YANDEX_MUSIC_ARTIST + artist_code + "/info"
        self.__parse = Request(self.artist_link).parse_url()
        self._artist_name = None
        self._artist_avatar = None
        self._artist_about = None

    # def __getattr__(self, item): # TODO
    #     if item in ArtistAdd.__dict__:
    #         raise AttributeError("These attributes are not in Artist, use ArtistAdd")

    @property
    def artist_name(self) -> str:
        """return artist name"""

        if not self._artist_name:
            self._artist_name = re.search(
                r"<h1.+?>(\w+)<",
                self.__parse,
                re.M,
            ).groups()[0]

        return self._artist_name

    @property
    def artist_avatar(self) -> str:
        """return artist avatar"""

        if not self._artist_avatar:
            if re.findall(r"artist-pics__pic\sartist-pics__pic_empty", self.__parse):
                return self._artist_avatar

            temp_artist_avatar = re.search(
                r"<img\ssrc=\"(.+?[^\"]*)",
                self.__parse,
                re.M,
            ).group()

            if re.search(r"\bw=\b", temp_artist_avatar):
                temp_artist_avatar_end = "".join(temp_artist_avatar.split(";"))
                self._artist_avatar = "https:" + temp_artist_avatar_end.replace(
                    "&#47", "\u002F"
                ).replace("&#38", "\u0026")

            self._artist_avatar = _full_size_image(temp_artist_avatar)

        return self._artist_avatar

    @property
    def artist_about(self) -> str:
        """return artist about"""

        if not self._artist_about:
            temp_artist_about: list[str] = re.findall(
                r"<div\sclass=\"page-artist__description\stypo\">(.+?[^<]*)",
                self.__parse,
                re.M,
            )

            if len(temp_artist_about) < 1:
                return self._artist_about

            self._artist_about = _fix_symbol(temp_artist_about)[0]

        return self._artist_about


class ReParser:
    """returns does a search on the available pages"""

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

        bytes_image = False

        temp_url: str = _full_size_image(temp)
        if cover:
            Request(temp_url).parse_img()
            bytes_image = generate_art("image.jpg", RICH_COLORS, RICH_RESETTER)
            os.remove("image.jpg")
            return temp_url, bytes_image

        return temp_url, bytes_image

    def get_track_name(self) -> str:
        """we get the name of the song"""

        check_correct: list = re.search(r"<title>(\w+)", self.parse).groups()


        if check_correct[0].lower() != "яндекс":
            temp: str = re.search(
                r"sidebar__section.+?d-link\sdeco-link\">(.+?)<",
                self.parse,
                re.M,
            ).groups()

            return _fix_symbol(temp)[0]

        return self.get_album_name()

    def get_artists(self, additional: bool) -> Artist:
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

        if self.check_collection():
            console.print(
                f"{INFO} This is a {GREEN}collection{GREENEND}, "
                "it contains a lot of artists\n(in the future, it is possible"
                "for an additional the argument can get information about "
                "all artists)\n"
            )
            return []

        artists_base = []

        for i in temp_artist_link_artists:
            artists_base.append(ArtistAdd(i[0]) if additional else Artist(i[0]))
            console.print(
                f"{INFO} The artist: {GREEN}{i[1]}{GREENEND}, "
                "his description, avatar were received"
            )
        print()

        return artists_base

    def get_album_name(self) -> str:
        """getting the name from the page from the album page"""

        # check_correct: list = re.search(r"<title>(\w+)", self.parse).groups()

        temp = re.findall(
            r"<span(?:\s+[^>]*)class=\"deco-typo\">(.+?[^<]*)",
            self.parse,
            re.M,
        )[0]

        return _fix_symbol(temp)[0]

    def get_type_link(self):
        """_su""" #TODO

        temp = re.findall(
            (
                r"<a(?:\s+[^>]*)href=\"/album/([\w]*)\"\s"
                r"class=\"d-link\sdeco-link\">(.+?[^<]*)"
            ),
            self.parse,
            re.M,
        )

        if _check_len(temp):
            return "track"

        return "album"

    def get_album_name_with_track(self) -> str:
        """getting the name from the track page

        the track may be incorrectly specified, but the album itself is correct,
        in this case, it will just find the album name"""

        temp = re.findall(
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

        console.print(
            f"{INFO} Your link is correct, but it contains a non-existent "
            "track, information about the album will be displayed"
        )
        print()

        return self.get_album_name()

    def get_length_tracks(self, track) -> str:
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

    def get_genre(self) -> list:
        """we get the genre of the track (album)"""

        return re.findall(
            (
                r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\s"
                r"deco-link_mimic\stypo\">(.+?[^<]*)"
            ),
            self.parse,
            re.M,
        )

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

    def get_similar_tracks(self) -> list | None:
        """returns a list of similar songs by track"""

        temp: str = re.findall(
            r"sidebar__section-title\stypo-caps\sdeco-typo-seco"
            r"ndary.+?class=\"footer\"",
            self.parse,
            re.M,
        )

        if temp:
            list_tracks: list = list(
                map(
                    lambda x: x.strip(),
                    re.findall(
                        r"d-track__title\sdeco-link\sdeco-link_stronger\">(.+?[^<]*)",
                        temp[0],
                        re.M,
                    ),
                )
            )

            return _fix_symbol(list_tracks)

        return None

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


class ArtistAdd(Artist):
    """advanced artist class"""

    def __init__(self, artist_code: str) -> str:
        super().__init__(artist_code)
        self.parse = Request(YANDEX_MUSIC_ARTIST + artist_code).parse_url()
        self.__popular_tracks = None
        self.__last_release = None
        self.__popular_album = None
        self.__playlists = None


    @property
    def popular_tracks(self) -> list:
        """return a list of the artist's popular tracks"""

        if not self.__popular_tracks:
            temp: list = re.findall(
                r"d-track__title\sdeco-link deco-link_stronger\">(.+?)<",
                self.parse,
                re.M,
            )
            return _fix_symbol(temp)

        return self.__popular_tracks

    @property
    def latest_release(self) -> str:
        """return the artist's latest release"""

        if not self.__last_release:
            temp: re.Match = re.search(
                r"page-artist__latest-album.+?album__caption\">(.+?)<",
                self.parse,
                re.M,
            )
            if temp:
                return _fix_symbol(temp.groups()[0])[0]

            return 'Not specified'

        return self.__last_release

    @property
    def popular_album(self) -> list:
        """return a list of popular artsit albums"""

        if not self.__popular_album:
            return _fix_symbol(
                re.findall(
                    r"album album_selectable.+?d-link\sdeco-link\salbum__caption\">(.+?[^<]*)",
                    self.parse,
                    re.M,
                )
            )

        return self.__popular_album

    @property
    def video_link(self):
        print(self.parse)
        exit()

    @property
    def playlists(self) -> list:
        """return playlists associated with the artist"""

        if not self.__playlists:
            return _fix_symbol(
                re.findall(
                    r"d-link deco-link playlist__title-link\">(.+?[^<]*)<",
                    self.parse,
                    re.M,
                )
            )

        return self.__playlists

    # def similar_artists(self):
    #     pass
