import re
from typing import List, NamedTuple

from re_parsing.simple_request import Request

# TODO
# ------------

# FIXME
# ------------

# UPDATED
# 2022-06-12
# non-existent links
# label
# not correct name song
# multiple performers*
# about performers*

# 2022-06-14|1:00AM
# extra requests on the performer
# multi labels

# 2022-06-14|7:30AM
# track time, as well as a fix of possible incorrect links for this

# MAYBE
# explicit ?
# similar tracks ?
# new albums of the genre ?
# albums of the user ?

class Artist(NamedTuple):
    """returns the data container"""

    links: list
    name: str
    avatar_about: dict

class ReParser:
    """returns does a search on the available pages"""

    __YANDEX_IMAGES: str = 'https://avatars.yandex.net/get-music-content/'
    YANDEX_MUSIC_ARTIST: str = 'https://music.yandex.ru/artist/'

    def __init__(self, url: str):
        self.url: str = url
        self.parse: str = Request(self.url).parse_url()

    @classmethod
    def check_len(cls, lst: list):
        """checking the length of the list"""
        if len(lst) != 0:
            return lst
        return None


    def get_img(self) -> str:
        """getting a list of link elements"""

        print('  \u21B3 YaMusic Wrapper - the request is successful! Expect') # decoration
        print('----------------------------------------------------') # decoration

        pat: list = (r"<img(?:\s+[^>]*)class=\"entity-cover__image\s"
               r"deco-pane\"(?:\s+[^>]*)src=([\"\'])(.+?)\1")

        temp: str = re.findall(pat, self.parse, re.M,)[0][1]
        return ReParser.get_full_size_image(temp)

    def get_track_name(self) -> str:
        """we get the name of the song"""

        check_correct: list = re.findall(r"<title>(\w+)", self.parse)
        if check_correct[0].lower() != 'яндекс':

            return re.findall(
                r"<a(?:\s+[^>]*)class=\"d-link\sdeco-link\">(.+?[^<]*)",
                self.parse, re.M,)[-1]

        return self.get_album_name()


    def get_artist(self) -> Artist:
        """we get (the performer, a link to him, a link to his avatar, his description)

        not all performers on the service have
        official avatars, some have requests from
        their search engine so I had to add a check"""

        print('\u21B3 Find out information about the performer') # decoration

        temp_artist_link_block: str = re.findall(
            r"<span\sclass=\"d-artists(.+?)</a></span>",
            self.parse, re.M,)[0]

        temp_artist_link_artists: list = re.findall(
            r"href=\"/artist/(\d+)\"\s+[^>]*>(.+?[^<]*)",
            temp_artist_link_block, re.M,)

        temp_artist_links: dict = {}
        if len(temp_artist_link_artists) > 1:
            for i in temp_artist_link_artists:
                get_artist_request = GetArtist(i[0])
                temp_artist_links[i[1]] = [
                    get_artist_request.artist_avatar(), get_artist_request.artist_about()]
                print(f'  \u21B3 Performers: {i[1]}, their description, avatars were received')
        else:
            get_artist_request = GetArtist(temp_artist_link_artists[0][0])
            temp_artist_links[temp_artist_link_artists[0][1]] = [
                get_artist_request.artist_avatar(), get_artist_request.artist_about()]
            print(f'  \u21B3 The performer: {temp_artist_link_artists[0][1]}, '
                  'his description, avatar were received')
        print('----------------------------------------------------') # decoration

        return (Artist(name = ', '.join(temp_artist_links).replace("&#39;", "'"),
                links = temp_artist_link_artists,
                avatar_about = temp_artist_links))

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
            self.parse, re.M,)

        if not self.check_len(temp) is None:
        # if len(temp) != 0:
            # if len(temp[0]) > 1:
            #     return temp[0][1]
            return temp[0][1]
            # return self.get_album_name()

        print('  \u21B3 Your link is correct, but it contains a non-existent track, '
              'information about the album will be displayed')

        return self.get_album_name()

    def get_tracktime(self, track) -> str:
        """return track time"""

        temp = re.findall(
            (fr"class=\"d-track__name\".+?[^<]*<a\shref=\"/album/{track}\""
             r".+?typo-track deco-typo-secondary\">(\w+[^<]*)"),
            self.parse, re.M,)

        if not self.check_len(temp) is None:
            return temp[0]

        return 'incorrect track id, album is shown'

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

    def get_label(self) -> str:
        """return label"""

        return ', '.join(re.findall(
            r"<a\shref=\"/label/\d+\"\sclass=\"d-link\sdeco-link\">(.+?[^<]*)",
            self.parse, re.M,))


    @classmethod
    def get_full_size_image(cls, sym_image: str) -> str:
        """ we get a link to the full size of the image"""

        return (
            cls.__YANDEX_IMAGES+sym_image
            .split(";")[-3][:-4]+'/'+sym_image
            .split(";")[-2][:-4]+'/m1000x1000')


class GetArtist(ReParser):
    """all info of artist"""

    def __init__(self, artist_code):
        super().__init__(self.YANDEX_MUSIC_ARTIST+artist_code+'/info')


    def artist_name(self):
        """return artist name"""

        return re.findall(
            r"<a(?:\s+[^>]*)class=\"d-link deco-link\"\stitle=\"(.+?[^\"]*)",
            self.parse, re.M,)

    def artist_avatar(self):
        """return artist avatar"""

        temp_artist_avatar: str = re.search(
            r"<img\ssrc=\"[^/blocks](.+?[^\"]*)",
            self.parse, re.M,).groups()[0]

        if re.search(r"\bw=\b",temp_artist_avatar):
            temp_artist_avatar_end: str = '&'
            for i in temp_artist_avatar.split(';'):
                temp_artist_avatar_end += i
            return ('https:'+temp_artist_avatar_end
                    .replace('&#47', '/')
                    .replace('&#38', '&'))

        return self.get_full_size_image(temp_artist_avatar)

    def artist_about(self):
        """return artist about"""

        temp_artist_about: List[str] = re.findall(
            r"<div\sclass=\"page-artist__description\stypo\">(.+?[^<]*)",
            self.parse, re.M,)

        if len(temp_artist_about) < 1:
            return 'There is no description'

        return temp_artist_about[0]
