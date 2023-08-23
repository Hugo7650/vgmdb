from .utils import VGMdbObject, VGMdbType, Name, Link

from lxml import etree


class Artist(VGMdbObject):
    type: VGMdbType = VGMdbType.Artist
    aliases: list[str] | None
    role: str | None

    def __init__(self, id: int | str | None, name: str | Name | None = None) -> None:
        super().__init__(id if id else -1, name)

    @staticmethod
    def from_table(element: etree._Element) -> "Artist":
        link_element = element.xpath("./td/a")[0]
        link = Link.from_element(link_element)
        artist = Artist(link.id)
        artist.name = Name.from_element(link_element)
        if aliases := element.xpath("./td/span/text()"):
            artist.aliases = list(map(lambda x: x.strip(), aliases[0].split("/")))[1:]
        return artist

    @staticmethod
    def from_page(page) -> "Artist":
        return Artist(-1)  # TODO

    @staticmethod
    def from_element(element: etree._Element, role: str | None = None) -> "Artist":
        link = Link.from_element(element)
        artist = Artist(link.id)
        artist.name = Name.from_element(element)
        if role:
            artist.role = role
        return artist

    @staticmethod
    def from_mixed_td(td: etree._Element, role: str | None = None) -> list["Artist"]:
        raw_artists = "".join(td.xpath(".//text()")).split(",")
        raw_artists = list(
            map(lambda x: x.split("(")[0].split("/")[0].strip(), raw_artists)
        )
        artists = []
        for raw_artist in raw_artists:
            if element := td.xpath(f""".//a/span[text()={raw_artist!r}]/.."""):
                artists.append(Artist.from_element(element[0], role))
            else:
                artist = Artist(-1, raw_artist)
                artist.role = role
                artists.append(artist)
        return artists
