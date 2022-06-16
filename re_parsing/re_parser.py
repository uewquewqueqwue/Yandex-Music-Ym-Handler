import re
from datetime import timedelta
from typing import NamedTuple

from re_parsing.simple_request import Request

# TODO
# ------------

# FIXME
# if the avatar does not exist, someone else's is taken

# UPDATED
# 2022-6-12
# non-existent links
# label
# not correct name song
# multiple performers*
# about performers*

# 2022-6-14|1:00AM
# extra requests on the performer
# multi labels

# 2022-6-14|7:30AM
# track length, as well as a fix of possible incorrect links for this

# 2022-6-15|3:00AM
# number of songs on the album

# 2022-6-15|6:30PM
# fixed the length of the track, as well as the author and
# the first song if the link to the compilation

# 2022-6-15|1:40AM
# now the list of artists is always returned

# 2022-6-16|10:10PM
# the length of the entire album(timedelta)
# links(list)

# 2022-6-16|01:05AM
# moved to a separate function, which means that it
# can be used everywhere separately from main

# Additional parameters(MAYBE)
# explicit ?timedelta
# similar tracks ?
# new albums of the genre ?
# albums of the user ?


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


def _check_len(lst: list) -> list | None:
    """checking the length of the list"""

    if len(lst) != 0:
        return lst
    return None


def _fix_symbol(item: list | str) -> list:
    """corrects the ' character in strings"""

    if isinstance(item, list):
        return list(map(lambda x: x.replace("&#39;", "'"), item))
    if isinstance(item, tuple):
        return list(map(lambda x: x.replace("&#39;", "'"), item))
    return [item.replace("&#39;", "'")]


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

    def get_img(self) -> str:
        """getting a list of link elements"""

        print(
            "  \u21B3 YaMusic-Link-Wrapper - the request is successful! Expect"
        )  # decoration
        print("----------------------------------------------------")  # decoration

        pat: list = (
            r"<img(?:\s+[^>]*)class=\"entity-cover__image\s"
            r"deco-pane\"(?:\s+[^>]*)src=([\"\'])(.+?)\1"
        )

        temp: str = re.findall(pat, self.parse, re.M,)[
            0
        ][1]
        return _full_size_image(temp)

    def get_track_name(self) -> str:
        """we get the name of the song"""

        check_correct: list = re.findall(r"<title>(\w+)", self.parse)
        if check_correct[0].lower() != "яндекс":

            temp = re.findall(
                r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\">(.+?[^<]*)",
                self.parse,
                re.M,
            )[-1]
            return _fix_symbol(temp)[0]

        return self.get_album_name()

    def get_artist(self) -> Artist:
        """we get (the performer, a link to him,
        a link to his avatar, his description)

        not all performers on the service have
        official avatars, some have requests from
        their search engine so I had to add a check"""

        print("\u21B3 Find out information about the performer")  # decoration

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
                    get_artist_request.artist_about(),
                ]
                print(
                    f" \u21B3 The performer: {i[1]}, "
                    "his description, avatar were received"
                )
            print("----------------------------------------------------")  # decoration
            return Artist(
                names=list(temp_artist_links.keys()),
                links=_default_links(temp_artist_link_artists),
                avatar_about=temp_artist_links,
            )
        if self.check_collection():
            print(
                "  \u21B3 This is a collection, it contains a lot of "
                "performers\n(in the future, it is possible for an additional "
                "the argument can get information about all performers)"
            )
            print("----------------------------------------------------")  # decoration
            return Artist(
                names=["A lot of artists, because this is a collection"],
                links=self.get_default_links(temp_artist_link_artists),
                avatar_about=None,
            )

        get_artist_request = GetArtist(temp_artist_link_artists[0][0])
        temp_artist_links[temp_artist_link_artists[0][1]] = [
            get_artist_request.artist_avatar(),
            get_artist_request.artist_about(),
        ]
        print(
            f"  \u21B3 The performer: {temp_artist_link_artists[0][1]}, "
            "his description, avatar were received"
        )
        print("----------------------------------------------------")  # decoration
        return Artist(
            names=[temp_artist_link_artists[0][1]],
            links=_default_links(temp_artist_link_artists),
            avatar_about=temp_artist_links,
        )

    def get_album_name(self) -> str:
        """getting the name from the page from the album page"""

        temp = re.findall(
            r"<span(?:\s+[^>]*)class=\"deco-typo\">(.+?[^<]*)",
            self.parse,
            re.M,
        )
        return _fix_symbol(temp)[0]

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

        if _check_len(temp) is not None:
            # if len(temp) != 0:
            # if len(temp[0]) > 1:
            #     return temp[0][1]
            return _fix_symbol(temp[0][1])[0]
            # return self.get_album_name()

        print(
            "  \u21B3 Your link is correct, but it contains a non-existent track, "
            "information about the album will be displayed"
        )

        return self.get_album_name()

    def get_tracktime(self, track) -> str:
        """return track time"""

        temp = re.findall(
            (
                rf"class=\"d-track__name\".+?[^<]*<a\shref=\"/album/{track}\""
                r".+?typo-track deco-typo-secondary\">(\w+[^<]*)"
            ),
            self.parse,
            re.M,
        )

        if _check_len(temp) is not None:
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

    def get_label(self) -> str:
        """return label"""

        return ", ".join(
            re.findall(
                r"<a\shref=\"/label/\d+\"\sclass=\"d-link\sdeco-link\">(.+?[^<]*)",
                self.parse,
                re.M,
            )
        )

    def get_numbers_song(self) -> int:
        """return number of songs in the album"""

        return len(
            re.findall(
                r"<div\sclass=\"d-track\stypo-track\sd-track_selectable",
                self.parse,
                re.M,
            )
        )

    def check_collection(self) -> bool:
        """checks whether this album is a compilation"""

        temp = re.findall(
            r"<span\sclass=\"deco-typo-secondary\s+\">(.+?)</",
            self.parse,
            re.M,
        )
        if not temp or temp[0] != "сборник":
            return False
        return True

    def length_all_tracks(self) -> list:
        """return the length of the entire album(timedelta)"""

        temp = re.findall(
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

    def artist_avatar(self) -> str:
        """return artist avatar"""

        temp_artist_avatar: str = re.search(
            r"<img\ssrc=\"[^/blocks](.+?[^\"]*)",
            self.parse,
            re.M,
        ).groups()[0]

        if re.search(r"\bw=\b", temp_artist_avatar):
            temp_artist_avatar_end: str = "&"
            for i in temp_artist_avatar.split(";"):
                temp_artist_avatar_end += i
            return "https:" + temp_artist_avatar_end.replace("&#47", "/").replace(
                "&#38", "&"
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
