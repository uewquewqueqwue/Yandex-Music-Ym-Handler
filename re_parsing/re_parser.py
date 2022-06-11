import re
from typing import List, NamedTuple

from re_parsing.simple_request import Request

# TODO
# multiple performers*
# about performers*

# explicit ?
# label
# similar tracks ?
# new albums of the genre ?
# albums of the user ?

# search down from the link class="d-track__name" before class="d-track__end"
# below it is a link с href="/album/12189572/track/71495455"

class Artist(NamedTuple):
    """returns the data container"""
    
    link: str
    name: str
    avatar: str
    about: str

class ReParser:
    """returns does a search on the available pages"""

    YANDEX_IMAGES: str = 'https://avatars.yandex.net/get-music-content/'
    YANDEX_MUSIC_ARTIST: str = 'https://music.yandex.ru/artist/'

    def __init__(self, url: str):
        self.url: str = url
        self.parse: str = Request(self.url).parse_url()

        print('  \u21B3 YaMusic Wrapper - the request is successful! Expect') # decoration
        print('----------------------------------------------------') # decoration

    def get_img(self) -> str:
        """getting a list of link elements"""

        pat = (r"<img(?:\s+[^>]*)class=\"entity-cover__image "
               r"deco-pane\"(?:\s+[^>]*)src=([\"\'])(.+?)\1")
        temp = re.findall(pat, self.parse, re.M,)[0][1]
        return ReParser.get_full_size_image(temp)

    def get_track_name(self) -> str:
        """we get the name of the song"""

        return re.findall(
            r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\">(.+?[^<]*)",
            self.parse, re.M,)[-1]

    def get_artist(self) -> Artist:
        """we get (the performer, a link to him, a link to his avatar, his description)

        not all performers on the service have
        official avatars, some have requests from
        their search engine so I had to add a check"""

        temp_artist_link: str = re.findall(
            r"<a\s+href=\"/artist/(.+?)\"\sclass=\"d-link deco-link\"",
            self.parse, re.M,)[0]

        temp_artist_name: str = re.findall(
            r"<a(?:\s+[^>]*)class=\"d-link deco-link\"\stitle=\"(.+?[^\"]*)",
            self.parse, re.M,)[0]

        temp_artist_request: str = Request(
            self.YANDEX_MUSIC_ARTIST+temp_artist_link+'/info').parse_url()

        temp_artist_avatar: str = re.search(
            r"<img\ssrc=\"[^/blocks](.+?[^\"]*)",
            temp_artist_request, re.M,).groups()[0]

        if re.search(r"\bw=\b",temp_artist_avatar):
            temp_artist_avatar_end: str = '&'
            for i in temp_artist_avatar.split(';'):
                temp_artist_avatar_end += i
            temp_artist_avatar: str = ('https:'+temp_artist_avatar_end
                                       .replace('&#47', '/')
                                       .replace('&#38', '&'))
        else:
            temp_artist_avatar: str = self.get_full_size_image(temp_artist_avatar)

        temp_artist_about: List[str] = re.findall(
            r"<div\sclass=\"page-artist__description\stypo\">(.+?[^<]*)",
            temp_artist_request, re.M,)

        if len(temp_artist_about) < 1:
            temp_artist_about_end: str = 'There is no description'
        else:
            temp_artist_about_end: str = temp_artist_about[0]

        return (Artist(name = temp_artist_name.replace("&#39;", "'"),
                link = self.YANDEX_MUSIC_ARTIST+temp_artist_link+'/info',
                avatar = temp_artist_avatar,
                about = temp_artist_about_end))

    def get_album_name(self) -> str:
        """getting the name from the page from the album page"""

        return re.findall(
            r"<span(?:\s+[^>]*)class=\"deco-typo\">(.+?[^<]*)",
            self.parse, re.M,)[0]

    def get_album_name_with_track(self) -> str:
        """getting the name from the track page

        the track may be incorrectly specified, but the album itself is correct,
        in this case, it will just find the album name"""

        temp = re.findall(
            r"<a(?:\s+[^>]*)href=\"/album/([\w]*)\"\sclass=\"d-link\sdeco-link\">(.+?[^<]*)",
            self.parse, re.M,)[0]

        if len(temp) > 1:
            return temp[1]

        return self.get_album_name()

    def get_genre(self) -> str:
        """we get the genre of the track (album)"""

        return re.findall(
            r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\sdeco-link_mimic\stypo\">(.+?[^<]*)",
            self.parse, re.M,)[0]

    def get_date(self) -> str:
        """we get the date of the track (album)"""

        return re.findall(
            r"<span\s+class=\"typo deco-typo-secondary\">(.+?[^<]*)",
            self.parse, re.M,)[0]


    @classmethod
    def get_full_size_image(cls, sym_image: str) -> str:
        """ we get a link to the full size of the image"""

        return (
            cls.YANDEX_IMAGES+sym_image
            .split(";")[-3][:-4]+'/'+sym_image
            .split(";")[-2][:-4]+'/m1000x1000')
