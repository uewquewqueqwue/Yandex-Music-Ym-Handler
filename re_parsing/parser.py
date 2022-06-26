import re
from datetime import timedelta

from re_parsing.request import Request

# Consts

YM = " https://music.yandex.com/"
YM_ARTIST = "https://music.yandex.com/artist/"
YM_ALBUM = "https://music.yandex.com/album/"
YM_IMAGES = "https://avatars.yandex.net/get-music-content/"
EXAMPLE_LINKS = (
    "https://music.yandex.com/album/123123",
    "https://music.yandex.com/album/123123/track/123123",
)

# Utilitarian functions


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
        return_list.extend([YM_ARTIST + i[0]])

    return return_list


def _full_size_image(sym_image: str) -> str:
    """we get a link to the full size of the image"""

    return (
        YM_IMAGES
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


def _fix_symbol(item: str | tuple | list) -> list:
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
            done_str = item.strip().replace(i, j)

        return [done_str]

    for i, j in symbol_case.items():
        done_str = list(map(lambda a: a.strip().replace(i, j), done_str))

    return done_str


# Album class
# to -> search - DONE


class Album:
    """_summary_"""

    def __init__(self, parse: str) -> None:
        self.__parse = parse

    @property
    def name(self) -> str:
        """getting the name from the page from the album page"""

        return _fix_symbol(
            re.search(
                r"<span(?:\s+[^>]*)class=\"deco-typo\">(.+?[^<]*)",
                self.__parse,
                re.M,
            ).groups()
        )[0]

    @property
    def number_songs(self) -> int:
        """return number of songs in the album"""

        return len(
            re.findall(
                r"<div\sclass=\"d-track\stypo-track\sd-track_selectable",
                self.__parse,
                re.M,
            )
        )

    @property
    def length(self) -> timedelta:
        """return the length of the entire album(timedelta)"""

        return _convert_to_timedelta(
            re.findall(
                r"<div\sclass=\"d-track\stypo-track\sd-track_selecta"
                r"ble.+?typo-track\sdeco-typo-secondary\">(\w+[^<]*)",
                self.__parse,
                re.M,
            )
        )


# Track class
# to -> search - DONE


class Track:
    """_summary_"""

    def __init__(self, parse: str, track_id: str) -> None:
        self.__parse = self.check_id(parse)
        self.__track_id = track_id
        self.__name = None
        self.__length = None
        # self.__length = None

    @classmethod
    def check_id(cls, parse: str) -> str:
        """_summary_"""

        check_correct = re.search(r"<title>(\w+)", parse).groups()
        check_correct_ = re.search(
            r"class=\"d-link\sdeco-link\".+?>(\w+)", parse
        ).groups()
        if (
            check_correct[0].lower() not in ["яндекс", "yandex"]
            and check_correct[0] != check_correct_[0]
        ):
            return parse

        raise TypeError("Нет такого ид")

    @property
    def name(self) -> str:
        """_summ"""

        if not self.__name:
            return _fix_symbol(
                re.search(
                    r"sidebar__title\ssidebar-track__title\sdeco-type\sty"
                    r"po-h2\".+?d-link\sdeco-link\">(.+?[^<]*)",
                    self.__parse,
                    re.M,
                ).groups()
            )[0]

        return self.__name

    @property
    def length(self) -> timedelta:
        """_sum"""

        if not self.__length:
            return _convert_to_timedelta(
                [
                    re.search(
                        (
                            rf"class=\"d-track__name\".+?<a\shref=\"/album/{self.__track_id}\""
                            r".+?typo-track\sdeco-typo-secondary\">(\w+[^<]*)"
                        ),
                        self.__parse,
                        re.M,
                    ).groups()[0]
                ]
            )

        return self.__length

    @property
    def similar_tracks(self):
        """_s"""

        temp = re.search(
            r"sidebar__section-title\stypo-caps\sdeco-typo-seco"
            r"ndary.+?class=\"footer\"",
            self.__parse,
            re.M,
        )

        return _fix_symbol(
            list(
                map(
                    lambda x: x.strip(),
                    re.findall(
                        r"d-track__title\sdeco-link\sdeco-link_stronger\">(.+?[^<]*)",
                        temp[0],
                        re.M,
                    ),
                )
            )
        )


class Artist:
    """_s"""

    def __init__(self, artist_code: str) -> None:
        print("artist")
        self.__parse = Request(YM_ARTIST + artist_code + "/info").parse_url()
        self.__name = None
        self.__avatar = None
        self.__about = None
        self.__likes_month = None
        self.__listeners_month = None

    # def __getattr__(self, item):
    #     if item in ArtistAdd.__dict__:
    #         raise AttributeError("These attributes are not in Artist, use ArtistAdd")

    @property
    def name(self) -> str:
        """return artist name"""

        if not self.__name:
            self.__name = re.search(
                r"<h1.+?>(\w+)<",
                self.__parse,
                re.M,
            ).groups()[0]

        return self.__name

    @property
    def avatar(self) -> str:
        """return artist avatar"""

        if not self.__avatar:
            if re.findall(r"artist-pics__pic\sartist-pics__pic_empty", self.__parse):
                return self.__avatar

            temp_artist_avatar = re.search(
                r"<img\ssrc=\"(.+?[^\"]*)",
                self.__parse,
                re.M,
            ).groups()[0]

            if re.search(r"\bw=\b", temp_artist_avatar):
                temp_artist_avatar_end = "".join(temp_artist_avatar.split(";"))
                return "https:" + temp_artist_avatar_end.replace(
                    "&#47", "\u002F"
                ).replace("&#38", "\u0026")

            return _full_size_image(temp_artist_avatar)

        return self.__avatar

    @property
    def about(self) -> str | None:
        """return artist about"""

        if not self.__about:
            temp_artist_about: list[str] = re.findall(
                r"<div\sclass=\"page-artist__description\stypo\">(.+?[^<]*)",
                self.__parse,
                re.M,
            )

            if temp_artist_about:
                return _fix_symbol(temp_artist_about)[0]

        return self.__about

    @property
    def likes_month(self) -> int:
        """_su"""

        if not self.__likes_month:
            return int(re.search(
                r"page-section__title\stypo typo-medium.+?\"(?:Лай|Lik).+?total-count\">(\w+[^<]*)",
                self.__parse,
                re.M,
            ).groups()[0])

        return self.__likes_month

    @property
    def listeners_month(self) -> int:
        """_su"""

        if not self.__listeners_month:
            return int(re.search(
                r"page-section__title\stypo typo-medium.+?\"(?:Слу|Lis).+?total-count\">(\w+[^<]*)",
                self.__parse,
                re.M,
            ).groups()[0])

        return self.__listeners_month


class ArtistDetails(Artist):
    """advanced artist class"""

    def __init__(self, artist_code: str) -> str:
        super().__init__(artist_code)
        print("artist-details")
        self.__parse = Request(YM_ARTIST + artist_code).parse_url()
        self.__popular_tracks = None
        self.__last_release = None
        self.__popular_album = None
        self.__playlists = None
        self.__video_names = None
        self.__similar_artists = None

    @property
    def popular_tracks(self) -> list:
        """return a list of the artist's popular tracks"""

        if not self.__popular_tracks:
            temp: list = re.findall(
                r"d-track__title\sdeco-link\sdeco-link_stronger\">(.+?[^<]*)",
                self.__parse,
                re.M,
            )
            return _fix_symbol(temp)

        return self.__popular_tracks

    @property
    def latest_release(self) -> str | None:
        """return the artist's latest release"""

        if not self.__last_release:
            temp: re.Match = re.search(
                r"page-artist__latest-album.+?album__caption\">(.+?[^<]*)",
                self.__parse,
                re.M,
            )

            if temp:
                return _fix_symbol(temp.groups()[0])[0]

        return self.__last_release

    @property
    def popular_albums(self) -> list:
        """return a list of popular artsit albums"""

        if not self.__popular_album:
            return _fix_symbol(
                re.findall(
                    r"album\salbum_selectable.+?d-link\sdeco-link\salbum__caption\">(.+?[^<]*)",
                    self.__parse,
                    re.M,
                )
            )

        return self.__popular_album

    @property
    def video_names(self):
        """_su"""

        if not self.__video_names:
            return re.findall(
                r"video-list__item\".+?d-link\sdeco-link\">(.+?[^<]*)",
                self.__parse,
                re.M,
            )

        return self.__video_names

    @property
    def playlists(self) -> list:
        """return playlists associated with the artist"""

        if not self.__playlists:
            return _fix_symbol(
                re.findall(
                    r"d-link\sdeco-link\splaylist__title-link\">(.+?[^<]*)",
                    self.__parse,
                    re.M,
                )
            )

        return self.__playlists

    @property
    def similar_artists(self) -> list | None:
        """_s"""

        if not self.__similar_artists:
            temp = re.findall(
                r"data-card=\"similar_artists\".+?sidebar__placeholder",
                self.__parse,
                re.M,
            )[0]

            if temp:
                return _fix_symbol(
                    re.findall(
                        r"artist__name.+?title=\"(.+?[^\"]*)",
                        temp,
                        re.M,
                    )
                )

            return None

        return self.__similar_artists


# Static class


class Static:
    """_s"""

    def __init__(self, url: str) -> None:
        self.__parse = self.analysis(url)
        self.__genre = None
        self.__date = None
        self.__labels = None
        self.__cover = None

    def analysis(self, url: str) -> str | None:
        """_s"""

        pat = (
            r"https:\/\/music[.]yandex[.](?:com|ru)\/album\/((?P<track>[\d]+\/tra"
            r"ck\/[\d]+)|(?P<album>[\d]+))"
        )
        match = re.search(
            pat,
            url,
            re.M,
        )

        if match:
            answer = match.groupdict()
            if answer.get("album"):
                self.type_url = "album"
            else:
                self.type_url = "track"
                self.__track_id = answer.get("track")
            print("url")
            return Request(match.group()).parse_url()

        raise TypeError("Неправильная ссылка")

    def check_collection(self) -> bool:
        """checks whether this album is a compilation"""

        temp = re.findall(
            r"<span\sclass=\"deco-typo-secondary\s+\">(.+?[^<]*)",
            self.__parse,
            re.M,
        )
        temp_ = re.search(
            r"sidebar__section sidebar__section_albums",
            self.__parse,
            re.M,
        )

        if temp_ or not temp or temp[0].lower() not in ["сборник", "various artists"]:
            return False

        return True

    @property
    def album(self) -> Album:
        """_su"""

        return Album(self.__parse)

    @property
    def track(self) -> Track:
        """_st"""

        return Track(self.__parse, self.__track_id)

    def artists(
        self, details: bool = False, creativity: bool = False
    ) -> Artist | ArtistDetails:
        """we get (the artist, a link to him,
        a link to his avatar, his description)"""

        temp_artist_link_block: str = re.findall(
            r"<span\sclass=\"d-artists(.+?)</a></span>",
            self.__parse,
            re.M,
        )[0]

        temp_artist_link_artists: list = re.findall(
            r"href=\"/artist/(\d+)\"\s+[^>]*>(.+?[^<]*)",
            temp_artist_link_block,
            re.M,
        )

        temp_artist_link_artists = list(map(_fix_symbol, temp_artist_link_artists))

        if self.check_collection():
            return []

        artists_base = []
        for i in temp_artist_link_artists:
            if details and creativity:
                pass
            elif details:
                artists_base.append(ArtistDetails(i[0]))
            elif creativity:
                pass
            else:
                artists_base.append(Artist(i[0]))

        return artists_base

    @property
    def genre(self) -> tuple | None:
        """we get the genre of the track (album)"""

        if not self.__genre:
            temp = re.search(
                (
                    r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\s"
                    r"deco-link_mimic\stypo\">(.+?[^<]*)"
                ),
                self.__parse,
                re.M,
            )

            if temp:
                return temp.groups()

        return self.__genre

    @property
    def date(self) -> str | None:
        """we get the date of the track (album)"""

        if not self.__date:
            temp = re.search(
                r"<span\s+class=\"typo\sdeco-typo-secondary\">(.+?[^<]*)",
                self.__parse,
                re.M,
            )

            if temp:
                return temp.groups()[0]

        return self.__date

    @property
    def labels(self) -> list | None:
        """we get labels of the track (album)"""

        if not self.__labels:
            temp = _fix_symbol(
                re.findall(
                    r"<a\shref=\"/label/\d+\"\sclass=\"d-link\sdeco-link\">(.+?[^<]*)",
                    self.__parse,
                    re.M,
                )
            )

            if temp:
                return temp

        return self.__labels

    @property
    def cover(self) -> str | None:
        """we get the cover url of the track (album)"""

        if not self.__cover:
            check_cover = re.search(
                r"entity-cover__image\sentity-cover__image_no-cover",
                self.__parse,
                re.M,
            )

            if check_cover:
                return self.__cover

            return _full_size_image(
                re.search(
                    (
                        r"<img(?:\s+[^>]*)class=\"entity-cover__image\sde"
                        r"co-pane\"(?:\s+[^>]*)src=\"(.+?)\""
                    ),
                    self.__parse,
                    re.M,
                ).groups()[0]
            )

        return self.__cover
